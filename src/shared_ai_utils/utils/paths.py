"""
Workspace-relative path resolution utilities.

This module provides functions to resolve workspace-relative configuration
and data directories, avoiding writes to user home directories.
"""

import os
from pathlib import Path
from typing import Optional


def find_workspace_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Find the workspace root directory.

    Looks for the workspace root by checking for:
    - `.workspace-config/` directory
    - `.git/` directory with parent named "Gits" (workspace root marker)

    Args:
        start_path: Path to start searching from (defaults to current working directory)

    Returns:
        Path to workspace root, or None if not found
    """
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    while current != current.parent:
        # Check for workspace config directory
        if (current / ".workspace-config").exists():
            return current

        # Check for workspace root marker (Gits directory with .git)
        if current.name == "Gits" and (current / ".git").exists():
            return current

        current = current.parent

    return None


def get_workspace_config_dir(app_name: Optional[str] = None) -> Path:
    """Get workspace-relative config directory.

    Args:
        app_name: Optional application name for subdirectory (e.g., "council-ai")

    Returns:
        Path to workspace config directory (or subdirectory if app_name provided)
    """
    workspace_root = find_workspace_root()

    if workspace_root is None:
        # Fallback: use current directory
        workspace_root = Path.cwd()
        # Create .workspace-config if it doesn't exist
        config_dir = workspace_root / ".workspace-config"
        config_dir.mkdir(exist_ok=True)

    config_dir = workspace_root / ".workspace-config"

    if app_name:
        return config_dir / app_name

    return config_dir


def get_workspace_data_dir(app_name: str, subdirectory: Optional[str] = None) -> Path:
    """Get workspace-relative data directory for an application.

    Args:
        app_name: Application name (e.g., "council-ai")
        subdirectory: Optional subdirectory within app's data directory

    Returns:
        Path to data directory
    """
    base_dir = get_workspace_config_dir(app_name)

    if subdirectory:
        return base_dir / subdirectory

    return base_dir


def get_config_path(
    app_name: str,
    filename: str = "config.yaml",
    fallback_home: bool = False,
) -> Path:
    """Get configuration file path with fallback options.

    Args:
        app_name: Application name
        filename: Configuration filename
        fallback_home: If True, fallback to home directory if workspace not found

    Returns:
        Path to configuration file
    """
    # Try workspace first
    workspace_root = find_workspace_root()
    if workspace_root:
        return get_workspace_config_dir(app_name) / filename

    # Fallback to home directory if requested
    if fallback_home:
        from pathlib import Path as PathLib

        return PathLib.home() / ".config" / app_name / filename

    # Default: workspace-relative even if workspace not found
    return get_workspace_config_dir(app_name) / filename
