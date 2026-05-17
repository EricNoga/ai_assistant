from backend.core.config import (
    ALLOW_MEDIUM_RISK_TOOLS,
    ALLOW_HIGH_RISK_TOOLS
)

from backend.tools.file_system import read_file, write_file, list_files
from backend.sandbox.python_runner import run_python_code
from backend.tools.media_tools import create_media_project
from backend.tools.media_workflow import create_media_package
from backend.tools.cybersecurity_tools import analyze_security_log
from backend.tools.security_reports import save_security_report
from backend.tools.cleanup_tools import cleanup_test_file

from backend.tools.registry import get_tool_permission_level


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_python_code": run_python_code,
    "create_media_project": create_media_project,
    "create_media_package": create_media_package,
    "analyze_security_log": analyze_security_log,
    "save_security_report": save_security_report,
    "cleanup_test_file": cleanup_test_file
}


def _is_tool_allowed(tool_name: str):
    permission_level = get_tool_permission_level(
        tool_name
    )

    if permission_level == "high":
        return ALLOW_HIGH_RISK_TOOLS

    if permission_level == "medium":
        return ALLOW_MEDIUM_RISK_TOOLS

    return True


def _execute_tool(
    tool_name: str,
    args: dict
):
    if tool_name == "read_file":
        return TOOL_FUNCTIONS[tool_name](
            args.get("path")
        )

    if tool_name == "write_file":
        return TOOL_FUNCTIONS[tool_name](
            args.get("path"),
            args.get("content", "")
        )

    if tool_name == "list_files":
        return TOOL_FUNCTIONS[tool_name](
            args.get("path", ".")
        )

    if tool_name == "run_python_code":
        return TOOL_FUNCTIONS[tool_name](
            args.get("code", "")
        )

    if tool_name == "create_media_project":
        return TOOL_FUNCTIONS[tool_name](
            args.get("project_name", "untitled_project"),
            args.get("description", "")
        )

    if tool_name == "create_media_package":
        return TOOL_FUNCTIONS[tool_name](
            args.get("project_name", "untitled_project"),
            args.get("concept", ""),
            args.get("image_prompt", ""),
            args.get("video_prompt", ""),
            args.get("audio_prompt", ""),
            args.get("storyboard", ""),
            args.get("shot_list", "")
        )

    if tool_name == "analyze_security_log":
        return TOOL_FUNCTIONS[tool_name](
            args.get("log_text", "")
        )

    if tool_name == "save_security_report":
        return TOOL_FUNCTIONS[tool_name](
            args.get("report_name", "security_report"),
            args.get("findings", ""),
            args.get("severity", "Low"),
            args.get("recommendations", "")
        )

    if tool_name == "cleanup_test_file":
        return TOOL_FUNCTIONS[tool_name](
            args.get("path", "")
        )

    return f"Unknown tool requested: {tool_name}"


def run_tool(
    tool_name: str,
    args: dict
):
    """
    Routes AI tool requests to backend functions with permission checks.
    """

    from backend.security.approval_manager import create_approval_request

    if args is None:
        args = {}

    if tool_name not in TOOL_FUNCTIONS:
        return f"Unknown tool requested: {tool_name}"

    permission_level = get_tool_permission_level(
        tool_name
    )

    if not _is_tool_allowed(tool_name):
        approval_id = create_approval_request(
            tool_name=tool_name,
            args=args,
            permission_level=permission_level
        )

        return {
            "blocked": True,
            "reason": (
                f"Tool requires {permission_level}-risk permission."
            ),
            "approval_id": approval_id,
            "tool_name": tool_name,
            "permission_level": permission_level
        }

    try:
        return _execute_tool(
            tool_name,
            args
        )

    except Exception as e:
        return f"Tool runtime error: {str(e)}"


def run_tool_with_approval_override(
    tool_name: str,
    args: dict
):
    """
    Executes a tool after explicit approval.
    This bypasses global permission flags but still only runs registered tools.
    """

    if args is None:
        args = {}

    if tool_name not in TOOL_FUNCTIONS:
        return f"Unknown tool requested: {tool_name}"

    try:
        return _execute_tool(
            tool_name,
            args
        )

    except Exception as e:
        return f"Tool runtime error: {str(e)}"