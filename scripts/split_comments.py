import json
import os

# === CONFIG ===
SOURCE_FILE = "../data/mined-comments-25stars-25prs-Go.json"
OUTPUT_DIR = "../data/split"
CHUNK_SIZE = 50000

# === Ensure output directory exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Load all comments from the giant JSON ===
with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

all_comments = []
for repo, comments in raw_data.items():
    for comment in comments:
        comment["repo"] = repo  # keep repo info in each comment
        all_comments.append(comment)

print(f"[INFO] Total comments loaded: {len(all_comments)}")

# === Split into chunks ===
for i in range(0, len(all_comments), CHUNK_SIZE):
    chunk = all_comments[i:i+CHUNK_SIZE]
    chunk_num = i // CHUNK_SIZE + 1
    output_file = os.path.join(OUTPUT_DIR, f"chunk_{chunk_num:02d}.json")
    
    with open(output_file, "w", encoding="utf-8") as f_out:
        json.dump(chunk, f_out, indent=2, ensure_ascii=False)
    
    print(f"[INFO] Saved chunk {chunk_num} ({len(chunk)} comments) to {output_file}")

print("[DONE] All chunks generated.")
