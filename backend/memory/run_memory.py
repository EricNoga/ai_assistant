import uuid
from datetime import datetime


runs = {}


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

    return run_id


def add_task_to_run(run_id: str, task_id: str):
    if run_id in runs:
        runs[run_id]["task_ids"].append(task_id)


def complete_run(run_id: str, final_response: str):
    if run_id in runs:
        runs[run_id]["status"] = "completed"
        runs[run_id]["completed_at"] = datetime.now().isoformat()
        runs[run_id]["final_response"] = final_response


def fail_run(run_id: str, error: str):
    if run_id in runs:
        runs[run_id]["status"] = "failed"
        runs[run_id]["completed_at"] = datetime.now().isoformat()
        runs[run_id]["final_response"] = error


def get_run(run_id: str):
    return runs.get(run_id)


def list_runs():
    return list(runs.values())