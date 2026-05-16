from fastapi import APIRouter

from backend.tools.registry import (
TOOLS,
get_tool_names
)

router = APIRouter(
    tags=["Tools"]
)

@router.get("/tools")
async def tools():
    return {
        "tools": TOOLS
    }

@router.get("/tools/names")
async def tool_names():
    return {
        "tools": get_tool_names()
    }