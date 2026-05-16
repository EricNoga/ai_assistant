from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FOLDERS = [
    "data",
    "data/state",
    "data/media",
    "data/media/projects",
    "data/security",
    "data/security/reports",
    "backend/memory_db"
]

def bootstrap_project():
    for folder in FOLDERS:
        path = PROJECT_ROOT / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created/verified: {path}")

if __name__ == "__main__":
    bootstrap_project()