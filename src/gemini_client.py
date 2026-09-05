"""
Google Gemini API Client & Explanation Engine.
Converts deterministic evidence packages into human-readable, grounded explanations.
Includes robust offline/fallback handling if API key is missing or API fails.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from src.models import EvidencePackage


class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_explanation(self, query: str, evidence_packages: List[EvidencePackage], context_str: str) -> Tuple[str, bool, Optional[str]]:
        """
        Returns: (markdown_text, is_fallback, fallback_message)
        """
        if not self.is_available():
            msg = "Gemini API key is not configured (GEMINI_API_KEY missing). Displaying deterministic data-grounded analysis."
            fallback_text = self._build_deterministic_text_response(query, evidence_packages, context_str)
            return fallback_text, True, msg

        # Construct Gemini Prompt
        evidence_json = json.dumps([ev.model_dump() for ev in evidence_packages], indent=2)

        system_instruction = (
            "You are RetailIQ Copilot, an expert AI retail decision assistant for store managers.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. You are grounded strictly in the provided Python-calculated evidence JSON.\n"
            "2. NEVER calculate numbers or invent product/store facts yourself. Use ONLY the numbers provided.\n"
            "3. Structure your response clearly using markdown numbered lists or headings.\n"
            "4. For each product/issue, clearly highlight:\n"
            "   - Product & Store\n"
            "   - Current Metrics (Stock, Avg Daily Sales, Coverage)\n"
            "   - Risk Level / Finding\n"
            "   - Recommended Action\n"
            "   - Supporting Evidence & Configured Business Rule\n"
            "   - Stated Assumptions\n"
            "5. Keep the response concise, professional, and directly actionable."
        )

        user_prompt = f"""
Manager Question: "{query}"

Calculated Context:
{context_str}

Structured Evidence Packages (Python Calculated):
{evidence_json}

Provide a clear, structured decision support answer based strictly on the above evidence.
"""

        try:
            # First try google.genai if available, otherwise direct HTTP request to Gemini REST endpoint
            response_text = self._call_gemini_api(system_instruction, user_prompt)
            if response_text:
                return response_text, False, None
            else:
                raise Exception("Empty response from Gemini API")
        except Exception as e:
            msg = f"Gemini API request failed ({str(e)}). Displaying deterministic data-grounded analysis."
            fallback_text = self._build_deterministic_text_response(query, evidence_packages, context_str)
            return fallback_text, True, msg

    def _call_gemini_api(self, system_instruction: str, user_prompt: str) -> Optional[str]:
        # Direct REST API call using urllib (zero extra native C dependencies, 100% reliable)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"{system_instruction}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        return None

    def _build_deterministic_text_response(self, query: str, evidence_packages: List[EvidencePackage], context_str: str) -> str:
        lines = [
            "### Data-Grounded Analysis\n",
        ]
        if not evidence_packages:
            lines.append(context_str)
            return "\n".join(lines)

        for idx, ev in enumerate(evidence_packages, 1):
            lines.append(f"#### {idx}. Product: {ev.product_name}")
            lines.append(f"- **Store**: {ev.store_name}")
            for k, v in ev.metrics.items():
                lines.append(f"- **{k}**: {v}")
            lines.append(f"- **Finding**: {ev.finding}")
            lines.append(f"- **Conclusion**: {ev.conclusion}")
            lines.append(f"\n**Recommendation**:")
            lines.append(f"{ev.recommended_action}\n")
            lines.append(f"**Evidence & Rule**:")
            lines.append(f"- Rule: `{ev.configured_rule}` ({ev.rule_source})")
            for step in ev.calculation_steps:
                lines.append(f"- Step: {step}")
            lines.append(f"\n**Assumption**:")
            for a in ev.assumptions:
                lines.append(f"- {a}")
            lines.append("\n" + "─" * 40 + "\n")

        return "\n".join(lines)
