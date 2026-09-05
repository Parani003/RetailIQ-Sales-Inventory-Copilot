"""
Unit tests for Copilot query pipeline and refusal logic.
"""

import pytest
from src.data_loader import get_data_loader
from src.copilot import RetailCopilot


@pytest.fixture
def copilot():
    loader = get_data_loader()
    return RetailCopilot(loader)


def test_copilot_running_out_intent(copilot):
    response = copilot.process_query("What products are running out?")
    assert response.parsed_intent == "RUNNING_OUT"
    assert response.refuses_unsupported is False
    assert len(response.evidence_packages) > 0


def test_copilot_no_hallucination_refusal(copilot):
    response = copilot.process_query("How did iPhone sales perform this month?")
    assert response.refuses_unsupported is True
    assert "couldn't find 'Iphone'" in response.answer_markdown or "couldn't find" in response.answer_markdown
    assert response.refusal_reason is not None


def test_copilot_gemini_fallback_when_unconfigured(copilot):
    # API key unconfigured in test environment
    response = copilot.process_query("Show me overstocked products.")
    assert response.is_gemini_fallback is True
    assert "Gemini API key is not configured" in response.fallback_message
    assert len(response.evidence_packages) > 0
