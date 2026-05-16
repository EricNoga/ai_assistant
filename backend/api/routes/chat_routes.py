from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.config import USE_MOCK_AI
from backend.models.agent_engine import get_ai_response
from backend.models.mock_client import get_mock_ai_response


router = APIRouter(
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    if USE_MOCK_AI:
        ai_response = get_mock_ai_response(
            request.message
        )
    else:
        ai_response = get_ai_response(
            request.message
        )

    return {
        "response": ai_response
    }