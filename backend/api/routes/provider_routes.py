from fastapi import APIRouter

from backend.core.config import DEFAULT_MODEL
from backend.providers.registry import (
    get_active_provider_name,
    get_valid_providers
)


router = APIRouter(
    tags=["Providers"]
)


@router.get("/providers")
async def providers():
    return {
        "active_provider": get_active_provider_name(),
        "valid_providers": get_valid_providers(),
        "default_model": DEFAULT_MODEL
    }