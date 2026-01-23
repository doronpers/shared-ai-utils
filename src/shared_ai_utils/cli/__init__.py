"""
CLI Framework

Rich terminal utilities and interactive wizards for command-line interfaces.
"""

from shared_ai_utils.cli.base import BaseCLI
from shared_ai_utils.cli.docs import docs
from shared_ai_utils.cli.extensions import AssessmentCLI, PatternCLI, SensorCLI
from shared_ai_utils.cli.onboarding import onboard
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
