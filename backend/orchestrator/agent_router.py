def choose_agent(user_message: str):
    message = user_message.lower()

    cybersecurity_keywords = [
        "cybersecurity",
        "security",
        "defender",
        "defense",
        "threat",
        "alert",
        "incident",
        "malware",
        "phishing",
        "vulnerability",
        "exploit",
        "cve",
        "siem",
        "log",
        "firewall",
        "ids",
        "ips",
        "wazuh",
        "suricata",
        "zeek",
        "wireshark",
        "suspicious",
        "blocked",
        "unauthorized",
        "authentication",
        "brute force"
    ]

    coding_keywords = [
        "code",
        "script",
        "python",
        "debug",
        "function",
        "class",
        "file",
        "api",
        "fastapi",
        "error",
        "bug",
        "program",
        "run"
    ]

    if any(keyword in message for keyword in cybersecurity_keywords):
        return "cybersecurity"

    if any(keyword in message for keyword in coding_keywords):
        return "coding"

    return "general"