"""Tests for TTS (Text-to-Speech) providers and manager."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from shared_ai_utils.tts import (
    TTSProvider,
    TTSResponse,
    ElevenLabsTTSProvider,
    OpenAITTSProvider,
    TTSManager,
)


class TestTTSResponse:
    """Test TTSResponse dataclass."""

    def test_tts_response_creation(self):
        """Test creating TTSResponse."""
        response = TTSResponse(
            audio_data=b"fake_audio_data",
            format="mp3",
            provider="elevenlabs",
            model="eleven_multilingual_v2",
        )
        assert response.audio_data == b"fake_audio_data"
        assert response.format == "mp3"
        assert response.provider == "elevenlabs"
        assert response.model == "eleven_multilingual_v2"


class TestElevenLabsTTSProvider:
    """Test ElevenLabsTTSProvider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = ElevenLabsTTSProvider(api_key="test-key")
        assert provider.provider_name == "elevenlabs"

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        provider = ElevenLabsTTSProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        provider = ElevenLabsTTSProvider(api_key=None)
        assert provider.is_available() is False

    @pytest.mark.asyncio
    async def test_generate_speech(self):
        """Test text synthesis."""
        provider = ElevenLabsTTSProvider(api_key="test-key")
        
        with patch("shared_ai_utils.tts.providers.httpx") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"fake_audio_data"
            mock_async_client = AsyncMock()
            mock_async_client.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            mock_httpx.AsyncClient.return_value = mock_async_client

            response = await provider.generate_speech("Hello, world!")

            assert isinstance(response, TTSResponse)
            assert response.audio_data == b"fake_audio_data"
            assert response.provider == "elevenlabs"


class TestOpenAITTSProvider:
    """Test OpenAITTSProvider."""

    def test_provider_name(self):
        """Test provider name."""
        provider = OpenAITTSProvider(api_key="test-key")
        assert provider.provider_name == "openai"

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        provider = OpenAITTSProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        provider = OpenAITTSProvider(api_key=None)
        assert provider.is_available() is False


class TestTTSManager:
    """Test TTSManager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = TTSManager()
        assert manager.primary_provider is not None or manager.fallback_provider is not None

    def test_is_available(self):
        """Test availability check."""
        manager = TTSManager()
        # May or may not be available depending on API keys
        assert isinstance(manager.is_available(), bool)

    @pytest.mark.asyncio
    async def test_generate_speech_with_fallback(self):
        """Test speech generation with fallback."""
        # Create manager with mocked providers
        with patch("shared_ai_utils.tts.manager.ElevenLabsTTSProvider") as mock_elevenlabs_class, \
             patch("shared_ai_utils.tts.manager.OpenAITTSProvider") as mock_openai_class:
            
            mock_elevenlabs = Mock()
            mock_elevenlabs.is_available.return_value = False
            mock_elevenlabs_class.return_value = mock_elevenlabs
            
            mock_openai = Mock()
            mock_openai.is_available.return_value = True
            mock_openai.generate_speech = AsyncMock(return_value=TTSResponse(
                audio_data=b"audio",
                format="mp3",
                provider="openai",
            ))
            mock_openai_class.return_value = mock_openai

            manager = TTSManager(primary_provider="elevenlabs", fallback_provider="openai")
            response = await manager.generate_speech("Hello")

            assert response.provider == "openai"
            assert response.audio_data == b"audio"
