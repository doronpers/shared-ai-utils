"""
Insights Engine Module

Generates actionable insights, recommendations, and trends from metrics data.
Provides intelligent analysis for analytics dashboards.

This module is designed to be generic and work with any metrics data source
that provides pattern effectiveness, frequency, and severity information.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Protocol


class MetricsAnalyzerProtocol(Protocol):
    """Protocol for metrics analyzer compatibility."""

    metrics_data: Dict[str, Any]

    def calculate_effectiveness(self) -> Dict[str, Dict[str, Any]]:
        ...

    def get_high_frequency_patterns(self, threshold: int) -> List[Dict[str, Any]]:
        ...

    def get_severity_distribution(self) -> Dict[str, int]:
        ...

    def get_summary(self) -> Dict[str, Any]:
        ...


class InsightsEngine:
    """Engine for generating insights and recommendations from metrics."""

    def __init__(self, analyzer: Optional[MetricsAnalyzerProtocol] = None):
        """Initialize insights engine.

        Args:
            analyzer: Metrics analyzer instance (must implement MetricsAnalyzerProtocol)
        """
        self.analyzer = analyzer

    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate actionable insights from metrics data.

        Returns:
            List of insight dictionaries
        """
        if not self.analyzer:
            return [
                {
                    "title": "No Metrics Data",
                    "description": "Provide a metrics analyzer to generate insights.",
                    "type": "info",
                    "impact": "Connect a data source to unlock insights",
                }
            ]

        insights = []

        # Pattern effectiveness insights
        effectiveness = self.analyzer.calculate_effectiveness()
        if effectiveness:
            sorted_patterns = sorted(effectiveness.items(), key=lambda x: x[1]["score"])

            if sorted_patterns:
                # Best performing pattern
                best_pattern, best_metrics = sorted_patterns[-1]
                insights.append(
                    {
                        "title": f"🏆 Top Performing Pattern: {best_pattern}",
                        "description": (
                            f"Pattern '{best_pattern}' has {best_metrics['score']:.1%} "
                            f"effectiveness with {best_metrics['trend']} trend."
                        ),
                        "type": "success",
                        "impact": "Continue applying this pattern - it's working well",
                    }
                )

                # Worst performing pattern (if score < 50%)
                worst_pattern, worst_metrics = sorted_patterns[0]
                if worst_metrics["score"] < 0.5:
                    insights.append(
                        {
                            "title": f"⚠️ Low Effectiveness: {worst_pattern}",
                            "description": (
                                f"Pattern '{worst_pattern}' only has "
                                f"{worst_metrics['score']:.1%} effectiveness."
                            ),
                            "type": "warning",
                            "impact": "Review and update this pattern",
                        }
                    )

        # High frequency patterns
        high_freq = self.analyzer.get_high_frequency_patterns(threshold=3)
        if high_freq:
            top_pattern = high_freq[0]
            insights.append(
                {
                    "title": f"🔄 High Frequency Pattern: {top_pattern['pattern']}",
                    "description": (
                        f"Pattern '{top_pattern['pattern']}' occurs "
                        f"{top_pattern['count']} times."
                    ),
                    "type": "info",
                    "impact": "Consider automating detection for this pattern",
                }
            )

        # Severity insights
        severity_ranking = self.analyzer.get_severity_distribution()
        if severity_ranking.get("high", 0) > severity_ranking.get("low", 0):
            insights.append(
                {
                    "title": "🚨 High Severity Issues Detected",
                    "description": (
                        f"Found {severity_ranking.get('high', 0)} high-severity issues."
                    ),
                    "type": "danger",
                    "impact": "Address high-severity issues to improve reliability",
                }
            )

        return insights

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations.

        Returns:
            List of recommendation dictionaries
        """
        if not self.analyzer:
            return [
                {
                    "action": "Connect Metrics Source",
                    "description": "Provide a metrics analyzer to generate recommendations",
                    "priority": "high",
                    "effort": "low",
                }
            ]

        recommendations = []

        # Pattern-based recommendations
        high_freq = self.analyzer.get_high_frequency_patterns(threshold=2)
        if high_freq:
            recommendations.append(
                {
                    "action": f"Automate {high_freq[0]['pattern']} Detection",
                    "description": "Create automated checks for this frequently occurring pattern",
                    "priority": "high",
                    "effort": "medium",
                }
            )

        # Effectiveness-based recommendations
        effectiveness = self.analyzer.calculate_effectiveness()
        if effectiveness:
            low_effective = [p for p, m in effectiveness.items() if m["score"] < 0.6]
            if low_effective:
                recommendations.append(
                    {
                        "action": "Review Low-Effectiveness Patterns",
                        "description": f"Update patterns: {', '.join(low_effective[:3])}",
                        "priority": "medium",
                        "effort": "high",
                    }
                )

        return recommendations

    def calculate_pattern_roi(self, pattern_name: str) -> Dict[str, Any]:
        """Calculate return on investment for a pattern.

        Args:
            pattern_name: Name of the pattern

        Returns:
            ROI analysis dictionary
        """
        if not self.analyzer:
            return {"error": "No metrics data available"}

        effectiveness = self.analyzer.calculate_effectiveness()
        pattern_effectiveness = effectiveness.get(pattern_name, {})

        if not pattern_effectiveness:
            return {"error": f"Pattern '{pattern_name}' not found"}

        total_occurrences = pattern_effectiveness.get("total_occurrences", 0)
        effectiveness_score = pattern_effectiveness.get("score", 0.5)
        occurrences_prevented = int(total_occurrences * effectiveness_score * 0.5)

        base_cost_minutes = 10
        time_saved_per_occurrence = 5
        time_saved = occurrences_prevented * time_saved_per_occurrence

        return {
            "pattern": pattern_name,
            "implementation_cost_minutes": base_cost_minutes,
            "estimated_occurrences_prevented": occurrences_prevented,
            "estimated_time_saved_minutes": time_saved,
            "roi_ratio": time_saved / base_cost_minutes if base_cost_minutes > 0 else 0,
            "status": "profitable" if time_saved > base_cost_minutes else "not_yet",
        }

    def get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of issue severities.

        Returns:
            Dictionary mapping severity levels to counts
        """
        if not self.analyzer:
            return {"high": 0, "medium": 0, "low": 0}
        return self.analyzer.get_severity_distribution()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard.

        Returns:
            Summary statistics dictionary
        """
        if not self.analyzer:
            return {"total_issues": 0, "avg_effectiveness": 0.0, "top_pattern": None}

        summary = self.analyzer.get_summary()
        effectiveness = self.analyzer.calculate_effectiveness()

        avg_effectiveness = 0.0
        if effectiveness:
            scores = [m["score"] for m in effectiveness.values()]
            avg_effectiveness = sum(scores) / len(scores) if scores else 0.0

        high_freq = self.analyzer.get_high_frequency_patterns(threshold=1)
        top_pattern = high_freq[0]["pattern"] if high_freq else None

        return {
            "total_issues": summary.get("total", 0),
            "avg_effectiveness": avg_effectiveness,
            "top_pattern": top_pattern,
        }
