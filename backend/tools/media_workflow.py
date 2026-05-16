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

def create_media_package(
        project_name: str,
        concept: str,
        image_prompt: str,
        video_prompt: str,
        audio_prompt: str,
        storyboard: str,
        shot_list: str
):
    safe_name = project_name.lower().replace(" ", "_")
    project_path = BASE_MEDIA_PATH / safe_name

    project_path.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    files = {
        "project_overview.txt": f"""
PROJECT:
{project_name}

CONCEPT:
{concept}

CREATED:
{timestamp}
""",
        "image_prompts.txt": image_prompt,
        "video_prompts.txt": video_prompt,
        "audio_prompts.txt": audio_prompt,
        "storyboard.txt": storyboard,
        "shot_list.txt": shot_list
    }

    for filename, content in files.items():
        file_path = project_path / filename
        file_path.write_text(content or "", encoding="utf-8")

    return{
        "status": "success",
        "project_path": str(project_path),
        "created_files": list(files.keys())
    }