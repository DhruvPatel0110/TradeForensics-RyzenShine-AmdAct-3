"""
Unit tests for FireworksLLMClient and AMD Instinct hardware adapter.
"""

import pytest
from backend.app.llm.fireworks_client import FireworksLLMClient
from backend.app.llm.client import get_llm_client
from backend.app.core.config import settings

def test_fireworks_client_initialization():
    client = FireworksLLMClient(api_key="fw_test_key", model="accounts/fireworks/models/llama-v3p3-70b-instruct")
    assert client.api_key == "fw_test_key"
    assert "accounts/fireworks" in client.model
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "Bearer fw_test_key"

def test_fireworks_client_generate_json_schema():
    client = FireworksLLMClient(api_key="fw_placeholder_key")
    prompt = "Generate remediation plan for high delay seller."
    result = client.generate_json(prompt)
    
    assert isinstance(result, dict)
    assert "summary" in result
    assert "severity" in result
    assert "ml_risk_assessment" in result
    assert "recommended_actions" in result
    assert isinstance(result["recommended_actions"], list)
    assert len(result["recommended_actions"]) > 0

def test_get_llm_client_factory_fallback(monkeypatch):
    monkeypatch.setattr(settings, "LLM_PROVIDER", "fireworks")
    client = get_llm_client()
    assert client is not None
