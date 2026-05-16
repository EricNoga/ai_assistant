from backend.core.config import (
    PROJECT_ROOT,
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    MAX_AGENT_STEPS,
    ALLOW_MEDIUM_RISK_TOOLS,
    ALLOW_HIGH_RISK_TOOLS
)

from backend.tools.registry import get_tool_names

from backend.providers.registry import (
    get_active_provider_name,
    get_valid_providers
)


def check_health():
    data_dir = PROJECT_ROOT / "data"
    state_dir = data_dir / "state"
    media_dir = data_dir / "media"
    security_dir = data_dir / "security"
    logs_dir = data_dir / "logs"

    checks = {
        "project_root_exists": PROJECT_ROOT.exists(),
        "data_dir_exists": data_dir.exists(),
        "state_dir_exists": state_dir.exists(),
        "media_dir_exists": media_dir.exists(),
        "security_dir_exists": security_dir.exists(),
        "logs_dir_exists": logs_dir.exists(),
        "openai_api_key_loaded": bool(OPENAI_API_KEY),
        "active_provider": get_active_provider_name(),
        "valid_providers": get_valid_providers(),
        "default_model": DEFAULT_MODEL,
        "max_agent_steps": MAX_AGENT_STEPS,
        "allow_medium_risk_tools": ALLOW_MEDIUM_RISK_TOOLS,
        "allow_high_risk_tools": ALLOW_HIGH_RISK_TOOLS,
        "available_tools": get_tool_names()
    }

    required_checks = [
        "project_root_exists",
        "data_dir_exists",
        "state_dir_exists",
        "media_dir_exists",
        "security_dir_exists",
        "logs_dir_exists"
    ]

    overall_ok = all(
        checks[item] is True
        for item in required_checks
    )

    return {
        "ok": overall_ok,
        "checks": checks
    }