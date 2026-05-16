from fastapi import APIRouter

from backend.core.config import (
    DEFAULT_MODEL,
    MAX_AGENT_STEPS,
    OPENAI_API_KEY
)
from backend.core.health import check_health
from backend.core.bootstrap import bootstrap_project
from backend.tools.registry import get_tool_names
from backend.providers.registry import (
    get_active_provider_name,
    get_valid_providers
)


router = APIRouter(
    tags=["Status"]
)


@router.get("/")
async def root():
    return {
        "message": "AI Assistant Backend Running"
    }


@router.get("/status")
async def status():
    return {
        "status": "running",
        "provider": get_active_provider_name(),
        "valid_providers": get_valid_providers(),
        "model": DEFAULT_MODEL,
        "max_agent_steps": MAX_AGENT_STEPS,
        "openai_api_key_loaded": bool(OPENAI_API_KEY),
        "available_tools": get_tool_names()
    }


@router.get("/health")
async def health():
    return check_health()


@router.post("/bootstrap")
async def bootstrap():
    folders = bootstrap_project()

    return {
        "message": "Bootstrap completed",
        "folders": folders
    }