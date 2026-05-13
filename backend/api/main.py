from fastapi import FastAPI
from pydantic import BaseModel

from backend.models.openai_client import get_ai_response

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