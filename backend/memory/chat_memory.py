import json
from pathlib import Path


STATE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "state"
CHAT_FILE = STATE_DIR / "chat_history.json"

MAX_HISTORY = 40

STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_history():
    if not CHAT_FILE.exists():
        return []

    try:
        return json.loads(
            CHAT_FILE.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError:
        return []


def _save_history(history: list):
    CHAT_FILE.write_text(
        json.dumps(
            history,
            indent=2
        ),
        encoding="utf-8"
    )


chat_history = _load_history()


def add_message(
    role: str,
    content: str
):
    chat_history.append(
        {
            "role": role,
            "content": content
        }
    )

    while len(chat_history) > MAX_HISTORY:
        chat_history.pop(0)

    _save_history(
        chat_history
    )


def get_history():
    return chat_history


def clear_history():
    chat_history.clear()

    _save_history(
        chat_history
    )