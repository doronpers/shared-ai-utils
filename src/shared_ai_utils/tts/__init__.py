"""
Text-to-Speech (TTS) Utilities

Unified async-first interface for multiple TTS providers with automatic fallback.
Supports ElevenLabs and OpenAI TTS.
"""

from .providers import (
    TTSProvider,
    TTSResponse,
    ElevenLabsTTSProvider,
    OpenAITTSProvider,
)
from .manager import TTSManager, get_tts_manager

__all__ = [
    "TTSProvider",
    "TTSResponse",
    "ElevenLabsTTSProvider",
    "OpenAITTSProvider",
    "TTSManager",
    "get_tts_manager",
]
