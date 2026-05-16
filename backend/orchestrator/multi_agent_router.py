def choose_agents(user_message: str):
    message = user_message.lower()

    selected_agents = []

    cybersecurity_keywords = [
        "security",
        "cybersecurity",
        "log",
        "alert",
        "incident",
        "threat",
        "malware",
        "phishing",
        "vulnerability",
        "firewall",
        "wireshark",
        "suricata",
        "wazuh"
    ]

    coding_keywords = [
        "code",
        "script",
        "python",
        "parser",
        "debug",
        "api",
        "fastapi",
        "function",
        "program",
        "automation"
    ]

    media_keywords = [
        "image",
        "video",
        "audio",
        "visual",
        "chart",
        "storyboard",
        "prompt",
        "media",
        "cinematic"
    ]

    if any(keyword in message for keyword in cybersecurity_keywords):
        selected_agents.append("cybersecurity")

    if any(keyword in message for keyword in coding_keywords):
        selected_agents.append("coding")

    if any(keyword in message for keyword in media_keywords):
        selected_agents.append("media")

    if not selected_agents:
        selected_agents.append("general")

    return selected_agents