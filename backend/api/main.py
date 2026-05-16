from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.core.bootstrap import bootstrap_project

from backend.api.routes.chat_routes import router as chat_router
from backend.api.routes.history_routes import router as history_router
from backend.api.routes.task_routes import router as task_router
from backend.api.routes.run_routes import router as run_router
from backend.api.routes.memory_routes import router as memory_router
from backend.api.routes.status_routes import router as status_router


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


app.include_router(status_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(task_router)
app.include_router(run_router)
app.include_router(memory_router)