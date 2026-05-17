from backend.security.approval_manager import (
    approvals,
    _save_approvals
)
from backend.security.approval_audit import (
    audit_events,
    _save_audit_events
)

def clear_approval_state():
    approvals.clear()
    audit_events.clear()

    _save_approvals(
        approvals
    )

    _save_audit_events(
        audit_events
    )

    return {
        "message": "Approval state cleared"
    }