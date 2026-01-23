"""Analytics dashboard templates for cross-repo usage."""

from shared_ai_utils.analytics.dashboards import (
    create_assessment_dashboard_config,
    create_pattern_dashboard_config,
    create_sensor_dashboard_config,
    create_unified_dashboard_config,
)

__all__ = [
    "create_unified_dashboard_config",
    "create_assessment_dashboard_config",
    "create_sensor_dashboard_config",
    "create_pattern_dashboard_config",
]
