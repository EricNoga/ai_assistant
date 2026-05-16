import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

os.environ["AI_PROVIDER"] = "mock"
os.environ["USE_MOCK_AI"] = "true"
os.environ["ALLOW_MEDIUM_RISK_TOOLS"] = "true"
os.environ["ALLOW_HIGH_RISK_TOOLS"] = "false"