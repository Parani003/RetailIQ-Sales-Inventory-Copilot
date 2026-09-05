"""
Deterministic Inventory Intelligence Module.
Calculates stockout risks, inventory coverage, overstock, slow/non-moving status with explicit safety rules.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from src.config import Config
from src.models import InventoryMetrics, Product, Store
from src.data_loader import DataLoader, get_data_loader


class InventoryAnalyzer:
    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or get_data_loader()

    def calculate_metrics_for_pair(self, product_id: str, store_id: str) -> Optional[InventoryMetrics]:
        product = self.loader.product_map.get(product_id)
        store = self.loader.store_map.get(store_id)
        if not product or not store:
            return None

        # Filter sales and inventory for pair
        df_s = self.loader.df_sales[
            (self.loader.df_sales['product_id'] == product_id) & 
            (self.loader.df_sales['store_id'] == store_id)
        ].sort_values('date')

        df_inv = self.loader.df_inventory[
            (self.loader.df_inventory['product_id'] == product_id) & 
            (self.loader.df_inventory['store_id'] == store_id)
        ].sort_values('date')

        if df_inv.empty:
            return None

        latest_date = df_inv['date'].max()
        current_stock = int(df_inv[df_inv['date'] == latest_date]['stock_quantity'].values[0])

        # Demand window (last N days)
        demand_window = Config.DEMAND_ESTIMATION_WINDOW
        window_start = latest_date - pd.Timedelta(days=demand_window - 1)
        df_recent_sales = df_s[df_s['date'] >= window_start]

        total_recent_units = int(df_recent_sales['units_sold'].sum()) if not df_recent_sales.empty else 0
        avg_daily_sales = round(total_recent_units / float(demand_window), 2)

        # Days remaining & division by zero guard
        if avg_daily_sales > 0:
            days_remaining = round(current_stock / avg_daily_sales, 1)
            days_remaining_str = f"{days_remaining} days"
        else:
            days_remaining = None
            days_remaining_str = "N/A (No Recent Sales)"

        # Stockout risk classification
        if days_remaining is not None and days_remaining <= Config.STOCKOUT_DAYS_THRESHOLD:
            stockout_risk = "HIGH"
        elif days_remaining is not None and days_remaining <= (Config.STOCKOUT_DAYS_THRESHOLD * 2.0):
            stockout_risk = "MEDIUM"
        else:
            stockout_risk = "LOW"

        # Overstock classification
        overstock_status = False
        if days_remaining is not None and days_remaining >= Config.OVERSTOCK_DAYS_THRESHOLD:
            overstock_status = True
        elif current_stock > (Config.LOW_STOCK_THRESHOLD * 10) and avg_daily_sales < 0.2:
            overstock_status = True

        # Days since last sale calculation
        sales_with_units = df_s[df_s['units_sold'] > 0]
        if not sales_with_units.empty:
            last_sale_date = sales_with_units['date'].max()
            days_since_last_sale = int((latest_date - last_sale_date).days)
        else:
            days_since_last_sale = 90  # Max dataset range

        slow_moving_status = (days_since_last_sale >= Config.SLOW_MOVING_THRESHOLD_DAYS)
        non_moving_status = (days_since_last_sale >= 30) or (total_recent_units == 0 and current_stock > 0)

        return InventoryMetrics(
            product_id=product.product_id,
            product_name=product.product_name,
            store_id=store.store_id,
            store_name=store.store_name,
            current_stock=current_stock,
            avg_daily_sales=avg_daily_sales,
            days_remaining=days_remaining,
            days_remaining_str=days_remaining_str,
            stockout_risk=stockout_risk,
            overstock_status=overstock_status,
            slow_moving_status=slow_moving_status,
            non_moving_status=non_moving_status,
            days_since_last_sale=days_since_last_sale,
            demand_window_days=demand_window
        )

    def get_all_inventory_metrics(self, store_id: Optional[str] = None, category: Optional[str] = None) -> List[InventoryMetrics]:
        results = []
        for p in self.loader.get_products():
            if category and p.category.lower() != category.lower():
                continue
            for s in self.loader.get_stores():
                if store_id and s.store_id != store_id:
                    continue
                metrics = self.calculate_metrics_for_pair(p.product_id, s.store_id)
                if metrics:
                    results.append(metrics)
        return results

    def get_stockout_risk_products(self, store_id: Optional[str] = None) -> List[InventoryMetrics]:
        all_metrics = self.get_all_inventory_metrics(store_id=store_id)
        return [m for m in all_metrics if m.stockout_risk in ["HIGH", "MEDIUM"]]

    def get_overstocked_products(self, store_id: Optional[str] = None) -> List[InventoryMetrics]:
        all_metrics = self.get_all_inventory_metrics(store_id=store_id)
        return [m for m in all_metrics if m.overstock_status]

    def get_slow_non_moving_products(self, store_id: Optional[str] = None) -> List[InventoryMetrics]:
        all_metrics = self.get_all_inventory_metrics(store_id=store_id)
        return [m for m in all_metrics if m.slow_moving_status or m.non_moving_status]
