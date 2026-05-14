import uuid

#In-memory task store (we'll upgrade to database later)
tasks ={}

def create_task(description: str):
    task_id = str(uuid.uuid4())

    tasks[task_id] = {
        "id": task_id,
        "description": description,
        "status": "pending",
        "result": None
    }

    return task_id

def update_task(task_id: str, status: str, result: str = None):
    if task_id in tasks:
        tasks[task_id]["status"] = status
        tasks[task_id]["result"] = result

def get_task(task_id: str):
    return tasks.get(task_id)

def list_tasks():
    return list(tasks.values())