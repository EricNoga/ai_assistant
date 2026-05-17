import json
from pathlib import Path
from datetime import datetime


STATE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "state"
AUDIT_FILE = STATE_DIR / "approval_audit.json"

STATE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def _load_audit_events():
    if not AUDIT_FILE.exists():
        return []

    try:
        return json.loads(
            AUDIT_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError:
        return []


def _save_audit_events(events: list):
    AUDIT_FILE.write_text(
        json.dumps(
            events,
            indent=2
        ),
        encoding="utf-8"
    )


audit_events = _load_audit_events()


def record_approval_event(
    approval_id: str,
    action: str,
    details: dict = None
):
    event = {
        "approval_id": approval_id,
        "action": action,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }

    audit_events.append(
        event
    )

    _save_audit_events(
        audit_events
    )

    return event


def list_approval_audit_events():
    return audit_events


def get_audit_events_for_approval(
    approval_id: str
):
    return [
        event
        for event in audit_events
        if event["approval_id"] == approval_id
    ]