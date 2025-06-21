from scripts.review_patch import review_patch_with_rag

def review_all(patches):
    results = []
    for item in patches:
        try:
            review = review_patch_with_rag(item["patch"])
            results.append({
                "file": item["file"],
                "review": review
            })
        except Exception as e:
            results.append({
                "file": item["file"],
                "error": str(e)
            })
    return results
