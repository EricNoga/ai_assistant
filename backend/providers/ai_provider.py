from openai import OpenAI, OpenAIError, RateLimitError

from backend.core.config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    USE_MOCK_AI
)

from backend.core.logger import logger

openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)

def mock_chat(messages: list):
    last_user_message = ""

    for message in reversed(messages):
        if message.get("role") == "user":
            last_user_message = message.get("content", "")
            break

        return (
            "Mock AI response. "
            f"Last user message was: {last_user_message}"
        )

def openai_chat(messages: list):
    response = openai_client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages
    )

    return response.choices[0].message.content

def chat_completion(messages: list):
    if USE_MOCK_AI:
        return mock_chat(messages)

    try:
        return openai_chat(messages)

    except RateLimitError as e:
        logger.error(
            "OpenAI quota/rate limit error: %s",
            str(e)
        )

        return (
            "OpenAI quota exceeded. "
            "Enable mock mode or add API credits."
        )

    except OpenAIError as e:
        logger.error(
            "OpenAPI error: %s",
            str(e)
        )

        return (
            "OpenAI API error occurred. "
            "Check your API key, billing, model name, or network."
        )