"""
Data models and schemas for RetailIQ Copilot.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Product(BaseModel):
    product_id: str
    product_name: str
    category: str
    price: float
    cost: float
    supplier: str
    lead_time_days: int


class Store(BaseModel):
    store_id: str
    store_name: str
    location: str
    manager_name: str


class InventoryMetrics(BaseModel):
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    current_stock: int
    avg_daily_sales: float
    days_remaining: Optional[float] = None  # None if avg_daily_sales == 0
    days_remaining_str: str                 # "2.2 days" or "N/A (No Recent Sales)"
    stockout_risk: str                      # "HIGH", "MEDIUM", "LOW"
    overstock_status: bool
    slow_moving_status: bool
    non_moving_status: bool
    days_since_last_sale: int
    demand_window_days: int


class SalesAnomaly(BaseModel):
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    recent_7day_sales: float       # Weekly rate or total in 7d
    recent_daily_avg: float
    historical_baseline_weekly: float  # Baseline 7-day average from prior 30 days
    historical_daily_avg: float
    pct_change: float
    anomaly_type: str              # "SALES_SPIKE" or "SALES_DROP"
    detection_rule: str
    interpretation: str
    calculation_breakdown: str


class EvidencePackage(BaseModel):
    title: str
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    finding: str
    metrics: Dict[str, Any]
    calculation_steps: List[str]
    configured_rule: str
    rule_source: str = "Application business rule"
    assumptions: List[str]
    conclusion: str
    recommended_action: str


class Recommendation(BaseModel):
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    action_type: str                # "REORDER", "REALLOCATE", "MARKDOWN", "INVESTIGATE"
    title: str
    severity: str                   # "HIGH", "MEDIUM", "LOW"
    metrics_summary: Dict[str, Any]
    why_reason: str
    assumption: str
    recommended_action: str
    evidence: EvidencePackage


class NeedsAttentionItem(BaseModel):
    id: str
    product_id: str
    product_name: str
    store_id: str
    store_name: str
    problem: str
    severity: str                   # "CRITICAL", "WARNING", "INFO"
    metrics_summary: str
    why_it_matters: str
    recommended_action: str
    confidence_evidence: str
    evidence: EvidencePackage


class CopilotResponse(BaseModel):
    query: str
    parsed_intent: str
    entities_found: Dict[str, List[str]]
    answer_markdown: str
    recommendations: List[Recommendation] = []
    evidence_packages: List[EvidencePackage] = []
    refuses_unsupported: bool = False
    refusal_reason: Optional[str] = None
    is_gemini_fallback: bool = False
    fallback_message: Optional[str] = None
