"""
LLM Provider Abstractions

Unified async-first interface for multiple LLM providers.
Combines council-ai's async interface with feedback-loop's token tracking.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Unified response from any LLM provider with token tracking."""

    text: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure metadata is a dict."""
        if not isinstance(self.metadata, dict):
            self.metadata = {}


class ModelParameterSpec(BaseModel):
    """Supported generation parameter specification."""

    name: str
    type: str = Field(..., description="Parameter type (int, float, string)")
    min: Optional[float] = None
    max: Optional[float] = None
    default: Optional[float] = None
    description: Optional[str] = None


class ModelInfo(BaseModel):
    """Model capability information for a provider."""

    provider: str
    default_model: Optional[str] = None
    models: list[str] = Field(default_factory=list)
    parameters: list[ModelParameterSpec] = Field(default_factory=list)


class LLMProvider(ABC):
    """Abstract base class for LLM providers (async-first)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize provider.

        Args:
            api_key: API key for the provider
            model: Model name to use (provider-specific)
            base_url: Base URL for API (optional, for custom endpoints)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/query
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)

        Returns:
            LLMResponse with generated text and token usage
        """
        pass

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Stream a completion token by token.

        Default implementation collects stream and yields chunks.
        Providers should override for true streaming.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/query
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Yields:
            Text chunks as they arrive
        """
        result = await self.complete(system_prompt, user_prompt, max_tokens, temperature)
        # Yield in chunks for default implementation
        chunk_size = 10
        for i in range(0, len(result.text), chunk_size):
            yield result.text[i : i + chunk_size]

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """
        Generate a structured completion following a JSON schema.

        Default implementation uses complete() and parses JSON.
        Providers should override for native structured output support.

        Args:
            system_prompt: System prompt/instructions
            user_prompt: User prompt/query
            json_schema: JSON schema to follow
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Parsed JSON dict matching the schema
        """
        # Add schema instruction to prompt
        schema_instruction = (
            f"\n\nRespond with valid JSON matching this schema: {json.dumps(json_schema, indent=2)}"
        )
        enhanced_prompt = user_prompt + schema_instruction

        result = await self.complete(system_prompt, enhanced_prompt, max_tokens, temperature)

        # Try to parse JSON from response
        try:
            text = result.text
            # Extract JSON from markdown code blocks if present
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            elif "```" in text:
                json_start = text.find("```") + 3
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()

            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON object
            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", result.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse structured JSON from response: {result.text[:200]}")

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available (API key set, package installed).

        Returns:
            True if provider can be used
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name (e.g., 'anthropic', 'openai')."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Anthropic provider."""
        super().__init__(
            api_key or os.environ.get("ANTHROPIC_API_KEY"),
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY or pass api_key.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using Anthropic."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        def _call() -> tuple[str, int, int]:
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            text = message.content[0].text
            return text, input_tokens, output_tokens

        text, input_tokens, output_tokens = await asyncio.to_thread(_call)

        return LLMResponse(
            text=text,
            model=self.model or self.DEFAULT_MODEL,
            provider="anthropic",
            tokens_used=input_tokens + output_tokens,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using Anthropic."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        async with client.messages.stream(
            model=self.model or self.DEFAULT_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for text_block in stream.text_stream:
                yield text_block

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """Generate structured completion using Anthropic."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Install with: pip install anthropic"
            )

        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        # Anthropic supports response_format for structured output
        try:
            message = await client.messages.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                response_format={"type": "json_object"},
            )
            result_text = message.content[0].text
            return json.loads(result_text)
        except Exception as e:
            # Fallback to base implementation
            logger.debug(f"Anthropic structured output failed, falling back to base: {e}")
            return await super().complete_structured(
                system_prompt, user_prompt, json_schema, max_tokens, temperature
            )

    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        try:
            import anthropic  # noqa: F401
            return self.api_key is not None
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        return "anthropic"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider (also supports Vercel AI Gateway)."""

    DEFAULT_MODEL = "gpt-4-turbo-preview"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize OpenAI provider."""
        # Try OpenAI key first, then Vercel AI Gateway key
        resolved_key = (
            api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_GATEWAY_API_KEY")
        )

        # If using Vercel AI Gateway, set the base URL
        if (
            not base_url
            and os.environ.get("AI_GATEWAY_API_KEY")
            and not os.environ.get("OPENAI_API_KEY")
        ):
            base_url = (
                base_url or os.environ.get("VERCEL_AI_GATEWAY_URL") or "https://api.vercel.ai/v1"
            )

        super().__init__(
            resolved_key,
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY, AI_GATEWAY_API_KEY, or pass api_key."
            )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using OpenAI."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        def _call() -> tuple[str, Optional[int], Optional[int]]:
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            client = openai.OpenAI(**client_kwargs)
            response = client.chat.completions.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = response.choices[0].message.content
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else None
            output_tokens = usage.completion_tokens if usage else None
            return text, input_tokens, output_tokens

        text, input_tokens, output_tokens = await asyncio.to_thread(_call)
        total_tokens = (input_tokens + output_tokens) if (input_tokens and output_tokens) else None

        return LLMResponse(
            text=text,
            model=self.model or self.DEFAULT_MODEL,
            provider="openai",
            tokens_used=total_tokens,
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using OpenAI."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = openai.AsyncOpenAI(**client_kwargs)

        stream = await client.chat.completions.create(
            model=self.model or self.DEFAULT_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def complete_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        json_schema: dict,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> dict:
        """Generate structured completion using OpenAI."""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = openai.AsyncOpenAI(**client_kwargs)

        try:
            # OpenAI supports response_format for JSON mode
            response = await client.chat.completions.create(
                model=self.model or self.DEFAULT_MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            result_text = response.choices[0].message.content
            return json.loads(result_text)
        except Exception as e:
            # Fallback to base implementation
            logger.debug(f"OpenAI structured output failed, falling back to base: {e}")
            return await super().complete_structured(
                system_prompt, user_prompt, json_schema, max_tokens, temperature
            )

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            import openai  # noqa: F401
            return self.api_key is not None
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        return "openai"


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    DEFAULT_MODEL = "gemini-pro"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize Gemini provider."""
        # Check GEMINI_API_KEY first, then fall back to GOOGLE_API_KEY
        env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        super().__init__(
            api_key or env_key,
            model=model,
            base_url=base_url,
        )
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY or pass api_key.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using Google Gemini."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            )

        def _call() -> str:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model or self.DEFAULT_MODEL)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return response.text

        text = await asyncio.to_thread(_call)

        # Gemini doesn't always provide token counts
        return LLMResponse(
            text=text,
            model=self.model or self.DEFAULT_MODEL,
            provider="gemini",
            tokens_used=None,
            metadata={},
        )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using Google Gemini."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model or self.DEFAULT_MODEL)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Gemini streaming - need to use async wrapper
        def _stream():
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
                stream=True,
            )
            return response

        response = await asyncio.to_thread(_stream)

        # Yield chunks as they arrive
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def is_available(self) -> bool:
        """Check if Gemini is available."""
        if self.api_key is None:
            return False
        try:
            import google.generativeai  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        return "gemini"


class HTTPProvider(LLMProvider):
    """Custom HTTP endpoint provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize HTTP provider."""
        resolved_api_key = (
            api_key or os.environ.get("HTTP_API_KEY") or os.environ.get("COUNCIL_API_KEY")
        )
        super().__init__(resolved_api_key, model=model, base_url=base_url)
        self.endpoint = endpoint or base_url or os.environ.get("LLM_ENDPOINT")
        if not self.endpoint:
            raise ValueError("HTTP endpoint required. Set LLM_ENDPOINT or pass endpoint.")

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a completion using custom HTTP endpoint."""
        import httpx

        async with httpx.AsyncClient() as client:
            payload = {
                "system": system_prompt,
                "prompt": user_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if self.model:
                payload["model"] = self.model
            response = await client.post(
                self.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            completion = result.get("completion", result.get("text", ""))
            return LLMResponse(
                text=completion,
                model=self.model or "custom",
                provider="http",
                tokens_used=result.get("tokens_used"),
                metadata=result.get("metadata", {}),
            )

    async def stream_complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Stream a completion using custom HTTP endpoint (SSE or chunked)."""
        import httpx

        async with httpx.AsyncClient() as client:
            payload = {
                "system": system_prompt,
                "prompt": user_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True,
            }
            if self.model:
                payload["model"] = self.model
            async with client.stream(
                "POST",
                self.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        # Try to parse SSE format or JSON chunks
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                yield data.get("text", data.get("content", ""))
                            except json.JSONDecodeError:
                                yield line[6:]
                        else:
                            yield line

    def is_available(self) -> bool:
        """Check if HTTP provider is available (endpoint configured)."""
        return self.endpoint is not None

    @property
    def provider_name(self) -> str:
        return "http"
