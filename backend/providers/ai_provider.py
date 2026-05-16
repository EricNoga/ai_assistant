import json

from openai import OpenAI, OpenAIError, RateLimitError

from backend.core.config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL
)
from backend.core.logger import logger
from backend.providers.registry import get_active_provider_name


openai_client = OpenAI(
    api_key=OPENAI_API_KEY
)


def _get_last_user_message(messages: list):
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")

    return ""


def _get_first_system_message(messages: list):
    for message in messages:
        if message.get("role") == "system":
            return message.get("content", "")

    return ""


def mock_chat(messages: list):
    last_user_message = _get_last_user_message(
        messages
    )

    system_message = _get_first_system_message(
        messages
    )

    if "JSON list of tasks" in system_message:
        return json.dumps(
            [
                {
                    "task": last_user_message,
                    "agent": "general"
                }
            ]
        )

    if "reviewer agent" in system_message.lower():
        return last_user_message

    return (
        "Mock AI response. "
        f"Last user message was: {last_user_message}"
    )


def openai_chat(messages: list):
    response = openai_client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages
    )

    content = response.choices[0].message.content

    if content is None:
        return ""

    return content


def chat_completion(messages: list):
    provider = get_active_provider_name()

    if provider == "mock":
        return mock_chat(
            messages
        )

    if provider == "openai":
        try:
            return openai_chat(
                messages
            )

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
                "OpenAI API error: %s",
                str(e)
            )

            return (
                "OpenAI API error occurred. "
                "Check your API key, billing, model name, or network."
            )

        except Exception as e:
            logger.error(
                "Unexpected AI provider error: %s",
                str(e)
            )

            return (
                "Unexpected AI provider error occurred."
            )

    return "No valid AI provider configured."