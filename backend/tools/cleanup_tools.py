from pathlib import Path
from backend.core.config import PROJECT_ROOT

ALLOWED_CLEANUP_DIRS = [
    PROJECT_ROOT / "data" / "state"
]

def cleanup_test_file(path: str):
    target = (PROJECT_ROOT / path).resolve()

    allowed = any(
        str(target).startswith(str(directory.resolve()))
        for directory in ALLOWED_CLEANUP_DIRS
    )

    if not allowed:
        return "Cleanup blocked: path is not an allowed cleanup directory."

    if not target.exists():
        return "File does not exist."

    if not target.is_file():
        return "Cleanup blocked: path is not a file."

    target.unlink()

    return f"Deleted file: {path}"