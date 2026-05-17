import os
import subprocess
import sys

def run_dev_server():
    env = os.environ.copy()

    env.setdefault(
        "AI_PROVIDER",
        "mock"
    )

    env.setdefault(
        "ALLOW_MEDIUM_RISK_TOOLS",
        "true"
    )

    env.setdefault(
        "ALLOW_HIGH_RISK_TOOLS",
        "false"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.api.main:app",
            "--reload"
        ],
        env=env,
    )

    return result.returncode

if __name__ == "__main__":
    raise SystemExit(
        run_dev_server()
    )