"""
Actionable Recommendation Generator Engine.
Translates inventory and sales findings into prioritized recommendations with explicit 'Why?' rationale.
"""

from typing import List, Optional
from src.config import Config
from src.models import Recommendation, InventoryMetrics, SalesAnomaly
from src.evidence import EvidenceBuilder


class RecommendationEngine:
    @staticmethod
    def from_inventory_metrics(metrics: InventoryMetrics) -> Optional[Recommendation]:
        if metrics.stockout_risk == "HIGH":
            ev = EvidenceBuilder.build_inventory_evidence(metrics, "Stock-out Risk High")
            return Recommendation(
                product_id=metrics.product_id,
                product_name=metrics.product_name,
                store_id=metrics.store_id,
                store_name=metrics.store_name,
                action_type="REORDER",
                title=f"⚠️ REORDER RECOMMENDED: {metrics.product_name} at {metrics.store_name}",
                severity="HIGH",
                metrics_summary={
                    "Current Stock": f"{metrics.current_stock} units",
                    "Avg Daily Sales": f"{metrics.avg_daily_sales} units/day",
                    "Inventory Coverage": metrics.days_remaining_str,
                    "Risk Threshold": f"≤ {Config.STOCKOUT_DAYS_THRESHOLD} days"
                },
                why_reason=f"Inventory coverage ({metrics.days_remaining_str}) is below the configured {Config.STOCKOUT_DAYS_THRESHOLD}-day stock-out threshold.",
                assumption=f"Demand is estimated using the previous {Config.DEMAND_ESTIMATION_WINDOW} days of daily sales.",
                recommended_action=f"Review inventory and place immediate replenishment order for {metrics.product_name}.",
                evidence=ev
            )
        elif metrics.overstock_status:
            ev = EvidenceBuilder.build_inventory_evidence(metrics, "Overstocked Inventory")
            return Recommendation(
                product_id=metrics.product_id,
                product_name=metrics.product_name,
                store_id=metrics.store_id,
                store_name=metrics.store_name,
                action_type="REALLOCATE",
                title=f"📦 OVERSTOCK ACTION: {metrics.product_name} at {metrics.store_name}",
                severity="MEDIUM",
                metrics_summary={
                    "Current Stock": f"{metrics.current_stock} units",
                    "Avg Daily Sales": f"{metrics.avg_daily_sales} units/day",
                    "Inventory Coverage": metrics.days_remaining_str,
                    "Overstock Threshold": f"≥ {Config.OVERSTOCK_DAYS_THRESHOLD} days"
                },
                why_reason=f"Inventory coverage ({metrics.days_remaining_str}) exceeds the configured overstock threshold of {Config.OVERSTOCK_DAYS_THRESHOLD} days.",
                assumption="Holding excess stock ties up working capital and increases holding costs.",
                recommended_action="Pause future purchase orders and evaluate transferring stock to higher-demand store locations.",
                evidence=ev
            )
        elif metrics.slow_moving_status or metrics.non_moving_status:
            ev = EvidenceBuilder.build_inventory_evidence(metrics, "Slow/Non-Moving Inventory")
            return Recommendation(
                product_id=metrics.product_id,
                product_name=metrics.product_name,
                store_id=metrics.store_id,
                store_name=metrics.store_name,
                action_type="MARKDOWN",
                title=f"🏷️ PROMOTION / MARKDOWN: {metrics.product_name} at {metrics.store_name}",
                severity="MEDIUM",
                metrics_summary={
                    "Current Stock": f"{metrics.current_stock} units",
                    "Days Since Last Sale": f"{metrics.days_since_last_sale} days",
                    "Slow Moving Threshold": f"≥ {Config.SLOW_MOVING_THRESHOLD_DAYS} days"
                },
                why_reason=f"No sales recorded for {metrics.days_since_last_sale} days, exceeding the {Config.SLOW_MOVING_THRESHOLD_DAYS}-day slow-moving threshold.",
                assumption="Product demand has stagnated in this store location.",
                recommended_action="Execute a 15-25% price markdown or bundle with complementary high-velocity items.",
                evidence=ev
            )
        return None

    @staticmethod
    def from_anomaly(anomaly: SalesAnomaly) -> Recommendation:
        ev = EvidenceBuilder.build_anomaly_evidence(anomaly)
        if anomaly.anomaly_type == "SALES_SPIKE":
            return Recommendation(
                product_id=anomaly.product_id,
                product_name=anomaly.product_name,
                store_id=anomaly.store_id,
                store_name=anomaly.store_name,
                action_type="REORDER",
                title=f"📈 DEMAND SURGE: {anomaly.product_name} at {anomaly.store_name} ({anomaly.pct_change:+.1f}%)",
                severity="HIGH",
                metrics_summary={
                    "Recent 7-Day Sales": f"{anomaly.recent_7day_sales} units",
                    "Historical Baseline": f"{anomaly.historical_baseline_weekly} units/wk",
                    "Change": f"{anomaly.pct_change:+.1f}%"
                },
                why_reason=f"Recent sales rate increased by {anomaly.pct_change:+.1f}% compared to non-overlapping 30-day baseline.",
                assumption="Demand surge is likely to persist over the coming week.",
                recommended_action="Increase safety stock levels to support continued elevated sales velocity.",
                evidence=ev
            )
        else:
            return Recommendation(
                product_id=anomaly.product_id,
                product_name=anomaly.product_name,
                store_id=anomaly.store_id,
                store_name=anomaly.store_name,
                action_type="INVESTIGATE",
                title=f"📉 SALES DROP WARNING: {anomaly.product_name} at {anomaly.store_name} ({anomaly.pct_change:+.1f}%)",
                severity="MEDIUM",
                metrics_summary={
                    "Recent 7-Day Sales": f"{anomaly.recent_7day_sales} units",
                    "Historical Baseline": f"{anomaly.historical_baseline_weekly} units/wk",
                    "Change": f"{anomaly.pct_change:+.1f}%"
                },
                why_reason=f"Recent sales fell by {anomaly.pct_change:+.1f}%, dropping significantly below baseline.",
                assumption="Potential out-of-stock condition on shelf, pricing discrepancy, or loss of foot traffic.",
                recommended_action="Inspect store shelf availability, price tags, and competitor positioning.",
                evidence=ev
            )
