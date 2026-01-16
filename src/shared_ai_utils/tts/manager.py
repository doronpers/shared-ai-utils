"""
TTS Manager - Unified interface for text-to-speech with automatic fallback.

Provides a high-level interface for TTS with automatic provider fallback
and caching support.
"""

import logging
from typing import AsyncIterator, Optional

from .providers import (
    TTSProvider,
    TTSResponse,
    ElevenLabsTTSProvider,
    OpenAITTSProvider,
)

logger = logging.getLogger(__name__)


class TTSManager:
    """
    Manages TTS providers with automatic fallback.

    Example:
        manager = TTSManager()
        response = await manager.generate_speech("Hello, world!")
        # Audio bytes are in response.audio_data
    """

    PROVIDER_MAP = {
        "elevenlabs": ElevenLabsTTSProvider,
        "openai": OpenAITTSProvider,
    }

    def __init__(
        self,
        primary_provider: str = "elevenlabs",
        fallback_provider: Optional[str] = "openai",
        elevenlabs_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialize TTS manager.

        Args:
            primary_provider: Primary provider name ("elevenlabs" or "openai")
            fallback_provider: Fallback provider name (None to disable)
            elevenlabs_api_key: ElevenLabs API key (or use env var)
            openai_api_key: OpenAI API key (or use env var)
        """
        self.primary_provider: Optional[TTSProvider] = None
        self.fallback_provider: Optional[TTSProvider] = None

        # Initialize primary provider
        if primary_provider in self.PROVIDER_MAP:
            api_key = (
                elevenlabs_api_key if primary_provider == "elevenlabs" else openai_api_key
            )
            try:
                self.primary_provider = self.PROVIDER_MAP[primary_provider](api_key)
                if not self.primary_provider.is_available():
                    logger.warning(
                        f"Primary TTS provider {primary_provider} not available (missing API key)"
                    )
                    self.primary_provider = None
            except Exception as e:
                logger.warning(f"Failed to initialize primary TTS provider: {e}")

        # Initialize fallback provider
        if fallback_provider and fallback_provider in self.PROVIDER_MAP:
            api_key = (
                elevenlabs_api_key if fallback_provider == "elevenlabs" else openai_api_key
            )
            try:
                self.fallback_provider = self.PROVIDER_MAP[fallback_provider](api_key)
                if not self.fallback_provider.is_available():
                    logger.debug(f"Fallback TTS provider {fallback_provider} not available")
                    self.fallback_provider = None
            except Exception as e:
                logger.warning(f"Failed to initialize fallback TTS provider: {e}")

    def is_available(self) -> bool:
        """Check if any TTS provider is available."""
        return (
            (self.primary_provider is not None and self.primary_provider.is_available())
            or (self.fallback_provider is not None and self.fallback_provider.is_available())
        )

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
    ) -> TTSResponse:
        """
        Generate speech with automatic fallback.

        Args:
            text: Text to convert to speech
            voice: Voice ID (provider-specific)
            model: TTS model (provider-specific)

        Returns:
            TTSResponse with audio data

        Raises:
            Exception: If all providers fail
        """
        # Try primary provider
        if self.primary_provider and self.primary_provider.is_available():
            try:
                return await self.primary_provider.generate_speech(text, voice, model)
            except Exception as e:
                logger.warning(f"Primary TTS provider failed: {e}")

        # Try fallback provider
        if self.fallback_provider and self.fallback_provider.is_available():
            try:
                logger.info("Falling back to secondary TTS provider")
                return await self.fallback_provider.generate_speech(text, voice, model)
            except Exception as e:
                logger.error(f"Fallback TTS provider also failed: {e}")
                raise

        raise Exception("No TTS providers available")

    async def stream_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncIterator[bytes]:
        """
        Stream speech with automatic fallback.

        Args:
            text: Text to convert to speech
            voice: Voice ID (provider-specific)
            model: TTS model (provider-specific)

        Yields:
            Audio chunk bytes

        Raises:
            Exception: If all providers fail
        """
        # Try primary provider
        if self.primary_provider and self.primary_provider.is_available():
            try:
                async for chunk in self.primary_provider.stream_speech(text, voice, model):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"Primary TTS provider streaming failed: {e}")

        # Try fallback provider
        if self.fallback_provider and self.fallback_provider.is_available():
            try:
                logger.info("Falling back to secondary TTS provider for streaming")
                async for chunk in self.fallback_provider.stream_speech(text, voice, model):
                    yield chunk
                return
            except Exception as e:
                logger.error(f"Fallback TTS provider streaming also failed: {e}")
                raise

        raise Exception("No TTS providers available")

    async def list_voices(self, provider: Optional[str] = None) -> list[dict]:
        """
        List available voices.

        Args:
            provider: Specific provider to query (or None for primary)

        Returns:
            List of voice dictionaries
        """
        if provider:
            if provider == "elevenlabs" and isinstance(
                self.primary_provider, ElevenLabsTTSProvider
            ):
                return await self.primary_provider.list_voices()
            elif provider == "elevenlabs" and isinstance(
                self.fallback_provider, ElevenLabsTTSProvider
            ):
                return await self.fallback_provider.list_voices()
            elif provider == "openai" and isinstance(
                self.primary_provider, OpenAITTSProvider
            ):
                return await self.primary_provider.list_voices()
            elif provider == "openai" and isinstance(
                self.fallback_provider, OpenAITTSProvider
            ):
                return await self.fallback_provider.list_voices()

        # Return from first available provider
        if self.primary_provider and self.primary_provider.is_available():
            return await self.primary_provider.list_voices()
        if self.fallback_provider and self.fallback_provider.is_available():
            return await self.fallback_provider.list_voices()

        return []


# Singleton instance for convenience
_tts_manager: Optional[TTSManager] = None


def get_tts_manager(**kwargs) -> TTSManager:
    """
    Get or create the global TTS manager.

    Args:
        **kwargs: Arguments passed to TTSManager on first creation

    Returns:
        TTSManager instance
    """
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager(**kwargs)
    return _tts_manager
