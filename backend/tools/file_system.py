import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def read_file(path: str):
    """Read a file from the project safely"""

    full_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(full_path):
        return "File not found."

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str):
    """Write content to a file safely"""

    full_path = os.path.join(BASE_DIR, path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"File written: {path}"

def list_files(path: str = "."):
    """List files in directory"""

    full_path = os.path.join(BASE_DIR, path)

    if not os.path.exists(full_path):
        return "Directory not found."

    return os.listdir(full_path)