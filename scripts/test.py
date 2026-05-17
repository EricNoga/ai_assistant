import os
import subprocess
import sys

def run_tests():
    env = os.environ.copy()

    env["AI_PROVIDER"] = "mock"
    env["USE_MOCK_AI"] = "true"
    env["ALLOW_MEDIUM_RISK_TOOLS"] = "true"
    env["ALLOW_HIGH_RISK_TOOLS"] = "false"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest"
        ],
        env=env
    )

    return result.returncode

if __name__ == "__main__":
    raise SystemExit(
        run_tests()
    )