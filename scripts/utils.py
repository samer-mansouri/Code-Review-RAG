import json

def stream_rag_docs(json_path: str, limit: int = None):
    """
    Streams PR comments from the large JSON file for RAG indexing.
    """
    count = 0
    with open(json_path, "r", encoding="utf-8") as f:
        # Load top-level JSON (all repos)
        raw = json.load(f)

        for repo, comments in raw.items():
            for comment in comments:
                body = comment.get("body", "")
                diff = comment.get("diff_hunk", "")
                path = comment.get("path", "")
                text = f"[{repo} | {path}]\n\nDiff:\n{diff}\n\nComment:\n{body}"

                yield text
                count += 1
                if limit and count >= limit:
                    return
