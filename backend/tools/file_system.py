from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _safe_path(path: str) -> Path:
    target = (BASE_DIR / path).resolve()

    if not str(target).startswith(str(BASE_DIR)):
        raise ValueError("Access denied: path is outside project directory.")

    return target


def read_file(path: str):
    target = _safe_path(path)

    if not target.exists():
        return "File not found."

    if not target.is_file():
        return "Path is not a file."

    return target.read_text(encoding="utf-8")


def write_file(path: str, content: str):
    target = _safe_path(path)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content or "", encoding="utf-8")

    return f"File written: {path}"


def list_files(path: str = "."):
    target = _safe_path(path)

    if not target.exists():
        return "Directory not found."

    if not target.is_dir():
        return "Path is not a directory."

    return [item.name for item in target.iterdir()]