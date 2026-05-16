def choose_agent(user_message: str):
    message = user_message.lower()

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

    if any(keyword in message for keyword in coding_keywords):
        return "coding"

    return "general"