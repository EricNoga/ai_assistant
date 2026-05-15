from fastapi import FastAPI
from pydantic import BaseModel

from backend.models.openai_client import get_ai_response
from backend.memory.chat_memory import get_history, clear_history
from backend.memory.task_memory import list_tasks
from backend.memory.vector_memory import search_memory, get_all_memories
from backend.core.config import DEFAULT_MODEL, MAX_AGENT_STEPS, OPENAI_API_KEY


app = FastAPI(
    title="AI Assistant",
    description="Modular AI Assistant Backend",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    message: str


class MemorySearchRequest(BaseModel):
    query: str
    n_results: int = 3


@app.get("/")
async def root():
    return {
        "message": "AI Assistant Backend Running"
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    ai_response = get_ai_response(request.message)

    return {
        "response": ai_response
    }


@app.get("/history")
async def history():
    return {
        "history": get_history()
    }


@app.post("/history/clear")
async def clear_chat_history():
    clear_history()

    return {
        "message": "Chat history cleared"
    }


@app.get("/tasks")
async def tasks():
    return {
        "tasks": list_tasks()
    }


@app.post("/memory/search")
async def memory_search(request: MemorySearchRequest):
    results = search_memory(
        request.query,
        request.n_results
    )

    return {
        "results": results
    }


@app.get("/memory/all")
async def memory_all():
    return {
        "memory": get_all_memories()
    }

@app.get("/status")
async def status():
    return {
        "status": "running",
        "model": DEFAULT_MODEL,
        "max_agent_steps": MAX_AGENT_STEPS,
        "openai_api_key_loaded": bool(OPENAI_API_KEY),
        "available_tools": [
            "read_file",
            "write_file",
            "list_files",
            "run_python_code"
        ]
    }