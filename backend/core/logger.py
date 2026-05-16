import logging
from pathlib import Path

from backend.core.config import PROJECT_ROOT


LOG_DIR = PROJECT_ROOT / "data" / "logs"
LOG_FILE = LOG_DIR / "assistant.log"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


logger = logging.getLogger("ai_assistant")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(
    LOG_FILE,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)


if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)