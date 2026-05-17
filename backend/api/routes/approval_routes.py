from fastapi import APIRouter

from backend.security.approval_manager import (
    list_approvals,
    get_approval,
    approve_request,
    deny_request,
    mark_executed
)

from backend.security.approval_audit import (
    list_approval_audit_events,
    get_audit_events_for_approval
)

from backend.orchestrator.tool_router import (
    run_tool_with_approval_override
)


router = APIRouter(
    tags=["Approvals"]
)


APPROVAL_STATE_ERRORS = {
    "approved": "Approval is already approved",
    "denied": "Approval has been denied and cannot be approved",
    "executed": "Approval has already been executed"
}


@router.get("/approvals")
async def approvals():
    return {
        "approvals": list_approvals()
    }


@router.get("/approvals/audit")
async def approval_audit():
    return {
        "events": list_approval_audit_events()
    }


@router.get("/approvals/{approval_id}/audit")
async def approval_audit_detail(approval_id: str):
    return {
        "events": get_audit_events_for_approval(
            approval_id
        )
    }


@router.get("/approvals/{approval_id}")
async def approval_detail(approval_id: str):
    return {
        "approval": get_approval(approval_id)
    }


@router.post("/approvals/{approval_id}/approve")
async def approve_approval(approval_id: str):
    current = get_approval(
        approval_id
    )

    if not current:
        return {
            "error": "Approval not found"
        }

    if current["status"] != "pending":
        return {
            "error": APPROVAL_STATE_ERRORS.get(
                current["status"],
                "Approval cannot be approved"
            ),
            "approval": current
        }

    approval = approve_request(
        approval_id
    )

    return {
        "approval": approval
    }


@router.post("/approvals/{approval_id}/deny")
async def deny_approval(approval_id: str):
    current = get_approval(
        approval_id
    )

    if not current:
        return {
            "error": "Approval not found"
        }

    if current["status"] != "pending":
        return {
            "error": "Only pending approvals can be denied",
            "approval": current
        }

    approval = deny_request(
        approval_id
    )

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

    if approval["status"] == "executed":
        return {
            "error": "Approval has already been executed",
            "approval": approval
        }

    if approval["status"] == "denied":
        return {
            "error": "Denied approval cannot be executed",
            "approval": approval
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