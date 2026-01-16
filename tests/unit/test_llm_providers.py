"""Tests for LLM providers."""

import pytest
from unittest.mock import Mock, patch

from shared_ai_utils.llm import LLMProvider, LLMResponse, AnthropicProvider, OpenAIProvider
from shared_ai_utils.llm.manager import LLMManager


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_llm_response_creation(self):
        """Test creating LLMResponse."""
        response = LLMResponse(
            text="Hello, world!",
            model="test-model",
            provider="test",
            tokens_used=100,
        )
        assert response.text == "Hello, world!"
        assert response.model == "test-model"
        assert response.provider == "test"
        assert response.tokens_used == 100
        assert isinstance(response.metadata, dict)

    def test_llm_response_default_metadata(self):
        """Test LLMResponse with default metadata."""
        response = LLMResponse(
            text="Test",
            model="test",
            provider="test",
        )
        assert response.metadata == {}


class TestLLMProvider:
    """Test LLMProvider base class."""

    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = Mock(spec=LLMProvider)
        provider.api_key = "test-key"
        provider.model = "test-model"
        provider.base_url = None

        assert provider.api_key == "test-key"
        assert provider.model == "test-model"


class TestAnthropicProvider:
    """Test AnthropicProvider."""

    def test_provider_name(self):
        """Test provider name."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = AnthropicProvider()
            assert provider.provider_name == "anthropic"

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("shared_ai_utils.llm.providers.anthropic"):
                provider = AnthropicProvider()
                assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        with patch.dict("os.environ", {}, clear=True):
            provider = AnthropicProvider(api_key=None)
            assert provider.is_available() is False

    @pytest.mark.asyncio
    async def test_complete(self):
        """Test completion generation."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("shared_ai_utils.llm.providers.anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_message = Mock()
                mock_message.content = [Mock(text="Test response")]
                mock_message.usage = Mock(input_tokens=10, output_tokens=20)
                mock_client.messages.create.return_value = mock_message
                mock_anthropic.Anthropic.return_value = mock_client

                provider = AnthropicProvider()
                response = await provider.complete(
                    system_prompt="You are a helpful assistant",
                    user_prompt="Hello",
                )

                assert isinstance(response, LLMResponse)
                assert response.text == "Test response"
                assert response.provider == "anthropic"
                assert response.tokens_used == 30


class TestLLMManager:
    """Test LLMManager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        with patch("shared_ai_utils.llm.manager.AnthropicProvider") as mock_anthropic, \
             patch("shared_ai_utils.llm.manager.OpenAIProvider") as mock_openai:
            mock_anthropic.return_value.is_available.return_value = False
            mock_openai.return_value.is_available.return_value = False

            manager = LLMManager()
            assert manager.preferred_provider == "anthropic"

    def test_list_available_providers(self):
        """Test listing available providers."""
        with patch("shared_ai_utils.llm.manager.AnthropicProvider") as mock_anthropic:
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_provider.provider_name = "anthropic"
            mock_anthropic.return_value = mock_provider

            manager = LLMManager()
            providers = manager.list_available_providers()
            assert "anthropic" in providers

    @pytest.mark.asyncio
    async def test_generate_with_fallback(self):
        """Test generation with fallback."""
        with patch("shared_ai_utils.llm.manager.AnthropicProvider") as mock_anthropic, \
             patch("shared_ai_utils.llm.manager.OpenAIProvider") as mock_openai:
            # First provider fails
            mock_anthropic_provider = Mock()
            mock_anthropic_provider.is_available.return_value = True
            mock_anthropic_provider.provider_name = "anthropic"
            mock_anthropic_provider.complete.side_effect = Exception("Failed")

            # Second provider succeeds
            mock_openai_provider = Mock()
            mock_openai_provider.is_available.return_value = True
            mock_openai_provider.provider_name = "openai"
            mock_openai_provider.complete.return_value = LLMResponse(
                text="Success",
                model="gpt-4",
                provider="openai",
            )

            mock_anthropic.return_value = mock_anthropic_provider
            mock_openai.return_value = mock_openai_provider

            manager = LLMManager(preferred_provider="anthropic")
            response = await manager.generate(
                system_prompt="Test",
                user_prompt="Hello",
                fallback=True,
            )

            assert response.text == "Success"
            assert response.provider == "openai"
