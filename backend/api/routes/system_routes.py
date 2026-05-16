from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.config import (
    DEFAULT_MODEL,
    MAX_AGENT_STEPS,
    OPENAI_API_KEY
)
from backend.core.health import check_health
from backend.core.bootstrap import bootstrap_project

from backend.memory.chat_memory import get_history, clear_history
from backend.memory.task_memory import list_tasks
from backend.memory.vector_memory import search_memory, get_all_memories
from backend.memory.run_memory import list_runs, get_run
from backend.tools.registry import get_tool_names


router = APIRouter(
    tags=["System"]
)


class MemorySearchRequest(BaseModel):
    query: str
    n_results: int = 3


@router.get("/")
async def root():
    return {
        "message": "AI Assistant Backend Running"
    }


@router.get("/history")
async def history():
    return {
        "history": get_history()
    }


@router.post("/history/clear")
async def clear_chat_history():
    clear_history()

    return {
        "message": "Chat history cleared"
    }


@router.get("/tasks")
async def tasks():
    return {
        "tasks": list_tasks()
    }


@router.get("/runs")
async def runs():
    return {
        "runs": list_runs()
    }


@router.get("/runs/{run_id}")
async def run_detail(run_id: str):
    return {
        "run": get_run(run_id)
    }


@router.post("/memory/search")
async def memory_search(request: MemorySearchRequest):
    results = search_memory(
        request.query,
        request.n_results
    )

    return {
        "results": results
    }


@router.get("/memory/all")
async def memory_all():
    return {
        "memory": get_all_memories()
    }


@router.get("/status")
async def status():
    return {
        "status": "running",
        "model": DEFAULT_MODEL,
        "max_agent_steps": MAX_AGENT_STEPS,
        "openai_api_key_loaded": bool(OPENAI_API_KEY),
        "available_tools": get_tool_names()
    }


@router.get("/health")
async def health():
    return check_health()


@router.post("/bootstrap")
async def bootstrap():
    folders = bootstrap_project()

    return {
        "message": "Bootstrap completed",
        "folders": folders
    }