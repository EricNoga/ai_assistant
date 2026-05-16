import json
import uuid
from pathlib import Path
from datetime import datetime


STATE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "state"
RUNS_FILE = STATE_DIR / "runs.json"

STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_runs():
    if not RUNS_FILE.exists():
        return {}

    try:
        return json.loads(RUNS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_runs(runs: dict):
    RUNS_FILE.write_text(
        json.dumps(runs, indent=2),
        encoding="utf-8"
    )


runs = _load_runs()


def create_run(user_message: str, selected_agents: list):
    run_id = str(uuid.uuid4())

    runs[run_id] = {
        "id": run_id,
        "user_message": user_message,
        "selected_agents": selected_agents,
        "task_ids": [],
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "final_response": None
    }

    _save_runs(runs)

    return run_id


def add_task_to_run(run_id: str, task_id: str):
    if run_id in runs:
        runs[run_id]["task_ids"].append(task_id)

        _save_runs(runs)


def complete_run(run_id: str, final_response: str):
    if run_id in runs:
        runs[run_id]["status"] = "completed"
        runs[run_id]["completed_at"] = datetime.now().isoformat()
        runs[run_id]["final_response"] = final_response

        _save_runs(runs)


def fail_run(run_id: str, error: str):
    if run_id in runs:
        runs[run_id]["status"] = "failed"
        runs[run_id]["completed_at"] = datetime.now().isoformat()
        runs[run_id]["final_response"] = error

        _save_runs(runs)


def get_run(run_id: str):
    return runs.get(run_id)


def list_runs():
    return list(runs.values())