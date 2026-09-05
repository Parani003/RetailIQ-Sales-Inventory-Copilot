"""
Data loader and repository module.
Loads CSV files into Pandas DataFrames and provides clean lookup methods.
"""

import os
import pandas as pd
from typing import List, Dict, Optional, Tuple
from src.models import Product, Store

class DataLoader:
    _instance = None

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.df_products: pd.DataFrame = pd.DataFrame()
        self.df_stores: pd.DataFrame = pd.DataFrame()
        self.df_sales: pd.DataFrame = pd.DataFrame()
        self.df_inventory: pd.DataFrame = pd.DataFrame()
        
        self.product_map: Dict[str, Product] = {}
        self.store_map: Dict[str, Store] = {}
        
        self.load_data()

    def load_data(self):
        prod_path = os.path.join(self.data_dir, "products.csv")
        store_path = os.path.join(self.data_dir, "stores.csv")
        sales_path = os.path.join(self.data_dir, "sales.csv")
        inv_path = os.path.join(self.data_dir, "inventory.csv")

        if not (os.path.exists(prod_path) and os.path.exists(store_path) and 
                os.path.exists(sales_path) and os.path.exists(inv_path)):
            raise FileNotFoundError("Dataset CSV files missing in 'data/' directory. Run generate_dataset.py first.")

        self.df_products = pd.read_csv(prod_path)
        self.df_stores = pd.read_csv(store_path)
        self.df_sales = pd.read_csv(sales_path)
        self.df_inventory = pd.read_csv(inv_path)

        # Convert date columns
        self.df_sales['date'] = pd.to_datetime(self.df_sales['date'])
        self.df_inventory['date'] = pd.to_datetime(self.df_inventory['date'])

        # Build product map
        for _, row in self.df_products.iterrows():
            p = Product(
                product_id=str(row['product_id']),
                product_name=str(row['product_name']),
                category=str(row['category']),
                price=float(row['price']),
                cost=float(row['cost']),
                supplier=str(row['supplier']),
                lead_time_days=int(row['lead_time_days'])
            )
            self.product_map[p.product_id] = p

        # Build store map
        for _, row in self.df_stores.iterrows():
            s = Store(
                store_id=str(row['store_id']),
                store_name=str(row['store_name']),
                location=str(row['location']),
                manager_name=str(row['manager_name'])
            )
            self.store_map[s.store_id] = s

    def get_latest_date(() -> pd.Timestamp:
        pass # Helper method

    def get_products(self) -> List[Product]:
        return list(self.product_map.values())

    def get_stores(self) -> List[Store]:
        return list(self.store_map.values())

    def find_product_by_name_or_id(self, query: str) -> Optional[Product]:
        query_lower = query.strip().lower()
        # Exact ID match
        for pid, p in self.product_map.items():
            if pid.lower() == query_lower:
                return p
        # Name match (exact or substring)
        for p in self.product_map.values():
            if p.product_name.lower() == query_lower:
                return p
        for p in self.product_map.values():
            if query_lower in p.product_name.lower():
                return p
        return None

    def find_store_by_name_or_id(self, query: str) -> Optional[Store]:
        query_lower = query.strip().lower()
        for sid, s in self.store_map.items():
            if sid.lower() == query_lower:
                return s
        for s in self.store_map.values():
            if s.store_name.lower() == query_lower:
                return s
        for s in self.store_map.values():
            if query_lower in s.store_name.lower():
                return s
        return None

_global_loader: Optional[DataLoader] = None

def get_data_loader() -> DataLoader:
    global _global_loader
    if _global_loader is None:
        _global_loader = DataLoader()
    return _global_loader
