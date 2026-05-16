import json
import uuid
from pathlib import Path


STATE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "state"
TASKS_FILE = STATE_DIR / "tasks.json"

STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_tasks():
    if not TASKS_FILE.exists():
        return {}

    try:
        return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_tasks(tasks: dict):
    TASKS_FILE.write_text(
        json.dumps(tasks, indent=2),
        encoding="utf-8"
    )


tasks = _load_tasks()


def create_task(description: str):
    task_id = str(uuid.uuid4())

    tasks[task_id] = {
        "id": task_id,
        "description": description,
        "status": "pending",
        "result": None
    }

    _save_tasks(tasks)

    return task_id


def update_task(task_id: str, status: str, result: str = None):
    if task_id in tasks:
        tasks[task_id]["status"] = status
        tasks[task_id]["result"] = result

        _save_tasks(tasks)


def get_task(task_id: str):
    return tasks.get(task_id)


def list_tasks():
    return list(tasks.values())