from fastapi import APIRouter
from pydantic import BaseModel

from backend.orchestrator.tool_router import run_tool
from backend.tools.registry import get_tool_names

router = APIRouter(
    tags=["Tools"]
)

class ToolRunRequest(BaseModel):
    tool_name: str
    args: dict = {}

@router.post("/tools/run")
async def run_tool_endpoint(request: ToolRunRequest):
    if request.tool_name not in get_tool_names():
        return {
            "error": f"Unknown tool: {request.tool_name}",
            "available_tools": get_tool_names()
        }

    result = run_tool(
        request.tool_name,
        request.args
    )

    return {
        "tool_name": request.tool_name,
        "result": result
    }