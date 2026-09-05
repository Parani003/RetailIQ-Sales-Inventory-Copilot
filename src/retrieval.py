"""
Intent Classification & Entity Parsing Engine.
Extracts products, stores, categories, and analytical intent from natural language queries.
"""

import re
from typing import Dict, List, Optional, Tuple
from src.data_loader import DataLoader, get_data_loader
from src.models import Product, Store


class QueryParser:
    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or get_data_loader()

    def parse_query(self, query: str) -> Tuple[str, Dict[str, List[Any]], Optional[str]]:
        query_lower = query.lower().strip()
        entities: Dict[str, List[Any]] = {
            "products": [],
            "stores": [],
            "categories": [],
            "unknown_entities": []
        }

        # 1. Product extraction
        # Exact/partial name matching against dataset
        found_products = []
        for p in self.loader.get_products():
            if p.product_name.lower() in query_lower or p.product_id.lower() == query_lower:
                found_products.append(p)

        # 2. Store extraction
        found_stores = []
        for s in self.loader.get_stores():
            if s.store_name.lower() in query_lower or s.store_id.lower() == query_lower:
                found_stores.append(s)
            elif s.store_name.lower().replace(" store", "") in query_lower:
                found_stores.append(s)
            elif "store a" in query_lower and s.store_id == "S101":
                found_stores.append(s)
            elif "store b" in query_lower and s.store_id == "S102":
                found_stores.append(s)
            elif "store c" in query_lower and s.store_id == "S103":
                found_stores.append(s)
            elif "store d" in query_lower and s.store_id == "S104":
                found_stores.append(s)

        entities["products"] = found_products
        entities["stores"] = found_stores

        # 3. Check for explicitly queried non-existent products/brands (e.g. "iPhone", "MacBook", "PlayStation")
        common_unknowns = ["iphone", "macbook", "ipad", "playstation", "xbox", "nike", "adidas", "tesla", "samsung galaxy"]
        unsupported_mention = None
        for u in common_unknowns:
            if u in query_lower:
                unsupported_mention = u.capitalize()
                entities["unknown_entities"].append(unsupported_mention)
                break

        # 4. Intent Classification
        intent = "GENERAL"

        if any(w in query_lower for w in ["run out", "running out", "stock out", "stockout", "reorder first", "low stock"]):
            intent = "RUNNING_OUT"
        elif any(w in query_lower for w in ["overstock", "overstocked", "excess stock", "too much stock"]):
            intent = "OVERSTOCKED"
        elif any(w in query_lower for w in ["not moving", "slow moving", "stagnant", "zero sales"]):
            intent = "SLOW_MOVING"
        elif any(w in query_lower for w in ["spike", "drop", "unusual", "change", "anomaly", "anomalies", "sudden"]):
            intent = "ANOMALIES"
        elif any(w in query_lower for w in ["why", "evidence", "risk factor", "reason"]):
            intent = "PRODUCT_WHY_RISK"
        elif any(w in query_lower for w in ["store performing", "best store", "compare store", "which store"]):
            intent = "STORE_COMPARISON"
        elif any(w in query_lower for w in ["today", "attention", "urgent", "priority"]):
            intent = "NEEDS_ATTENTION"
        elif found_products:
            intent = "PRODUCT_PERFORMANCE"

        return intent, entities, unsupported_mention
