"""
Unit tests for evidence-grounded recommendations.
"""

import pytest
from src.data_loader import get_data_loader
from src.inventory import InventoryAnalyzer
from src.recommendations import RecommendationEngine


@pytest.fixture
def analyzer():
    loader = get_data_loader()
    return InventoryAnalyzer(loader)


def test_recommendation_from_stockout(analyzer):
    metrics = analyzer.calculate_metrics_for_pair("P101", "S101")
    assert metrics is not None
    rec = RecommendationEngine.from_inventory_metrics(metrics)
    assert rec is not None
    assert rec.action_type == "REORDER"
    assert rec.severity == "HIGH"
    assert "Wireless Mouse" in rec.title
    assert "below the configured" in rec.why_reason
    assert rec.evidence.rule_source == "Application business rule"
