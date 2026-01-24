"""
CLI Framework

Rich terminal utilities and interactive wizards for command-line interfaces.
"""

from shared_ai_utils.cli.base import BaseCLI
from shared_ai_utils.cli.docs import docs
from shared_ai_utils.cli.extensions import AssessmentCLI, PatternCLI, SensorCLI
# Note: onboard imported lazily below to avoid circular dependency
from shared_ai_utils.cli.rich_utils import (
    format_score,
    print_error,
    print_info,
    print_json,
    print_success,
    print_table,
    print_warning,
)
from shared_ai_utils.cli.wizards import SetupWizard, Wizard, WizardStep

# Lazy import to avoid circular dependency: cli -> onboarding -> cli
def _get_onboard():
    """Lazy import of onboard to avoid circular dependency."""
    from shared_ai_utils.cli.onboarding import onboard as _onboard
    return _onboard

def onboard(*args, **kwargs):
    """Onboard function - lazy import wrapper to avoid circular dependency."""
    return _get_onboard()(*args, **kwargs)

__all__ = [
    "BaseCLI",
    "AssessmentCLI",
    "SensorCLI",
    "PatternCLI",
    "onboard",
    "docs",
    "print_table",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "print_json",
    "format_score",
    "Wizard",
    "WizardStep",
    "SetupWizard",
]
