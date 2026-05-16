from backend.tools.file_system import read_file, write_file, list_files
from backend.sandbox.python_runner import run_python_code


TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_python_code": run_python_code
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

    except Exception as e:
        return f"Tool runtime error: {str(e)}"