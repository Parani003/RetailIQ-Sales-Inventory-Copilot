"""
Deterministic Sales Anomaly Detection Engine.
Compares recent 7-day sales against a non-overlapping prior 30-day historical baseline.
"""

import pandas as pd
from typing import List, Optional
from src.config import Config
from src.models import SalesAnomaly
from src.data_loader import DataLoader, get_data_loader


class AnomalyDetector:
    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or get_data_loader()

    def detect_anomalies_for_pair(self, product_id: str, store_id: str) -> Optional[SalesAnomaly]:
        product = self.loader.product_map.get(product_id)
        store = self.loader.store_map.get(store_id)
        if not product or not store:
            return None

        df_s = self.loader.df_sales[
            (self.loader.df_sales['product_id'] == product_id) & 
            (self.loader.df_sales['store_id'] == store_id)
        ].sort_values('date')

        if df_s.empty:
            return None

        latest_date = df_s['date'].max()

        # Non-overlapping windows:
        # Recent period: [latest_date - 6 days, latest_date] (7 days total)
        recent_end = latest_date
        recent_start = latest_date - pd.Timedelta(days=Config.RECENT_ANOMALY_WINDOW - 1)

        # Historical baseline: [recent_start - 30 days, recent_start - 1 day] (30 days total, excluding recent period)
        hist_end = recent_start - pd.Timedelta(days=1)
        hist_start = hist_end - pd.Timedelta(days=Config.HISTORICAL_BASELINE_WINDOW - 1)

        df_recent = df_s[(df_s['date'] >= recent_start) & (df_s['date'] <= recent_end)]
        df_hist = df_s[(df_s['date'] >= hist_start) & (df_s['date'] <= hist_end)]

        recent_units = int(df_recent['units_sold'].sum()) if not df_recent.empty else 0
        recent_daily_avg = round(recent_units / float(Config.RECENT_ANOMALY_WINDOW), 2)

        hist_units = int(df_hist['units_sold'].sum()) if not df_hist.empty else 0
        hist_days = float(len(df_hist)) if not df_hist.empty else float(Config.HISTORICAL_BASELINE_WINDOW)
        if hist_days == 0:
            hist_days = 30.0

        hist_daily_avg = round(hist_units / hist_days, 2)
        hist_weekly_baseline = round(hist_daily_avg * 7.0, 2)

        # Percentage change calculation
        if hist_daily_avg > 0:
            pct_change = round(((recent_daily_avg - hist_daily_avg) / hist_daily_avg) * 100.0, 1)
        elif recent_daily_avg > 0:
            pct_change = 999.9  # Spike over zero baseline
        else:
            pct_change = 0.0

        anomaly_type = None
        if pct_change >= Config.SPIKE_THRESHOLD_PCT:
            anomaly_type = "SALES_SPIKE"
        elif pct_change <= Config.DROP_THRESHOLD_PCT:
            anomaly_type = "SALES_DROP"

        if not anomaly_type:
            return None

        rule_text = (
            f"Sales Spike Rule: Change ≥ +{Config.SPIKE_THRESHOLD_PCT}% | "
            f"Sales Drop Rule: Change ≤ {Config.DROP_THRESHOLD_PCT}% "
            f"(Source: {Config.RULE_SOURCE})"
        )

        calc_breakdown = (
            f"Recent 7-day sales: {recent_units} units ({recent_daily_avg}/day)\n"
            f"Historical 30-day baseline (excl. recent 7d): {hist_units} units ({hist_daily_avg}/day = {hist_weekly_baseline}/week)\n"
            f"Percentage Change: ({recent_daily_avg} - {hist_daily_avg}) / {hist_daily_avg} × 100 = {pct_change:+.1f}%"
        )

        interpretation = (
            f"{product.product_name} at {store.store_name} experienced a {anomaly_type.replace('_', ' ').lower()} "
            f"of {pct_change:+.1f}% compared to its non-overlapping 30-day historical baseline."
        )

        return SalesAnomaly(
            product_id=product.product_id,
            product_name=product.product_name,
            store_id=store.store_id,
            store_name=store.store_name,
            recent_7day_sales=recent_units,
            recent_daily_avg=recent_daily_avg,
            historical_baseline_weekly=hist_weekly_baseline,
            historical_daily_avg=hist_daily_avg,
            pct_change=pct_change,
            anomaly_type=anomaly_type,
            detection_rule=rule_text,
            interpretation=interpretation,
            calculation_breakdown=calc_breakdown
        )

    def detect_all_anomalies(self, store_id: Optional[str] = None) -> List[SalesAnomaly]:
        results = []
        for p in self.loader.get_products():
            for s in self.loader.get_stores():
                if store_id and s.store_id != store_id:
                    continue
                anom = self.detect_anomalies_for_pair(p.product_id, s.store_id)
                if anom:
                    results.append(anom)
        # Sort by absolute percentage change descending
        results.sort(key=lambda x: abs(x.pct_change), reverse=True)
        return results
