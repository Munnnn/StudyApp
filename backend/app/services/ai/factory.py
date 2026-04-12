"""Return the configured AIService based on AI_PROVIDER env var."""
from functools import lru_cache

from app.config import settings
from app.services.ai.base import AIService


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    provider = settings.AI_PROVIDER.lower()
    if provider == "anthropic":
        from app.services.ai.anthropic_adapter import AnthropicAdapter
        return AnthropicAdapter(api_key=settings.ANTHROPIC_API_KEY)
    if provider == "openai":
        from app.services.ai.openai_adapter import OpenAIAdapter
        return OpenAIAdapter(api_key=settings.OPENAI_API_KEY)
    if provider == "fake":
        try:
            from tests.fake_ai import FakeAIService
        except ImportError:
            from app.services.ai.fake import FakeAIService  # type: ignore[no-redef]
        return FakeAIService()
    raise ValueError(f"Unknown AI_PROVIDER: {provider!r}. Use 'anthropic', 'openai', or 'fake'.")
