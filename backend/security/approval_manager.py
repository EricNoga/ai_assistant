import json
import uuid
from pathlib import Path
from datetime import datetime

from backend.security.approval_audit import record_approval_event


STATE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "state"
APPROVALS_FILE = STATE_DIR / "approvals.json"

STATE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def _load_approvals():
    if not APPROVALS_FILE.exists():
        return {}

    try:
        return json.loads(
            APPROVALS_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError:
        return {}


def _save_approvals(approvals: dict):
    APPROVALS_FILE.write_text(
        json.dumps(
            approvals,
            indent=2
        ),
        encoding="utf-8"
    )


approvals = _load_approvals()


def create_approval_request(
    tool_name: str,
    args: dict,
    permission_level: str
):
    approval_id = str(
        uuid.uuid4()
    )

    approvals[approval_id] = {
        "id": approval_id,
        "tool_name": tool_name,
        "args": args,
        "permission_level": permission_level,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "resolved_at": None,
        "executed_at": None,
        "execution_result": None
    }

    _save_approvals(
        approvals
    )

    record_approval_event(
        approval_id,
        "created",
        {
            "tool_name": tool_name,
            "permission_level": permission_level
        }
    )

    return approval_id


def list_approvals():
    return list(
        approvals.values()
    )


def get_approval(
    approval_id: str
):
    return approvals.get(
        approval_id
    )


def approve_request(
    approval_id: str
):
    if approval_id not in approvals:
        return None

    approval = approvals[approval_id]

    if approval["status"] != "pending":
        return approval

    approval["status"] = "approved"
    approval["resolved_at"] = datetime.now().isoformat()

    _save_approvals(
        approvals
    )

    record_approval_event(
        approval_id,
        "approved",
        {
            "tool_name": approval["tool_name"]
        }
    )

    return approval


def deny_request(
    approval_id: str
):
    if approval_id not in approvals:
        return None

    approval = approvals[approval_id]

    if approval["status"] != "pending":
        return approval

    approval["status"] = "denied"
    approval["resolved_at"] = datetime.now().isoformat()

    _save_approvals(
        approvals
    )

    record_approval_event(
        approval_id,
        "denied",
        {
            "tool_name": approval["tool_name"]
        }
    )

    return approval


def mark_executed(
    approval_id: str,
    result
):
    if approval_id not in approvals:
        return None

    approval = approvals[approval_id]

    if approval["status"] != "approved":
        return approval

    approval["status"] = "executed"
    approval["executed_at"] = datetime.now().isoformat()
    approval["execution_result"] = result

    _save_approvals(
        approvals
    )

    record_approval_event(
        approval_id,
        "executed",
        {
            "tool_name": approval["tool_name"],
            "result": result
        }
    )

    return approval