"""Helper functions for assessment processing."""

from typing import Any, Dict


def extract_text_content(content: Dict[str, Any]) -> str:
    """
    Extract text content from submission dictionary.

    Args:
        content: Submission content dictionary

    Returns:
        String representation of content
    """
    text_parts = []

    # Try common content keys
    for key in ["code", "text", "content", "solution", "submission"]:
        if key in content:
            value = content[key]
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, list):
                text_parts.extend(str(v) for v in value)

    # If no specific key, convert entire content to string
    if not text_parts:
        text_parts.append(str(content))

    return "\n".join(text_parts)
