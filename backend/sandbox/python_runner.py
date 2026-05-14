import subprocess
import tempfile
import os


def run_python_code(code: str):
    """
    Safely execute Python code
    in a temporary sandbox file
    """

    try:

        # Create temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:

            temp_file.write(code)

            temp_path = temp_file.name

        # Execute with timeout
        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Cleanup temp file
        os.remove(temp_path)

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:

        return {
            "error": "Execution timed out"
        }

    except Exception as e:

        return {
            "error": str(e)
        }