import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")

MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "5"))

MEMORY_DB_PATH = os.getenv(
    "MEMORY_DB_PATH",
    str(PROJECT_ROOT / "backend" / "memory_db")
)