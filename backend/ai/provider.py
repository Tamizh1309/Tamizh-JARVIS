from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger("tamizh_jarvis.ai")


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
    """
    Factory to retrieve configured AI provider.
    Predictable Selection:
    - If provider_type explicitly specified (GEMINI, LOCAL, FALLBACK), load it.
    - If AUTO:
      -> Gemini configured (API key set & valid) -> GeminiProvider
      -> otherwise if local configured -> LocalProvider
      -> otherwise -> FallbackProvider
    """
    from config.settings import get_settings
    from ai.gemini_provider import GeminiProvider
    from ai.local_provider import LocalProvider
    from ai.fallback_provider import FallbackProvider

    settings = get_settings()
    choice = (provider_type or settings.DEFAULT_AI_PROVIDER).strip().upper()

    if choice == "GEMINI":
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    elif choice == "LOCAL":
        return LocalProvider(base_url=settings.LOCAL_LLM_BASE_URL, model=settings.LOCAL_LLM_MODEL)
    elif choice == "FALLBACK":
        return FallbackProvider()

    # AUTO Selection Strategy
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 0:
        logger.info("AUTO Provider Selection -> GeminiProvider selected")
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
    elif settings.LOCAL_LLM_BASE_URL and settings.LOCAL_LLM_BASE_URL != "http://localhost:11434":
        logger.info("AUTO Provider Selection -> LocalProvider selected")
        return LocalProvider(base_url=settings.LOCAL_LLM_BASE_URL, model=settings.LOCAL_LLM_MODEL)

    logger.info("AUTO Provider Selection -> FallbackProvider selected (deterministic offline)")
    return FallbackProvider()
