from pathlib import Path
from datetime import datetime

BASE_MEDIA_PATH = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
    / "data"
    / "media"
    / "projects"
)

def create_media_prompt(
        project_name: str,
        description: str
):
    """
    Creates a media project folder
    with starter production files.
    """

    safe_name = (
        project_name
        .lower()
        .replace(" ", "_")
    )

    project_path = (
        BASE_MEDIA_PATH / safe_name
    )

    project_path.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %h:%M:%S"
    )

    # Create starter files
    files = {
        "project_overview.txt":
            f"""
PROJECT:
{project_name}

DESCRIPTION:
{description}

CREATED:
{timestamp}
""",

        "image_prompts.txt":
        "# Image prompts\n",

        "video_prompts.txt":
        "# Video prompts\n",

        "audio_prompts.txt":
        "# Audio prompts\n",

        "storyboard.txt":
        "# Storyboard\n",

        "shot_list.txt":
        "# Shot list\n"
    }

    for filename, content in files.items():

        file_path = (
            project_path / filename
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

    return {
        "status": "success",
        "project_path": str(project_path),
        "created_files": list(files.keys())
    }