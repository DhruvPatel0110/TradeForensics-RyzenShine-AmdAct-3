import pytest
from backend.app.services.evidence_assembler import evidence_assembler
from backend.app.services.copilot_service import copilot_service
from backend.app.llm.schemas import EvidencePacket, ActionPlanResponse

def test_evidence_assembler_category():
    packet = evidence_assembler.assemble_evidence("cat_office_furniture")
    assert isinstance(packet, EvidencePacket)
    assert packet.entity_name == "office_furniture"
    assert packet.entity_type == "category"
    assert packet.severity_score > 0
    assert packet.deterministic_kpis.sample_size >= 1000
    assert packet.deterministic_kpis.low_score_delta > 0
    assert "predicted_risk_pct" in packet.ml_risk_assessment
    assert len(packet.ml_risk_assessment["top_drivers"]) > 0
    assert len(packet.qualitative_quotes) == 4
    for q in packet.qualitative_quotes:
        assert len(q.review_snippet) > 0
        assert q.review_score <= 2

def test_evidence_assembler_seller():
    seller_id = "seller_1ca7077d890b907f89be8c954a02686a"
    packet = evidence_assembler.assemble_evidence(seller_id)
    assert isinstance(packet, EvidencePacket)
    assert packet.entity_type == "seller"
    assert "1ca7077d" in packet.entity_name
    assert packet.deterministic_kpis.sample_size > 0
    assert packet.deterministic_kpis.total_orders > 0
    assert packet.severity_score >= 30.0  # Top problem seller has high severity

def test_action_plan_generation_category():
    plan = copilot_service.generate_action_plan("cat_office_furniture")
    assert isinstance(plan, ActionPlanResponse)
    assert plan.issue_id == "cat_office_furniture"
    assert plan.severity_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert len(plan.executive_summary) > 50
    assert len(plan.key_findings) >= 3
    assert len(plan.recommended_actions) >= 3
    
    # Check action items structure
    for act in plan.recommended_actions:
        assert act.priority >= 1
        assert act.category in ["LOGISTICS", "SUPPLIER_QUALITY", "CATALOG_ACCURACY", "CUSTOMER_SERVICE"]
        assert len(act.title) > 0
        assert len(act.action) > 10
        assert len(act.rationale) > 10
        assert act.effort in ["LOW", "MEDIUM", "HIGH"]
        assert len(act.responsible_team) > 0

    # Ensure cited metrics match empirical data
    assert plan.grounded_metrics_cited["sample_size"] == plan.grounded_metrics_cited["sample_size"]
    assert plan.grounded_metrics_cited["low_score_rate_pct"] > 0

def test_action_plan_generation_seller():
    plan = copilot_service.generate_action_plan("seller_1ca7077d890b907f89be8c954a02686a")
    assert isinstance(plan, ActionPlanResponse)
    assert "1ca7077d" in plan.entity_name
    assert plan.severity_level == "CRITICAL"  # Over 40 severity is CRITICAL
    assert len(plan.recommended_actions) >= 3
    assert len(plan.qualitative_signals) > 0

def test_ask_copilot_query():
    resp = copilot_service.ask_copilot(
        issue_id="cat_office_furniture",
        question="Why are customers unhappy with office furniture?"
    )
    assert isinstance(resp, dict)
    assert "answer" in resp
    assert len(resp["answer"]) > 20
    assert "cited_metrics" in resp
    assert resp["cited_metrics"]["low_score_rate_pct"] > 0
