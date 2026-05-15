from fastapi import FastAPI
from pydantic import BaseModel

from backend.models.openai_client import get_ai_response
from backend.memory.chat_memory import get_history, clear_history
from backend.memory.task_memory import list_tasks


app = FastAPI(
    title="AI Assistant",
    description="Modular AI Assistant Backend",
    version="0.1.0"
)


class ChatRequest(BaseModel):
    message: str


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