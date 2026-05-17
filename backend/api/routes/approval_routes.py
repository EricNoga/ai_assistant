from fastapi import APIRouter

from backend.security.approval_manager import (
    list_approvals,
    get_approval,
    approve_request,
    deny_request,
    mark_executed
)

from backend.orchestrator.tool_router import (
    run_tool_with_approval_override
)


router = APIRouter(
    tags=["Approvals"]
)


@router.get("/approvals")
async def approvals():
    return {
        "approvals": list_approvals()
    }


@router.get("/approvals/{approval_id}")
async def approval_detail(approval_id: str):
    return {
        "approval": get_approval(approval_id)
    }


@router.post("/approvals/{approval_id}/approve")
async def approve_approval(approval_id: str):
    approval = approve_request(
        approval_id
    )

    if not approval:
        return {
            "error": "Approval not found"
        }

    return {
        "approval": approval
    }


@router.post("/approvals/{approval_id}/deny")
async def deny_approval(approval_id: str):
    approval = deny_request(
        approval_id
    )

    if not approval:
        return {
            "error": "Approval not found"
        }

    return {
        "approval": approval
    }


@router.post("/approvals/{approval_id}/execute")
async def execute_approval(approval_id: str):
    approval = get_approval(
        approval_id
    )

    if not approval:
        return {
            "error": "Approval not found"
        }

    if approval["status"] != "approved":
        return {
            "error": "Approval must be approved before execution",
            "approval": approval
        }

    result = run_tool_with_approval_override(
        approval["tool_name"],
        approval["args"]
    )

    executed_approval = mark_executed(
        approval_id,
        result
    )

    return {
        "approval": executed_approval,
        "result": result
    }