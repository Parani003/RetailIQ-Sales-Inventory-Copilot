"""
Executive Analytics & Prioritization Engine.
Computes high-level retail KPIs, multi-store comparisons, and 'Needs Attention Today' issue scoring.
"""

from typing import List, Dict, Any, Optional
from src.data_loader import get_data_loader, DataLoader
from src.inventory import InventoryAnalyzer
from src.anomaly_detection import AnomalyDetector
from src.models import NeedsAttentionItem, InventoryMetrics, SalesAnomaly
from src.evidence import EvidenceBuilder


class AnalyticsEngine:
    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or get_data_loader()
        self.inventory_analyzer = InventoryAnalyzer(self.loader)
        self.anomaly_detector = AnomalyDetector(self.loader)

    def get_executive_summary(self) -> Dict[str, Any]:
        df_s = self.loader.df_sales
        total_revenue = round(float(df_s['revenue'].sum()), 2)
        total_units = int(df_s['units_sold'].sum())
        total_products = len(self.loader.get_products())
        total_stores = len(self.loader.get_stores())

        all_inv = self.inventory_analyzer.get_all_inventory_metrics()
        stockout_risks = [m for m in all_inv if m.stockout_risk == "HIGH"]
        overstocked = [m for m in all_inv if m.overstock_status]
        slow_moving = [m for m in all_inv if m.slow_moving_status or m.non_moving_status]

        all_anomalies = self.anomaly_detector.detect_all_anomalies()
        spikes = [a for a in all_anomalies if a.anomaly_type == "SALES_SPIKE"]
        drops = [a for a in all_anomalies if a.anomaly_type == "SALES_DROP"]

        return {
            "total_revenue": total_revenue,
            "total_units_sold": total_units,
            "total_products": total_products,
            "total_stores": total_stores,
            "stockout_risk_count": len(stockout_risks),
            "overstocked_count": len(overstocked),
            "slow_moving_count": len(slow_moving),
            "sales_spikes_count": len(spikes),
            "sales_drops_count": len(drops)
        }

    def get_needs_attention_today(self) -> List[NeedsAttentionItem]:
        items: List[NeedsAttentionItem] = []
        item_counter = 1

        # 1. High Stockout Risks
        all_inv = self.inventory_analyzer.get_all_inventory_metrics()
        high_stockouts = [m for m in all_inv if m.stockout_risk == "HIGH"]
        for m in high_stockouts:
            ev = EvidenceBuilder.build_inventory_evidence(m, "Critical Stock-out Risk")
            items.append(NeedsAttentionItem(
                id=f"ATTN-{item_counter:03d}",
                product_id=m.product_id,
                product_name=m.product_name,
                store_id=m.store_id,
                store_name=m.store_name,
                problem=f"Imminent Stock-out (Only {m.days_remaining_str} remaining)",
                severity="CRITICAL",
                metrics_summary=f"Stock: {m.current_stock} units | Daily Sales: {m.avg_daily_sales}/day",
                why_it_matters=f"Store will run out of stock in {m.days_remaining_str}, causing lost revenue and customer dissatisfaction.",
                recommended_action=f"Reorder {m.product_name} immediately from supplier with expedited lead time.",
                confidence_evidence="100% Deterministic — Calculated directly from 14-day sales velocity and live stock levels.",
                evidence=ev
            ))
            item_counter += 1

        # 2. Major Sales Spikes
        anomalies = self.anomaly_detector.detect_all_anomalies()
        spikes = [a for a in anomalies if a.anomaly_type == "SALES_SPIKE"]
        for a in spikes[:3]:
            ev = EvidenceBuilder.build_anomaly_evidence(a)
            items.append(NeedsAttentionItem(
                id=f"ATTN-{item_counter:03d}",
                product_id=a.product_id,
                product_name=a.product_name,
                store_id=a.store_id,
                store_name=a.store_name,
                problem=f"Unusual Demand Surge ({a.pct_change:+.1f}% vs 30-day baseline)",
                severity="WARNING",
                metrics_summary=f"Recent 7d Sales: {a.recent_7day_sales} units vs Baseline: {a.historical_baseline_weekly} units/wk",
                why_it_matters="Unpredicted demand spikes rapidly drain inventory and cause unexpected stock-outs if unmonitored.",
                recommended_action="Increase replenishment quota and verify store inventory buffers.",
                confidence_evidence="100% Deterministic — Calculated via non-overlapping 30-day baseline comparison.",
                evidence=ev
            ))
            item_counter += 1

        # 3. Severe Sales Drops
        drops = [a for a in anomalies if a.anomaly_type == "SALES_DROP"]
        for a in drops[:3]:
            ev = EvidenceBuilder.build_anomaly_evidence(a)
            items.append(NeedsAttentionItem(
                id=f"ATTN-{item_counter:03d}",
                product_id=a.product_id,
                product_name=a.product_name,
                store_id=a.store_id,
                store_name=a.store_name,
                problem=f"Sudden Sales Collapse ({a.pct_change:+.1f}% drop)",
                severity="WARNING",
                metrics_summary=f"Recent 7d Sales: {a.recent_7day_sales} units vs Baseline: {a.historical_baseline_weekly} units/wk",
                why_it_matters="Indicates potential store-level execution issues such as missing shelf tags or bad product placement.",
                recommended_action="Conduct store audit of shelf display and verify current retail pricing.",
                confidence_evidence="100% Deterministic — Statistically verified drop below historical baseline.",
                evidence=ev
            ))
            item_counter += 1

        # 4. Severe Overstock / Non-moving
        overstocked = [m for m in all_inv if m.overstock_status][:3]
        for m in overstocked:
            ev = EvidenceBuilder.build_inventory_evidence(m, "Capital Tied Up in Overstock")
            items.append(NeedsAttentionItem(
                id=f"ATTN-{item_counter:03d}",
                product_id=m.product_id,
                product_name=m.product_name,
                store_id=m.store_id,
                store_name=m.store_name,
                problem=f"Severe Overstock ({m.days_remaining_str} of inventory)",
                severity="INFO",
                metrics_summary=f"Stock: {m.current_stock} units | Daily Sales: {m.avg_daily_sales}/day",
                why_it_matters="Excess inventory ties up working capital and increases warehouse holding costs.",
                recommended_action="Halt orders and consider promotional discount or inter-store transfer.",
                confidence_evidence="100% Deterministic — Stock levels exceed 45-day coverage threshold.",
                evidence=ev
            ))
            item_counter += 1

        return items

    def get_store_comparison(()) -> List[Dict[str, Any]]:
        stores = self.loader.get_stores()
        df_s = self.loader.df_sales
        all_inv = self.inventory_analyzer.get_all_inventory_metrics()

        result = []
        for s in stores:
            df_store_sales = df_s[df_s['store_id'] == s.store_id]
            rev = round(float(df_store_sales['revenue'].sum()), 2)
            units = int(df_store_sales['units_sold'].sum())

            store_inv = [m for m in all_inv if m.store_id == s.store_id]
            stockout_count = sum(1 for m in store_inv if m.stockout_risk == "HIGH")
            overstock_count = sum(1 for m in store_inv if m.overstock_status)

            # Top product by revenue
            prod_rev = df_store_sales.groupby('product_id')['revenue'].sum().reset_index()
            prod_rev = prod_rev.sort_values('revenue', ascending=False)
            top_pid = prod_rev.iloc[0]['product_id'] if not prod_rev.empty else ""
            top_pname = self.loader.product_map[top_pid].product_name if top_pid in self.loader.product_map else "N/A"

            result.append({
                "store_id": s.store_id,
                "store_name": s.store_name,
                "location": s.location,
                "manager": s.manager_name,
                "total_revenue": rev,
                "total_units_sold": units,
                "top_product": top_pname,
                "stockout_risk_count": stockout_count,
                "overstock_count": overstock_count,
                "health_score": max(100 - (stockout_count * 15 + overstock_count * 5), 30)
            })

        result.sort(key=lambda x: x['total_revenue'], reverse=True)
        return result
