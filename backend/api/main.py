from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.core.bootstrap import bootstrap_project
from backend.api.routes.chat_routes import router as chat_router
from backend.api.routes.system_routes import router as system_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap_project()
    yield


app = FastAPI(
    title="AI Assistant",
    description="Modular AI Assistant Backend",
    version="0.1.0",
    lifespan=lifespan
)


app.include_router(system_router)
app.include_router(chat_router)