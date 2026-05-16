from backend.core.config import USE_MOCK_AI


def get_active_provider_name():
    if USE_MOCK_AI:
        return "mock"

    return "openai"