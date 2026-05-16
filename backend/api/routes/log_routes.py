from fastapi import APIRouter

from backend.core.logger import LOG_FILE

router = APIRouter(
    tags=["Logs"]
)

@router.get("/logs")
async def get_logs(lines: int = 100):
    if not LOG_FILE.exists():
        return {
            "logs": []
        }

    content = LOG_FILE.read_text(
        encoding="utf-8"
    ).splitlines()

    return {
        "logs": content[-lines:]
    }