import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from extractor import extract_patches
from reviewer import review_all
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Setup MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["git_review_db"]
ai_reviews_collection = db["ai_reviews"]

COLLECTIONS = {
    "gitlab": db["git_lab_merge_request"],
    "github": db["git_hub_pull_request"]
}

@app.route("/review", methods=["POST"])
def review_handler():
    req_data = request.get_json()

    if not req_data or "source" not in req_data or "id" not in req_data:
        return jsonify({"error": "Invalid request. Must contain 'source' and 'id'."}), 400

    source = req_data["source"]
    pr_id = req_data["id"]

    if source not in COLLECTIONS:
        return jsonify({"error": "Source must be 'github' or 'gitlab'."}), 400

    try:
        object_id = ObjectId(pr_id)
        record = COLLECTIONS[source].find_one({"_id": object_id})
    except Exception as e:
        return jsonify({"error": f"Invalid ObjectId format: {e}"}), 400

    if not record:
        return jsonify({"error": "Record not found."}), 404

    # Check if this PR has already been reviewed
    existing_review = ai_reviews_collection.find_one({"source": source, "pr_id": object_id})
    if existing_review:
        return jsonify({
            "status": "already_reviewed",
            "message": "This pull/merge request has already been reviewed.",
            "reviews": existing_review["reviews"]
        }), 200

    patches = extract_patches(record, source)
    if not patches:
        return jsonify({"error": "No valid patches found."}), 400

    reviews = review_all(patches)

    ai_reviews_collection.insert_one({
        "source": source,
        "pr_id": object_id,
        "created_at": datetime.utcnow(),
        "reviews": reviews
    })

    return jsonify({"status": "success", "reviews": reviews}), 200


@app.route("/reviews", methods=["GET"])
def get_reviews():
    source = request.args.get("source")
    pr_id = request.args.get("id")

    if not source or not pr_id:
        return jsonify({"error": "Missing 'source' or 'id' query parameter."}), 400

    if source not in COLLECTIONS:
        return jsonify({"error": "Source must be 'github' or 'gitlab'."}), 400

    try:
        object_id = ObjectId(pr_id)
    except Exception as e:
        return jsonify({"error": f"Invalid ObjectId format: {e}"}), 400

    reviews_doc = ai_reviews_collection.find_one({"source": source, "pr_id": object_id})
    if not reviews_doc:
        return jsonify({"status": "not_found", "message": "No review found for this PR."}), 404

    return jsonify({
        "status": "success",
        "reviews": reviews_doc["reviews"],
        "created_at": reviews_doc["created_at"]
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5002)
