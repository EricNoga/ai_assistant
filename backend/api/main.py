from fastapi import FastAPI

app = FastAPI(
    title="AI Assistant",
    description="Modular AI Assistant Backend",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {
        "message": "AI Assistant Backend Running"
    }