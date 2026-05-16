TOOLS = {
    "read_file": {
        "description": "Read a file inside the project directory.",
        "permission_level": "low",
        "args": {
            "path": "Relative path to the file."
        }
    },

    "write_file": {
        "description": "Write content to a file inside the project directory.",
        "permission_level": "medium",
        "args": {
            "path": "Relative path to the file.",
            "content": "Text content to write."
        }
    },

    "list_files": {
        "description": "List files inside a project directory.",
        "permission_level": "low",
        "args": {
            "path": "Relative path to the directory."
        }
    },

    "run_python_code": {
        "description": "Run Python code in a limited sandbox.",
        "permission_level": "high",
        "args": {
            "code": "Python code to execute."
        }
    },

    "create_media_project": {
        "description": "Create a structured media production project.",
        "permission_level": "medium",
        "args": {
            "project_name": "Name of the media project.",
            "description": "Description of the project."
        }
    },

    "create_media_package": {
        "description": "Create a full media production package with prompts, storyboard, and shot list.",
        "permission_level": "medium",
        "args": {
            "project_name": "Name of the media project.",
            "concept": "Short concept description.",
            "image_prompt": "Image generation prompt.",
            "video_prompt": "Video generation prompt.",
            "audio_prompt": "Audio/music/voice prompt.",
            "storyboard": "Storyboard text.",
            "shot_list": "Shot list text."
        }
    },

    "analyze_security_log": {
        "description": "Analyze defensive security logs for suspicious keywords, repeated IPs, and recommended actions.",
        "permission_level": "low",
        "args": {
            "log_text": "Security log text to analyze."
        }
    },

    "save_security_report": {
        "description": "Save a structured cybersecurity incident report.",
        "permission_level": "medium",
        "args": {
            "report_name": "Name of the report.",
            "findings": "Security findings text.",
            "severity": "Severity level.",
            "recommendations": "Recommended actions."
        }
    }
}


def get_tool_names():
    return list(
        TOOLS.keys()
    )


def get_tool_metadata(tool_name: str):
    return TOOLS.get(
        tool_name
    )


def get_tool_permission_level(tool_name: str):
    tool = get_tool_metadata(
        tool_name
    )

    if not tool:
        return None

    return tool.get(
        "permission_level",
        "unknown"
    )


def get_tool_descriptions():
    lines = []

    for name, data in TOOLS.items():
        args = ", ".join(
            data["args"].keys()
        )

        permission_level = data.get(
            "permission_level",
            "unknown"
        )

        lines.append(
            f"- {name}({args}): "
            f"{data['description']} "
            f"[permission: {permission_level}]"
        )

    return "\n".join(lines)