from fastapi import APIRouter
from pydantic import BaseModel

from backend.models.openai_client import get_ai_response


router = APIRouter(
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    ai_response = get_ai_response(
        request.message
    )

    return {
        "response": ai_response
    }