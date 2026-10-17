import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class BaseLLMClient(ABC):
    """Abstract Base Class for LLM Inference Adapters."""
    
    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured JSON response given user and system prompt."""
        pass


class MockLLMClient(BaseLLMClient):
    """Deterministic mock client for offline testing and baseline verification."""
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        logger.info("[MockLLMClient] Generating simulated structured response.")
        return {
            "summary": "Mock diagnosis: Delivery delay is the dominant friction point in Southeast corridor.",
            "severity": "high",
            "ml_risk_assessment": {
                "dissatisfaction_risk_score": 0.78,
                "top_drivers": [
                    {"feature": "delay_days", "importance_pct": 56.4},
                    {"feature": "freight_ratio", "importance_pct": 23.8},
                    {"feature": "catalog_mismatch", "importance_pct": 19.8}
                ]
            },
            "quantitative_evidence": [
                {"metric": "low_score_share", "value": "31.4%", "baseline": "18.2%", "sample_size": 340}
            ],
            "qualitative_evidence": [
                {"review_snippet": "Produto atrasou mais de 10 dias e nao tive suporte.", "theme": "DELIVERY_DELAY"}
            ],
            "recommended_actions": [
                {
                    "action": "Audit carrier SLA for delayed routes",
                    "rationale": "56.4% of negative review variance attributed to shipping delay",
                    "effort": "medium",
                    "expected_effect": "Mitigate low ratings by 15-20% within 30 days"
                }
            ],
            "limitations": [
                "Mock response for baseline testing and demonstration"
            ]
        }


class GroqLLMClient(BaseLLMClient):
    """Client for Groq API (Free Tier, ultra-low latency, Llama-3.3-70B)."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        from groq import Groq
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        if not self.api_key or self.api_key.startswith("gsk_placeholder"):
            raise ValueError("Groq API key is missing or set to placeholder. Please configure GROQ_API_KEY in .env.")
        self.client = Groq(api_key=self.api_key)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        default_system = (
            "You are TradeForensics Copilot, an expert commerce operations diagnostic engine. "
            "You must return ONLY a valid, parseable JSON object matching the requested schema. "
            "Never invent numbers or percentages outside the provided evidence."
        )
        sys_msg = system_prompt or default_system
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=2048
        )
        content = response.choices[0].message.content
        return json.loads(content)


from backend.app.llm.fireworks_client import FireworksLLMClient


def get_llm_client() -> BaseLLMClient:
    """Factory to get active LLM client based on environment configuration."""
    provider = settings.LLM_PROVIDER.lower().strip()
    if provider == "groq":
        try:
            return GroqLLMClient()
        except ValueError as e:
            logger.warning(f"Groq client init failed ({e}), falling back to MockLLMClient.")
            return MockLLMClient()
    elif provider == "fireworks":
        try:
            return FireworksLLMClient()
        except Exception as e:
            logger.warning(f"Fireworks client init failed ({e}), falling back to MockLLMClient.")
            return MockLLMClient()
    else:
        return MockLLMClient()

