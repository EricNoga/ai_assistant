from fastapi import APIRouter

from backend.memory.task_memory import list_tasks


router = APIRouter(
    tags=["Tasks"]
)


@router.get("/tasks")
async def tasks():
    return {
        "tasks": list_tasks()
    }