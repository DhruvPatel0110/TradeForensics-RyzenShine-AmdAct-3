import json
from typing import Dict, Any
from backend.app.llm.schemas import EvidencePacket

COPILOT_SYSTEM_PROMPT = """You are the TradeForensics AI Action Copilot, an enterprise-grade operational diagnostic engine for multi-vendor e-commerce marketplaces (RyzenShine team, AMD Developer Hackathon ACT III).

YOUR CORE DIRECTIVE: EVIDENCE-BOUNDED REASONING.
You must generate a structured, highly actionable operational diagnosis and remediation plan for an e-commerce merchant or platform operator.

CRITICAL ANTI-HALLUCINATION RULES:
1. NEVER INVENT METRICS: Do not compute or invent percentages, sample sizes, order volumes, or dollar values. Every metric you state MUST be directly drawn from the provided Evidence Packet.
2. CITATION OF HUMAN GROUND TRUTH: You must reference the authentic customer review quotes provided in the qualitative evidence to support why customers are dissatisfied.
3. CLEAR PRIORITIZATION: Provide 3 to 5 concrete operational actions. Each action must have an assigned responsible team (e.g., 'Fulfillment Logistics', 'Supplier Quality', 'Catalog Operations'), an estimated effort level (LOW, MEDIUM, HIGH), and an expected measurable outcome.
4. HONEST LIMITATIONS: Explicitly acknowledge observational data constraints and sample size boundaries in the 'data_limitations' field.
5. STRICT JSON OUTPUT: You MUST return a single, valid JSON object matching the requested schema. No surrounding text, no markdown backticks, just valid JSON.
"""

def generate_action_plan_user_prompt(packet: EvidencePacket) -> str:
    """Formats the EvidencePacket into a clean, structured context for the LLM."""
    kpis = packet.deterministic_kpis
    ml = packet.ml_risk_assessment
    quotes = packet.qualitative_quotes

    formatted_quotes = []
    for i, q in enumerate(quotes, 1):
        formatted_quotes.append(
            f'  [{i}] (Score: {q.review_score}★ | Delay: {q.delay_days:.1f}d | Topic: {q.complaint_topic} | Order: {q.order_id})\n'
            f'      Quote: "{q.review_snippet}"'
        )
    quotes_str = "\n".join(formatted_quotes) if formatted_quotes else "  (No direct customer quotes available)"

    prompt = f"""EVIDENCE PACKET FOR OPERATIONAL ISSUE: {packet.issue_id}
======================================================================
1. ENTITY & CLASSIFICATION:
   - Target Entity: {packet.entity_name} ({packet.entity_type.upper()})
   - Issue Type: {packet.issue_type}
   - Severity Score: {packet.severity_score:.1f}
   - Primary Symptom: {packet.primary_driver}

2. DETERMINISTIC SQL METRICS:
   - Total Orders Evaluated: {kpis.total_orders:,d}
   - Review Sample Size (N): {kpis.sample_size:,d}
   - Negative Review Rate (<= 2 stars): {kpis.low_score_rate_pct:.1f}% (Store Baseline: {kpis.store_baseline_low_score_pct:.1f}%, Delta: +{kpis.low_score_delta:.1f}%)
   - Late Delivery Rate: {kpis.late_delivery_rate_pct:.1f}% (Store Baseline: {kpis.store_baseline_late_rate_pct:.1f}%, Delta: +{kpis.late_rate_delta:.1f}%)
   - Average Delay on Late Orders: {kpis.avg_delay_days:.1f} days

3. TABULAR ML RISK & DRIVER ATTRIBUTION (LightGBM):
   - Predicted Segment Risk Probability: {ml.get('predicted_risk_pct', 'N/A')}%
   - Top Risk Drivers:
{json.dumps(ml.get('top_drivers', []), indent=5)}

4. QUALITATIVE REAL CUSTOMER EVIDENCE (ChromaDB Semantic Search):
{quotes_str}

======================================================================
TASK INSTRUCTIONS:
Using ONLY the verified evidence above, generate an ActionPlanResponse JSON object with:
- "issue_id": "{packet.issue_id}"
- "entity_name": "{packet.entity_name}"
- "issue_type": "{packet.issue_type}"
- "severity_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
- "executive_summary": 2-3 concise sentences diagnosing the core bottleneck.
- "key_findings": 3-4 bullet points synthesizing the metrics above.
- "ml_driver_summary": Explanation of how the LightGBM drivers explain this issue.
- "qualitative_signals": 2-3 sentences synthesizing the customer quotes and emotional distress signals.
- "recommended_actions": 3 to 5 prioritized ActionItem objects (priority, title, category, action, rationale, effort, expected_effect, responsible_team).
- "grounded_metrics_cited": Key numbers cited from section 2.
- "data_limitations": Specific data constraints (e.g., historical Olist observational data, sample size).
"""
    return prompt
