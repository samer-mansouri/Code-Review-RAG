from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils import stream_rag_docs
import os

CHUNK_SIZE = 250
MAX_DOCS = 250000
JSON_PATH = "../data/mined-comments-25stars-25prs-Go.json"
INDEX_PATH = "../index/qwen_rag_index"

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def build_index():
    print("[INFO] Streaming and indexing documents...")
    docs = []
    total = 0
    index = None

    for doc in stream_rag_docs(JSON_PATH, limit=MAX_DOCS):
        docs.append(doc)
        if len(docs) >= CHUNK_SIZE:
            print(f"[INFO] Embedding chunk {total}-{total+len(docs)}")
            if index is None:
                index = FAISS.from_texts(docs, embedding=embedding)
            else:
                index.add_texts(docs)
            total += len(docs)
            docs = []

    if docs:
        print(f"[INFO] Final chunk {total}-{total+len(docs)}")
        if index is None:
            index = FAISS.from_texts(docs, embedding=embedding)
        else:
            index.add_texts(docs)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    index.save_local(INDEX_PATH)
    print(f"[DONE] Vector index saved to {INDEX_PATH}")

if __name__ == "__main__":
    build_index()
