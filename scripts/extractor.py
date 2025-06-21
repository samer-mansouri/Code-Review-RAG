def extract_patches(data: dict, source: str):
    patches = []

    def is_binary_diff(patch: str) -> bool:
        # You can expand this detection if needed
        return (
            "Binary files" in patch or
            patch.strip() == "" or
            patch.strip().startswith("Binary")
        )

    if source == "gitlab":
        for diff in data.get("diffs", []):
            patch_content = diff.get("diff", "")
            if patch_content and not is_binary_diff(patch_content):
                patches.append({
                    "file": diff.get("new_path", "unknown"),
                    "patch": patch_content
                })

    elif source == "github":
        for commit in data.get("commits", []):
            for file in commit.get("files", []):
                patch_content = file.get("patch")
                if patch_content and not is_binary_diff(patch_content):
                    patches.append({
                        "file": file.get("filename", "unknown"),
                        "patch": patch_content
                    })

    return patches
