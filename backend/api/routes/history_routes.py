from fastapi import APIRouter

from backend.memory.chat_memory import get_history, clear_history


router = APIRouter(
    tags=["History"]
)


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