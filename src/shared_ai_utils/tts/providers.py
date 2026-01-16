"""
Text-to-Speech (TTS) Provider Abstractions

Unified async-first interface for multiple TTS providers (ElevenLabs, OpenAI)
with automatic fallback support.

Extracted from council-ai for cross-project reuse.
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class TTSResponse:
    """Unified response from any TTS provider."""

    audio_data: bytes
    format: str = "mp3"
    provider: str = ""
    voice: str = ""
    model: str = ""
    duration_seconds: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TTSProvider(ABC):
    """Abstract base class for TTS providers (async-first)."""

    @abstractmethod
    async def generate_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> TTSResponse:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice ID or name
            model: TTS model to use

        Returns:
            TTSResponse with audio bytes in MP3 format
        """
        pass

    @abstractmethod
    async def stream_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        Stream speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice ID or name
            model: TTS model to use

        Yields:
            Audio chunk bytes
        """
        pass

    @abstractmethod
    async def list_voices(self) -> list[dict]:
        """
        List available voices.

        Returns:
            List of voice dictionaries with 'id', 'name', and optional metadata
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available (API key set)."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (e.g., 'elevenlabs', 'openai')."""
        pass


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS provider implementation."""

    DEFAULT_VOICE = "EXAVITQu4vr4xnSDxMaL"  # Sarah voice
    DEFAULT_MODEL = "eleven_turbo_v2_5"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ElevenLabs provider.

        Args:
            api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"

    def is_available(self) -> bool:
        """Check if ElevenLabs API key is configured."""
        return bool(self.api_key)

    @property
    def provider_name(self) -> str:
        return "elevenlabs"

    async def generate_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> TTSResponse:
        """Generate speech using ElevenLabs API."""
        if not self.is_available():
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY environment variable."
            )

        voice = voice or self.DEFAULT_VOICE
        model = model or self.DEFAULT_MODEL

        url = f"{self.base_url}/text-to-speech/{voice}"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                if response.status_code != 200:
                    logger.error(f"ElevenLabs TTS error: {response.text}")
                    raise Exception(f"ElevenLabs API error: {response.status_code}")

                return TTSResponse(
                    audio_data=response.content,
                    format="mp3",
                    provider=self.provider_name,
                    voice=voice,
                    model=model,
                )
        except Exception as e:
            logger.error(f"ElevenLabs TTS generation failed: {e}")
            raise

    async def stream_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """Stream speech using ElevenLabs API."""
        if not self.is_available():
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY environment variable."
            )

        voice = voice or self.DEFAULT_VOICE
        model = model or self.DEFAULT_MODEL

        url = f"{self.base_url}/text-to-speech/{voice}/stream"
        headers = {"xi-api-key": self.api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", url, json=payload, headers=headers, timeout=30.0
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"ElevenLabs TTS streaming error: {error_text}")
                        raise Exception(f"ElevenLabs API error: {response.status_code}")

                    async for chunk in response.aiter_bytes(chunk_size=4096):
                        if chunk:
                            yield chunk
        except Exception as e:
            logger.error(f"ElevenLabs TTS streaming failed: {e}")
            raise

    async def list_voices(self) -> list[dict]:
        """List available ElevenLabs voices."""
        if not self.is_available():
            return self._get_default_voices()

        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10.0)
                if response.status_code != 200:
                    logger.error(f"Failed to list ElevenLabs voices: {response.status_code}")
                    return self._get_default_voices()

                data = response.json()
                voices = []
                for voice in data.get("voices", []):
                    voices.append(
                        {
                            "id": voice["voice_id"],
                            "name": voice["name"],
                            "category": voice.get("category", "premade"),
                            "labels": voice.get("labels", {}),
                        }
                    )
                return voices
        except Exception as e:
            logger.error(f"Failed to fetch ElevenLabs voices: {e}")
            return self._get_default_voices()

    def _get_default_voices(self) -> list[dict]:
        """Return default voice options."""
        return [
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "category": "premade"},
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "category": "premade"},
            {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "category": "premade"},
            {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "category": "premade"},
        ]


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS provider implementation (fallback)."""

    DEFAULT_VOICE = "alloy"
    DEFAULT_MODEL = "tts-1"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI TTS provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> TTSResponse:
        """Generate speech using OpenAI TTS API."""
        if not self.is_available():
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable."
            )

        voice = voice or self.DEFAULT_VOICE
        model = model or self.DEFAULT_MODEL

        url = f"{self.base_url}/audio/speech"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "input": text, "voice": voice, "response_format": "mp3"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=30.0)
                if response.status_code != 200:
                    logger.error(f"OpenAI TTS error: {response.text}")
                    raise Exception(f"OpenAI API error: {response.status_code}")

                return TTSResponse(
                    audio_data=response.content,
                    format="mp3",
                    provider=self.provider_name,
                    voice=voice,
                    model=model,
                )
        except Exception as e:
            logger.error(f"OpenAI TTS generation failed: {e}")
            raise

    async def stream_speech(
        self, text: str, voice: Optional[str] = None, model: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        Stream speech using OpenAI TTS API.
        Note: OpenAI doesn't support true streaming, so we generate and chunk the response.
        """
        tts_response = await self.generate_speech(text, voice, model)

        # Chunk the audio data for pseudo-streaming
        chunk_size = 4096
        audio_data = tts_response.audio_data
        for i in range(0, len(audio_data), chunk_size):
            yield audio_data[i : i + chunk_size]
            await asyncio.sleep(0.01)  # Small delay to simulate streaming

    async def list_voices(self) -> list[dict]:
        """List available OpenAI voices."""
        # OpenAI voices are hardcoded in their API
        return [
            {"id": "alloy", "name": "Alloy", "description": "Neutral and balanced"},
            {"id": "echo", "name": "Echo", "description": "Male voice"},
            {"id": "fable", "name": "Fable", "description": "British accent"},
            {"id": "onyx", "name": "Onyx", "description": "Deep and authoritative"},
            {"id": "nova", "name": "Nova", "description": "Friendly female"},
            {"id": "shimmer", "name": "Shimmer", "description": "Warm and expressive"},
        ]
