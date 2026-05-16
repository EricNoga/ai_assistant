from pathlib import Path
from datetime import datetime


BASE_SECURITY_PATH = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
    / "data"
    / "security"
    / "reports"
)


def save_security_report(
    report_name: str,
    findings: str,
    severity: str,
    recommendations: str
):
    """
    Save a structured security report.
    """

    safe_name = (
        report_name
        .lower()
        .replace(" ", "_")
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    filename = (
        f"{safe_name}_{timestamp}.txt"
    )

    report_path = (
        BASE_SECURITY_PATH / filename
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report_content = f"""
SECURITY REPORT
===========================

REPORT NAME:
{report_name}

GENERATED:
{timestamp}

SEVERITY:
{severity}

FINDINGS:
{findings}

RECOMMENDATIONS:
{recommendations}
"""

    report_path.write_text(
        report_content,
        encoding="utf-8"
    )

    return {
        "status": "success",
        "report_path": str(report_path),
        "severity": severity
    }