import keyword
import re
from collections import Counter

SUSPICIOUS_KEYWORDS = [
    "failed password",
    "failed login",
    "authentication failure",
    "invalid user",
    "unauthorized",
    "denied",
    "blocked",
    "malware",
    "trojan",
    "ransomware",
    "phishing",
    "brute force",
    "sql injection",
    "xss",
    "exploit",
    "privilege escalation"
]

def analyze_security_log(log_text: str):
    findings = []
    severity ="Low"

    text_lower = log_text.lower()

    matched_keywords = [
        keyword
        for keyword in SUSPICIOUS_KEYWORDS
        if keyword in text_lower
    ]

    ip_addresses = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        log_text
    )

    ip_counts = Counter(ip_addresses)

    repeated_ips = {
        ip: count
        for ip, count in ip_counts.items()
        if count >= 5
    }

    if matched_keywords:
        findings.append(
            {
                "type": "suspicious_keywords",
                "details": matched_keywords
            }
        )

    if repeated_ips and matched_keywords:
        severity = "High"
    elif matched_keywords or repeated_ips:
        severity = "Medium"

    recommendations = [
        "Review affected accounts and authentication logs.",
        "Check whether the source IP is trusted or expected.",
        "Consider blocking repeated suspicious IPs at the firewall.",
        "Enable or verify MFA for targeted accounts.",
        "Preserve logs for incident reviews.",
        "Correlate with endpoint and network monitoring alerts."
    ]

    return {
        "severity": severity,
        "matched_keywords": matched_keywords,
        "repeated_ips": repeated_ips,
        "findings": findings,
        "recommendations": recommendations
    }