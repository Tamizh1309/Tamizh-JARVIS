from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """Abstract base class for all AI LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """Generate response given a prompt and optional system prompt."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check whether the AI provider is reachable and operational."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        pass


def get_ai_provider(provider_type: Optional[str] = None) -> AIProvider:
    """Factory to retrieve configured or fallback AI provider."""
    from config.settings import get_settings
    from ai.gemini_provider import GeminiProvider
    from ai.local_provider import LocalProvider
    from ai.fallback_provider import FallbackProvider

    settings = get_settings()
    choice = provider_type or settings.DEFAULT_AI_PROVIDER

    if choice == "gemini" or (choice == "auto" and settings.GEMINI_API_KEY):
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    elif choice == "local":
        return LocalProvider(base_url=settings.LOCAL_LLM_BASE_URL, model=settings.LOCAL_LLM_MODEL)

    return FallbackProvider()

