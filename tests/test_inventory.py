"""
Unit tests for deterministic inventory intelligence.
"""

import pytest
from src.config import Config
from src.data_loader import get_data_loader
from src.inventory import InventoryAnalyzer


@pytest.fixture
def analyzer():
    loader = get_data_loader()
    return InventoryAnalyzer(loader)


def test_inventory_metrics_calculation(analyzer):
    metrics = analyzer.calculate_metrics_for_pair("P101", "S101")
    assert metrics is not None
    assert metrics.product_id == "P101"
    assert metrics.store_id == "S101"
    assert metrics.current_stock >= 0
    assert metrics.avg_daily_sales >= 0


def test_stockout_risk_detection(analyzer):
    # P101 at S101 is curated as high stockout risk
    metrics = analyzer.calculate_metrics_for_pair("P101", "S101")
    assert metrics is not None
    assert metrics.stockout_risk == "HIGH"
    assert metrics.days_remaining is not None
    assert metrics.days_remaining <= Config.STOCKOUT_DAYS_THRESHOLD


def test_zero_sales_division_by_zero_safety(analyzer):
    # P145 at S104 has zero sales in last 30 days
    metrics = analyzer.calculate_metrics_for_pair("P145", "S104")
    assert metrics is not None
    assert metrics.avg_daily_sales == 0
    assert metrics.days_remaining is None
    assert metrics.days_remaining_str == "N/A (No Recent Sales)"
    assert metrics.non_moving_status is True


def test_overstock_detection(analyzer):
    # P115 at S102 is curated as overstocked
    metrics = analyzer.calculate_metrics_for_pair("P115", "S102")
    assert metrics is not None
    assert metrics.overstock_status is True
