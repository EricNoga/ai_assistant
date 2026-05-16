from backend.tools.file_system import read_file, write_file, list_files
from backend.sandbox.python_runner import run_python_code
from backend.tools.media_tools import create_media_project
from backend.tools.media_workflow import create_media_package
from backend.tools.cybersecurity_tools import analyze_security_log


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_python_code": run_python_code,
    "create_media_project": create_media_project,
    "create_media_package": create_media_package,
    "analyze_security_log": analyze_security_log
}


def run_tool(tool_name: str, args: dict):
    """
    Routes AI tool requests to backend functions.
    """

    if args is None:
        args = {}

    if tool_name not in TOOL_FUNCTIONS:
        return f"Unknown tool requested: {tool_name}"

    try:
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

    except Exception as e:
        return f"Tool runtime error: {str(e)}"