"""
LLM Manager with Automatic Fallback

Manages multiple LLM providers with automatic fallback on failure.
"""

import logging
import os
from typing import Dict, List, Optional

from .providers import (
    LLMProvider,
    LLMResponse,
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
)

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages multiple LLM providers with automatic fallback."""

    def __init__(self, preferred_provider: Optional[str] = None):
        """Initialize LLM manager.

        Args:
            preferred_provider: Preferred provider name ("anthropic", "openai", "gemini")
        """
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()

        self.preferred_provider = preferred_provider or os.environ.get(
            "LLM_PROVIDER", "anthropic"
        )
        logger.info(
            f"LLM Manager initialized with preferred provider: {self.preferred_provider}"
        )

    def _initialize_providers(self):
        """Initialize all available providers."""
        provider_classes = [
            (AnthropicProvider, "anthropic"),
            (OpenAIProvider, "openai"),
            (GeminiProvider, "gemini"),
        ]

        for provider_class, provider_name in provider_classes:
            try:
                provider = provider_class()
                if provider.is_available():
                    self.providers[provider_name] = provider
                    logger.info(f"Provider {provider_name} is available")
            except Exception as e:
                logger.debug(f"Could not initialize {provider_class.__name__}: {e}")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        provider: Optional[str] = None,
        fallback: bool = True,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate response using specified or preferred provider.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/query
            provider: Specific provider to use (None = use preferred)
            fallback: If True, try other providers on failure
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            LLMResponse with generated text

        Raises:
            RuntimeError: If no providers are available or all fail
        """
        if not self.providers:
            raise RuntimeError(
                "No LLM providers available. Set API keys and install packages."
            )

        # Determine which provider to use
        target_provider = provider or self.preferred_provider

        # Try preferred provider first
        if target_provider in self.providers:
            try:
                return await self.providers[target_provider].complete(
                    system_prompt, user_prompt, max_tokens, temperature
                )
            except Exception as e:
                logger.warning(f"Provider {target_provider} failed: {e}")
                if not fallback:
                    raise

        # Fallback to other providers
        if fallback:
            for name, prov in self.providers.items():
                if name == target_provider:
                    continue  # Already tried
                try:
                    logger.info(f"Falling back to provider: {name}")
                    return await prov.complete(
                        system_prompt, user_prompt, max_tokens, temperature
                    )
                except Exception as e:
                    logger.warning(f"Provider {name} failed: {e}")
                    continue

        raise RuntimeError("All LLM providers failed")

    def list_available_providers(self) -> List[str]:
        """Get list of available provider names.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get specific provider by name.

        Args:
            name: Provider name

        Returns:
            LLMProvider instance or None if not found
        """
        return self.providers.get(name)

    def is_any_available(self) -> bool:
        """Check if any provider is available.

        Returns:
            True if at least one provider is available
        """
        return len(self.providers) > 0


# Global instance for easy access
_manager: Optional[LLMManager] = None


def get_llm_manager(preferred_provider: Optional[str] = None) -> LLMManager:
    """Get or create global LLM manager instance.

    Args:
        preferred_provider: Preferred provider name (only used on first call)

    Returns:
        LLMManager instance
    """
    global _manager
    if _manager is None:
        _manager = LLMManager(preferred_provider=preferred_provider)
    return _manager
