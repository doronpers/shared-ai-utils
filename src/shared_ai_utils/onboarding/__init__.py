"""
Unified Onboarding System

Provides a unified onboarding experience across all Sonotheia ecosystem repositories.
"""

from shared_ai_utils.onboarding.intent_detector import IntentDetector, IntentResult
from shared_ai_utils.onboarding.unified_setup import UnifiedOnboarding
from shared_ai_utils.onboarding.verification import SetupVerifier, VerificationResult
from shared_ai_utils.onboarding.setup_wizards.base import BaseSetupWizard

__all__ = [
    "UnifiedOnboarding",
    "IntentDetector",
    "IntentResult",
    "SetupVerifier",
    "VerificationResult",
    "BaseSetupWizard",
]
