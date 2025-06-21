import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

CHUNK_DIR = "../data/split"
INDEX_PATH = "../index/qwen_rag_index"
CHUNK_SIZE = 5000

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_documents_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    docs = [
        Document(
            page_content=item["body"],
            metadata={
                "repo": item["repo"],
                "path": item.get("path"),
                "line": item.get("line"),
                "user": item.get("user"),
                "url": item.get("html_url")
            }
        )
        for item in items if item.get("body")
    ]
    return docs

def build_index():
    print("[INFO] Building index from chunks...")
    all_files = sorted(f for f in os.listdir(CHUNK_DIR) if f.endswith(".json"))
    index = None
    total_docs = 0

    for file in all_files:
        path = os.path.join(CHUNK_DIR, file)
        docs = load_documents_from_file(path)

        print(f"[INFO] Processing {file} ({len(docs)} docs)")

        for i in range(0, len(docs), CHUNK_SIZE):
            batch = docs[i:i+CHUNK_SIZE]
            texts = [d.page_content for d in batch]
            metadatas = [d.metadata for d in batch]

            if index is None:
                index = FAISS.from_texts(texts, embedding=embedding, metadatas=metadatas)
            else:
                index.add_texts(texts, metadatas)

            total_docs += len(batch)

            # Save index progressively
            os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
            index.save_local(INDEX_PATH)
            print(f"[✅] Saved index after {total_docs} documents")

    print(f"[✔️ DONE] Total embedded: {total_docs}")
    print(f"[📦] Final index saved to: {INDEX_PATH}")

if __name__ == "__main__":
    build_index()
