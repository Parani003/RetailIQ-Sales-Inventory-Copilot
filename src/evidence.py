"""
Evidence Package Generator Engine.
Constructs transparent, auditable evidence packages with step-by-step calculations,
configured rules, explicit sources, and demand assumptions.
"""

from typing import Dict, Any, List
from src.config import Config
from src.models import EvidencePackage, InventoryMetrics, SalesAnomaly


class EvidenceBuilder:
    @staticmethod
    def build_inventory_evidence(metrics: InventoryMetrics, finding_title: str) -> EvidencePackage:
        calc_steps = []
        if metrics.avg_daily_sales > 0 and metrics.days_remaining is not None:
            calc_steps = [
                f"Current Stock = {metrics.current_stock} units",
                f"14-Day Average Daily Sales = {metrics.avg_daily_sales} units/day",
                f"Calculation: {metrics.current_stock} ÷ {metrics.avg_daily_sales} = {metrics.days_remaining} days of coverage"
            ]
            rule_str = f"Stock-out Risk Threshold: ≤ {Config.STOCKOUT_DAYS_THRESHOLD} days of coverage"
            conclusion = f"Coverage of {metrics.days_remaining} days is BELOW the configured {Config.STOCKOUT_DAYS_THRESHOLD}-day stock-out threshold -> HIGH STOCK-OUT RISK."
            rec_action = f"Initiate expedited stock replenishment for {metrics.product_name} at {metrics.store_name}."
        elif metrics.overstock_status:
            calc_steps = [
                f"Current Stock = {metrics.current_stock} units",
                f"14-Day Average Daily Sales = {metrics.avg_daily_sales} units/day",
                f"Calculation: {metrics.current_stock} ÷ {metrics.avg_daily_sales} = {metrics.days_remaining_str}"
            ]
            rule_str = f"Overstock Threshold: ≥ {Config.OVERSTOCK_DAYS_THRESHOLD} days of coverage"
            conclusion = f"Coverage of {metrics.days_remaining_str} EXCEEDS configured overstock threshold of {Config.OVERSTOCK_DAYS_THRESHOLD} days -> OVERSTOCKED."
            rec_action = f"Pause stock replenishment and evaluate inter-store reallocation or promotional discount."
        else:
            calc_steps = [
                f"Current Stock = {metrics.current_stock} units",
                f"Days Since Last Sale = {metrics.days_since_last_sale} days",
                f"14-Day Units Sold = 0 units"
            ]
            rule_str = f"Slow-Moving Threshold: ≥ {Config.SLOW_MOVING_THRESHOLD_DAYS} days without sales"
            conclusion = f"No sales recorded for {metrics.days_since_last_sale} days -> SLOW / NON-MOVING INVENTORY."
            rec_action = f"Consider price markdown, bundling promotion, or returning stock to supplier."

        return EvidencePackage(
            title=finding_title,
            product_id=metrics.product_id,
            product_name=metrics.product_name,
            store_id=metrics.store_id,
            store_name=metrics.store_name,
            finding=f"{metrics.product_name} ({metrics.store_name}): {finding_title}",
            metrics={
                "Current Stock": metrics.current_stock,
                "Avg Daily Sales": metrics.avg_daily_sales,
                "Inventory Coverage": metrics.days_remaining_str,
                "Stockout Risk": metrics.stockout_risk,
                "Days Since Last Sale": metrics.days_since_last_sale
            },
            calculation_steps=calc_steps,
            configured_rule=rule_str,
            rule_source=Config.RULE_SOURCE,
            assumptions=[
                f"Demand estimate uses average daily sales velocity from the previous {Config.DEMAND_ESTIMATION_WINDOW} days.",
                "Supplier lead times and future demand spikes are assumed constant over the coverage window."
            ],
            conclusion=conclusion,
            recommended_action=rec_action
        )

    @staticmethod
    def build_anomaly_evidence(anomaly: SalesAnomaly) -> EvidencePackage:
        calc_steps = [
            f"Recent 7-Day Total Sales = {anomaly.recent_7day_sales} units ({anomaly.recent_daily_avg} units/day)",
            f"Historical 30-Day Baseline (excl. recent 7d) = {anomaly.historical_baseline_weekly} units/week ({anomaly.historical_daily_avg} units/day)",
            f"Calculation: ({anomaly.recent_daily_avg} - {anomaly.historical_daily_avg}) ÷ {anomaly.historical_daily_avg} × 100 = {anomaly.pct_change:+.1f}%"
        ]
        
        if anomaly.anomaly_type == "SALES_SPIKE":
            rule_str = f"Sales Spike Threshold: Change ≥ +{Config.SPIKE_THRESHOLD_PCT}% over historical 30-day baseline"
            conclusion = f"Sales increased by {anomaly.pct_change:+.1f}%, exceeding the +{Config.SPIKE_THRESHOLD_PCT}% threshold -> SALES SPIKE DETECTED."
            rec_action = "Ensure stock levels are sufficient to capture surge demand and prevent sudden stock-out."
        else:
            rule_str = f"Sales Drop Threshold: Change ≤ {Config.DROP_THRESHOLD_PCT}% under historical 30-day baseline"
            conclusion = f"Sales decreased by {anomaly.pct_change:+.1f}%, dropping below the {Config.DROP_THRESHOLD_PCT}% threshold -> SALES DROP DETECTED."
            rec_action = "Investigate potential causes (price sensitivity, shelf display placement, competitor action, local stockout)."

        return EvidencePackage(
            title=f"{anomaly.anomaly_type.replace('_', ' ')}: {anomaly.pct_change:+.1f}%",
            product_id=anomaly.product_id,
            product_name=anomaly.product_name,
            store_id=anomaly.store_id,
            store_name=anomaly.store_name,
            finding=anomaly.interpretation,
            metrics={
                "Recent 7-Day Sales": anomaly.recent_7day_sales,
                "Recent Daily Avg": anomaly.recent_daily_avg,
                "Historical 30-Day Weekly Baseline": anomaly.historical_baseline_weekly,
                "Historical Daily Avg": anomaly.historical_daily_avg,
                "Percentage Change": f"{anomaly.pct_change:+.1f}%"
            },
            calculation_steps=calc_steps,
            configured_rule=rule_str,
            rule_source=Config.RULE_SOURCE,
            assumptions=[
                f"Recent period is defined as the latest {Config.RECENT_ANOMALY_WINDOW} days.",
                f"Historical baseline is defined as the prior {Config.HISTORICAL_BASELINE_WINDOW} days, non-overlapping with the recent period."
            ],
            conclusion=conclusion,
            recommended_action=rec_action
        )
