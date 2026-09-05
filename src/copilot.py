"""
Copilot Engine & Pipeline Orchestrator.
Links Query Parsing -> Deterministic Business Analytics -> Evidence Packaging -> Gemini Grounded Explanation.
"""

from typing import List, Optional, Dict, Any
from src.retrieval import QueryParser
from src.inventory import InventoryAnalyzer
from src.anomaly_detection import AnomalyDetector
from src.analytics import AnalyticsEngine
from src.evidence import EvidenceBuilder
from src.recommendations import RecommendationEngine
from src.gemini_client import GeminiClient
from src.models import CopilotResponse, EvidencePackage, Recommendation
from src.data_loader import DataLoader, get_data_loader


class RetailCopilot:
    def __init__(self, loader: Optional[DataLoader] = None):
        self.loader = loader or get_data_loader()
        self.parser = QueryParser(self.loader)
        self.inventory_analyzer = InventoryAnalyzer(self.loader)
        self.anomaly_detector = AnomalyDetector(self.loader)
        self.analytics_engine = AnalyticsEngine(self.loader)
        self.gemini_client = GeminiClient()

    def process_query(self, query: str) -> CopilotResponse:
        intent, entities, unknown_entity = self.parser.parse_query(query)

        entities_found = {
            "products": [p.product_name for p in entities["products"]],
            "stores": [s.store_name for s in entities["stores"]],
            "unknown": entities["unknown_entities"]
        }

        # 1. NO-HALLUCINATION GUARDRAIL: Refuse unsupported/missing products
        if unknown_entity:
            refusal_text = (
                f"I couldn't find '{unknown_entity}' in the available retail dataset, so I cannot provide a performance analysis.\n\n"
                f"Available product categories in our catalogue include:\n"
                f"- **Electronics**: Wireless Mouse, Mechanical Keyboard, HD Webcam, 4K Monitor, Smart Watch...\n"
                f"- **Apparel**: Cotton T-Shirt, Denim Jeans, Running Shoes, Winter Coat...\n"
                f"- **Grocery**: Organic Coffee Beans, Green Tea, Protein Bars, Extra Virgin Olive Oil...\n"
                f"- **Home Goods**: Stainless Travel Mug, Ceramic Plate Set, Air Purifier Filter...\n"
                f"- **Beauty & Health**: Facial Cleanser, Vitamin C Serum, Electric Toothbrush..."
            )
            return CopilotResponse(
                query=query,
                parsed_intent=intent,
                entities_found=entities_found,
                answer_markdown=refusal_text,
                recommendations=[],
                evidence_packages=[],
                refuses_unsupported=True,
                refusal_reason=f"Entity '{unknown_entity}' not found in catalogue dataset."
            )

        target_store_id = entities["stores"][0].store_id if entities["stores"] else None
        target_product = entities["products"][0] if entities["products"] else None

        evidence_packages: List[EvidencePackage] = []
        recommendations: List[Recommendation] = []
        context_str = ""

        # 2. DETERMINISTIC ANALYTICS ROUTING
        if intent == "RUNNING_OUT":
            stockouts = self.inventory_analyzer.get_stockout_risk_products(store_id=target_store_id)
            stockouts.sort(key=lambda x: x.days_remaining if x.days_remaining is not None else 999)
            context_str = f"Found {len(stockouts)} products at high/medium stock-out risk."
            for m in stockouts[:5]:
                ev = EvidenceBuilder.build_inventory_evidence(m, "Stock-out Risk")
                evidence_packages.append(ev)
                rec = RecommendationEngine.from_inventory_metrics(m)
                if rec:
                    recommendations.append(rec)

        elif intent == "OVERSTOCKED":
            overstocked = self.inventory_analyzer.get_overstocked_products(store_id=target_store_id)
            context_str = f"Found {len(overstocked)} overstocked products with excess inventory coverage."
            for m in overstocked[:5]:
                ev = EvidenceBuilder.build_inventory_evidence(m, "Overstocked Inventory")
                evidence_packages.append(ev)
                rec = RecommendationEngine.from_inventory_metrics(m)
                if rec:
                    recommendations.append(rec)

        elif intent == "SLOW_MOVING":
            slow = self.inventory_analyzer.get_slow_non_moving_products(store_id=target_store_id)
            context_str = f"Found {len(slow)} slow or non-moving products."
            for m in slow[:5]:
                ev = EvidenceBuilder.build_inventory_evidence(m, "Slow/Non-Moving Inventory")
                evidence_packages.append(ev)
                rec = RecommendationEngine.from_inventory_metrics(m)
                if rec:
                    recommendations.append(rec)

        elif intent == "ANOMALIES":
            anomalies = self.anomaly_detector.detect_all_anomalies(store_id=target_store_id)
            context_str = f"Detected {len(anomalies)} sales anomalies (spikes/drops) vs 30-day non-overlapping baseline."
            for a in anomalies[:5]:
                ev = EvidenceBuilder.build_anomaly_evidence(a)
                evidence_packages.append(ev)
                recommendations.append(RecommendationEngine.from_anomaly(a))

        elif intent == "PRODUCT_WHY_RISK" or (target_product and ("risk" in query.lower() or "why" in query.lower())):
            prod = target_product or self.loader.get_products()[0]
            store_id = target_store_id or "S101"
            m = self.inventory_analyzer.calculate_metrics_for_pair(prod.product_id, store_id)
            if m:
                ev = EvidenceBuilder.build_inventory_evidence(m, f"Risk & Inventory Breakdown for {prod.product_name}")
                evidence_packages.append(ev)
                rec = RecommendationEngine.from_inventory_metrics(m)
                if rec:
                    recommendations.append(rec)
                context_str = f"Detailed risk analysis for {prod.product_name} at store {store_id}."

        elif intent == "PRODUCT_PERFORMANCE" and target_product:
            store_id = target_store_id or "S101"
            m = self.inventory_analyzer.calculate_metrics_for_pair(target_product.product_id, store_id)
            anom = self.anomaly_detector.detect_anomalies_for_pair(target_product.product_id, store_id)
            if m:
                ev = EvidenceBuilder.build_inventory_evidence(m, f"Performance Metrics for {target_product.product_name}")
                evidence_packages.append(ev)
            if anom:
                ev_anom = EvidenceBuilder.build_anomaly_evidence(anom)
                evidence_packages.append(ev_anom)
            context_str = f"Performance overview for {target_product.product_name} ({target_product.category}). Price: ${target_product.price}."

        elif intent == "STORE_COMPARISON":
            comparisons = self.analytics_engine.get_store_comparison()
            best = comparisons[0]
            worst_risk = max(comparisons, key=lambda x: x['stockout_risk_count'])
            context_str = (
                f"Multi-Store Performance Summary:\n"
                f"- Top Revenue Store: {best['store_name']} (${best['total_revenue']:,} revenue, {best['total_units_sold']:,} units sold).\n"
                f"- Highest Stock-out Risk Store: {worst_risk['store_name']} ({worst_risk['stockout_risk_count']} high risk items).\n"
                f"Stores compared: {', '.join(c['store_name'] for c in comparisons)}"
            )

        else: # GENERAL or NEEDS_ATTENTION
            attn = self.analytics_engine.get_needs_attention_today()
            context_str = f"Prioritized {len(attn)} operational issues needing attention today."
            for item in attn[:4]:
                evidence_packages.append(item.evidence)

        # 3. GENERATE GROUNDED EXPLANATION VIA GEMINI (OR TRANSPARENT FALLBACK)
        answer_md, is_fallback, fallback_msg = self.gemini_client.generate_explanation(
            query=query,
            evidence_packages=evidence_packages,
            context_str=context_str
        )

        return CopilotResponse(
            query=query,
            parsed_intent=intent,
            entities_found=entities_found,
            answer_markdown=answer_md,
            recommendations=recommendations,
            evidence_packages=evidence_packages,
            refuses_unsupported=False,
            is_gemini_fallback=is_fallback,
            fallback_message=fallback_msg
        )
