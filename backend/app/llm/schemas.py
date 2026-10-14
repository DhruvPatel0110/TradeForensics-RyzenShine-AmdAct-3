from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CustomerQuote(BaseModel):
    order_id: str = Field(description="Olist order identifier")
    review_snippet: str = Field(description="Authentic customer Portuguese review text")
    review_score: int = Field(description="Customer rating 1-5")
    delay_days: float = Field(default=0.0, description="Delivery delay in days")
    complaint_topic: str = Field(description="NLP classified complaint category")
    similarity_score: float = Field(default=0.0, description="Vector search cosine similarity")

class FeatureDriver(BaseModel):
    feature_name: str
    importance_pct: float
    direction: str = Field(description="e.g., 'elevated', 'high', 'interstate'")
    display_label: str

class DeterministicMetrics(BaseModel):
    sample_size: int
    total_orders: int
    low_score_rate_pct: float
    store_baseline_low_score_pct: float
    low_score_delta: float
    late_delivery_rate_pct: float
    store_baseline_late_rate_pct: float
    late_rate_delta: float
    avg_delay_days: float

class EvidencePacket(BaseModel):
    issue_id: str
    entity_type: str  # "category" or "seller"
    entity_name: str
    issue_type: str
    primary_driver: str
    severity_score: float
    deterministic_kpis: DeterministicMetrics
    ml_risk_assessment: Dict[str, Any]
    qualitative_quotes: List[CustomerQuote]

class ActionItem(BaseModel):
    priority: int = Field(ge=1, le=5, description="Priority ranking 1-5")
    title: str = Field(description="Concise action item title")
    category: str = Field(description="LOGISTICS | SUPPLIER_QUALITY | CATALOG_ACCURACY | CUSTOMER_SERVICE")
    action: str = Field(description="Specific, practical operational step")
    rationale: str = Field(description="Grounding explanation referencing specific evidence packet numbers or quotes")
    effort: str = Field(description="LOW | MEDIUM | HIGH")
    expected_effect: str = Field(description="Measurable operational outcome expected")
    responsible_team: str = Field(description="e.g., Fulfillment Logistics, Merchant Management, Catalog Ops")

class ActionPlanResponse(BaseModel):
    issue_id: str
    entity_name: str
    issue_type: str
    severity_level: str = Field(description="CRITICAL | HIGH | MEDIUM | LOW")
    executive_summary: str = Field(description="High-level operational diagnosis grounded strictly in the data")
    key_findings: List[str] = Field(description="Bullet points synthesizing evidence without inventing numbers")
    ml_driver_summary: str = Field(description="Explanation of LightGBM risk model drivers")
    qualitative_signals: List[str] = Field(description="Direct synthesis of authentic customer quotes")
    recommended_actions: List[ActionItem] = Field(description="3 to 5 prioritized, actionable operational steps")
    grounded_metrics_cited: Dict[str, Any] = Field(description="Exact numbers cited from the evidence packet")
    data_limitations: str = Field(description="Sample size caveats, observational study boundaries")
