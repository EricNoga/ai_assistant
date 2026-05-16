from pathlib import Path

from backend.core.config import (
    PROJECT_ROOT,
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    MAX_AGENT_STEPS
)

from backend.tools.registry import get_tool_names

def check_health():
    data_dir = PROJECT_ROOT / "data"
    state_dir = data_dir / "state"
    media_dir = data_dir / "media"
    security_dir = data_dir / "security"

    checks = {
        "project_root_exists": PROJECT_ROOT.exists(),
        "data_dir_exists": data_dir.exists(),
        "state_dir_exists": state_dir.exists(),
        "media_dir_exists": media_dir.exists(),
        "security_dir_exists": security_dir.exists(),
        "openai_api_key_loaded": bool(OPENAI_API_KEY),
        "default_model": DEFAULT_MODEL,
        "max_agent_steps": MAX_AGENT_STEPS,
        "available_tools": get_tool_names()
    }

    overall_ok = all (
        value is True
        for key, value in checks.items()
        if key.endswith("_exists") or key == "openai_api_key_loaded"
    )

    return {
        "ok": overall_ok,
        "checks": checks
    }