TOOLS = {
    "read_file": {
        "description": "Read a file inside the project directory.",
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
    },
    "create_media_project": {
        "description": "Create a structured media production project.",
        "args": {
            "project_name": "Name of the media project.",
            "description": "Description of the project."
        }
    },
    "create_media_package": {
        "description": "Create a full media production package with prompts, storyboard, and shot list.",
        "args": {
            "project_name": "Name of the media project.",
            "concept": "Short concept description.",
            "image_prompt": "Image generation prompt.",
            "video_prompt": "Video generation prompt.",
            "audio_prompt": "Audio/music/voice prompt.",
            "storyboard": "Storyboard text.",
            "shot_list": "Shot list text."
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