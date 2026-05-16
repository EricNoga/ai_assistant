from backend.core.config import AI_PROVIDER


VALID_PROVIDERS = [
    "mock",
    "openai"
]


def get_active_provider_name():
    if AI_PROVIDER in VALID_PROVIDERS:
        return AI_PROVIDER

    return "mock"


def get_valid_providers():
    return VALID_PROVIDERS