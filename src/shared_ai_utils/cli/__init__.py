"""
CLI Framework

Rich terminal utilities and interactive wizards for command-line interfaces.
"""

from .base import BaseCLI
from .rich_utils import (
    format_score,
    print_error,
    print_info,
    print_json,
    print_success,
    print_table,
    print_warning,
)
from .wizards import SetupWizard, Wizard, WizardStep

__all__ = [
    "BaseCLI",
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
