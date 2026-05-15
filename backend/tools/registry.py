TOOLS ={
    "read-file": {
        "description": "Read a file inside the project direcotry.",
        "args": {
            "path": "Relative path to the file."
        }
    },
    "write_file": {
        "description": "Write content to a file inside the project directory.",
        "args": {
            "path": "Relative path to the file.",
            "content": "Text content to write."
        }
    },
    "list_files": {
        "description": "List files inside a project directory.",
        "args": {
            "path": "Relative path to the directory."
        }
    },
    "run_python_code": {
        "description": "Run Python code in a limited sandbox.",
        "args": {
            "code": "Python code to execute."
        }
    }
}

def get_tool_names():
    return list(TOOLS.keys())

def get_tool_descriptions():
    lines = []

    for name, data in TOOLS.items():
        args = ", ".join(data["args"].keys())
        lines.append(f"- {name}({args}): {data['description']}")

    return "\n".join(lines)