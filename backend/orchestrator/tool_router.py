from backend.tools.file_system import read_file, write_file, list_files
from backend.sandbox.python_runner import run_python_code


def run_tool(tool_name: str, args: dict):
    """
    Routes AI tool requests to backend functions.
    """

    if args is None:
        args = {}

    if tool_name == "read_file":
        return read_file(
            args.get("path")
        )

    if tool_name == "write_file":
        return write_file(
            args.get("path"),
            args.get("content")
        )

    if tool_name == "list_files":
        return list_files(
            args.get("path", ".")
        )

    if tool_name == "run_python_code":
        return run_python_code(
            args.get("code", "")
        )

    return f"Unknown tool requested: {tool_name}"