"""
Error Recovery Framework

Provides unified error recovery and contextual help across all repositories.
"""

from shared_ai_utils.errors.contextual_help import ContextualHelp, HelpResponse
from shared_ai_utils.errors.formatter import UnifiedErrorFormatter
from shared_ai_utils.errors.recovery import ErrorRecovery, RecoveryStep

__all__ = [
    "ErrorRecovery",
    "RecoveryStep",
    "ContextualHelp",
    "HelpResponse",
    "UnifiedErrorFormatter",
]
