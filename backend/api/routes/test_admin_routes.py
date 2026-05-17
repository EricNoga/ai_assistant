from fastapi import APIRouter

from backend.core.config import AI_PROVIDER
from backend.security.approval_cleanup import clear_approval_state

router = APIRouter(
    tags=["Test Admin"]
)

@router.post("/test-admin/clear-approvals")
async def clear_approvals():
    if AI_PROVIDER != "mock":
        return {
            "error": "This endpoint is only available in mock/test mode."
        }

    return clear_approval_state()