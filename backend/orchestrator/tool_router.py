from backend.tools.file_system import read_file, write_file, list_files

def run_tool(tool_name: str, args: dict):
    """Routes AI tool requests to actual functions"""

    if tool_name == "read_file":
        return read_file(args.get("path"))

    if tool_name == "write_file":
        return write_file(
            args.get("path"),
            args.get("content")
        )

    if tool_name == "list_files":
        return list_files(args.get("path", "."))

    return "Unknown tool requested."