"""
Unit tests for deterministic sales anomaly detection engine.
"""

import pytest
from src.config import Config
from src.data_loader import get_data_loader
from src.anomaly_detection import AnomalyDetector


@pytest.fixture
def detector():
    loader = get_data_loader()
    return AnomalyDetector(loader)


def test_sales_spike_detection(detector):
    # P103 at S101 is curated as a sales spike
    anomaly = detector.detect_anomalies_for_pair("P103", "S101")
    assert anomaly is not None
    assert anomaly.anomaly_type == "SALES_SPIKE"
    assert anomaly.pct_change >= Config.SPIKE_THRESHOLD_PCT
    assert anomaly.recent_daily_avg > anomaly.historical_daily_avg


def test_sales_drop_detection(detector):
    # P125 at S103 is curated as a sales drop
    anomaly = detector.detect_anomalies_for_pair("P125", "S103")
    assert anomaly is not None
    assert anomaly.anomaly_type == "SALES_DROP"
    assert anomaly.pct_change <= Config.DROP_THRESHOLD_PCT
    assert anomaly.recent_daily_avg < anomaly.historical_daily_avg


def test_non_overlapping_windows(detector):
    # Verify non-overlapping window math works without errors
    anomalies = detector.detect_all_anomalies()
    assert isinstance(anomalies, list)
    for a in anomalies:
        assert a.anomaly_type in ["SALES_SPIKE", "SALES_DROP"]
        assert "Application business rule" in a.detection_rule
