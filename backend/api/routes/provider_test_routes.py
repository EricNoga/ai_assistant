from fastapi import APIRouter

from backend.providers.ai_provider import chat_completion

router = APIRouter(
    tags=["Providers"]
)

@router.get("/providers/test")
async def provider_test():
    response = chat_completion(
        [
            {
                "role": "system",
                "content": "You are a provider smoke text."
            },
            {
                "role": "user",
                "content": "Say provider test successful."
            }
        ]
    )

    return {
        "response": response
    }