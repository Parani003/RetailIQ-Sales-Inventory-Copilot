"""
RetailIQ Copilot - Web Application Entry Point.
FastAPI server serving backend REST APIs and frontend dashboard static files on port 8000.
Starts via: python app.py
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.config import Config
from src.data_loader import get_data_loader
from src.analytics import AnalyticsEngine
from src.inventory import InventoryAnalyzer
from src.anomaly_detection import AnomalyDetector
from src.copilot import RetailCopilot

app = FastAPI(
    title="RetailIQ Copilot",
    description="Data-Grounded Sales & Inventory Intelligence",
    version="1.0.0"
)

# Initialize engines
loader = get_data_loader()
analytics_engine = AnalyticsEngine(loader)
inventory_analyzer = InventoryAnalyzer(loader)
anomaly_detector = AnomalyDetector(loader)
copilot = RetailCopilot(loader)


class QueryRequest(BaseModel):
    query: str


class RuleUpdateRequest(BaseModel):
    low_stock_threshold: Optional[int] = None
    stockout_days_threshold: Optional[float] = None
    overstock_days_threshold: Optional[float] = None
    slow_moving_threshold_days: Optional[int] = None
    spike_threshold_pct: Optional[float] = None
    drop_threshold_pct: Optional[float] = None


@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    summary = analytics_engine.get_executive_summary()
    needs_attention = analytics_engine.get_needs_attention_today()
    return {
        "summary": summary,
        "needs_attention_today": [item.model_dump() for item in needs_attention]
    }


@app.post("/api/copilot/query")
def process_copilot_query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    response = copilot.process_query(request.query)
    return response.model_dump()


@app.get("/api/inventory")
def get_inventory_list(store_id: Optional[str] = None, category: Optional[str] = None, filter_risk: Optional[str] = None):
    all_metrics = inventory_analyzer.get_all_inventory_metrics(store_id=store_id, category=category)
    if filter_risk == "stockout":
        all_metrics = [m for m in all_metrics if m.stockout_risk in ["HIGH", "MEDIUM"]]
    elif filter_risk == "overstock":
        all_metrics = [m for m in all_metrics if m.overstock_status]
    elif filter_risk == "slow":
        all_metrics = [m for m in all_metrics if m.slow_moving_status or m.non_moving_status]
    
    return [m.model_dump() for m in all_metrics]


@app.get("/api/anomalies")
def get_sales_anomalies(store_id: Optional[str] = None):
    anomalies = anomaly_detector.detect_all_anomalies(store_id=store_id)
    return [a.model_dump() for a in anomalies]


@app.get("/api/products")
def get_product_list():
    products = loader.get_products()
    return [p.model_dump() for p in products]


@app.get("/api/products/{product_id}")
def get_product_details(product_id: str):
    product = loader.product_map.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    store_metrics = []
    for store in loader.get_stores():
        m = inventory_analyzer.calculate_metrics_for_pair(product_id, store.store_id)
        if m:
            store_metrics.append(m.model_dump())
            
    return {
        "product": product.model_dump(),
        "store_metrics": store_metrics
    }


@app.get("/api/stores/comparison")
def get_stores_comparison():
    return analytics_engine.get_store_comparison()


@app.get("/api/config/rules")
def get_business_rules():
    return Config.to_dict()


@app.post("/api/config/rules")
def update_business_rules(req: RuleUpdateRequest):
    updates = req.model_dump(exclude_none=True)
    Config.update_rules(**updates)
    return {
        "status": "success",
        "updated_rules": Config.to_dict()
    }


# Serve static frontend files
static_dir = os.path.join(os.path.dirname(__file__), "frontend", "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))


if __name__ == "__main__":
    print("Starting RetailIQ Copilot on http://localhost:8000 ...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
