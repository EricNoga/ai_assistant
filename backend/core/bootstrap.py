from pathlib import Path

from backend.core.config import PROJECT_ROOT

REQUIRED_FOLDERS = [
    "data",
    "data/state",
    "data/media",
    "data/media/projects",
    "data/security",
    "data/security/reports",
    "backend/memory_db"
]

def bootstrap_project():
    created_or_verified = []

    for folder in REQUIRED_FOLDERS:
        path = Path(PROJECT_ROOT) / folder
        path.mkdir(parents=True, exist_ok=True)
        created_or_verified.append(str(path))

    return created_or_verified