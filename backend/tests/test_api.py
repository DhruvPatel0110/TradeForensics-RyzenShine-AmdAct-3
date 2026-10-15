import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "TradeForensics"
    assert data["team"] == "RyzenShine"
    assert data["dataset_rows"] == 98666
    assert data["ml_model_status"] == "ready"
    assert data["nlp_classifier_status"] == "ready"

def test_overview_endpoint(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    
    # KPIs check
    assert "kpis" in data
    kpis = data["kpis"]
    assert kpis["total_orders"] == 98666
    assert kpis["global_late_rate_pct"] > 7.0
    assert kpis["global_low_score_rate_pct"] > 13.0
    assert "store_health_score" in kpis
    assert "correlation_impact" in kpis
    assert kpis["correlation_impact"]["risk_multiplier"] > 5.0
    
    # Delay distribution check
    assert "delay_distribution" in data
    assert len(data["delay_distribution"]) == 5
    assert data["delay_distribution"][0]["bucket"] == "On Time"
    assert data["delay_distribution"][0]["order_count"] > 80000

    # Top categories and drivers
    assert "top_categories" in data
    assert len(data["top_categories"]) > 0
    assert "global_drivers" in data
    assert len(data["global_drivers"]) > 0

def test_list_issues_endpoint(client):
    response = client.get("/api/issues?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "issues" in data
    assert len(data["issues"]) == 10
    assert data["issues"][0]["severity_score"] > 0
    assert "entity_name" in data["issues"][0]
    assert "primary_driver" in data["issues"][0]

def test_filter_issues_by_entity_type(client):
    response = client.get("/api/issues?entity_type=category&limit=5")
    assert response.status_code == 200
    data = response.json()
    for iss in data["issues"]:
        assert iss["entity_type"] == "category"

def test_get_issue_detail(client):
    response = client.get("/api/issues/cat_office_furniture")
    assert response.status_code == 200
    data = response.json()
    assert data["issue_id"] == "cat_office_furniture"
    assert data["entity_type"] == "category"

def test_get_nonexistent_issue_404(client):
    response = client.get("/api/issues/cat_nonexistent_xyz_123")
    assert response.status_code == 404

def test_get_issue_evidence(client):
    response = client.get("/api/issues/cat_office_furniture/evidence")
    assert response.status_code == 200
    data = response.json()
    assert data["issue_id"] == "cat_office_furniture"
    assert "deterministic_kpis" in data
    assert data["deterministic_kpis"]["sample_size"] > 1000
    assert "ml_risk_assessment" in data
    assert data["ml_risk_assessment"]["predicted_risk_pct"] > 0
    assert "qualitative_quotes" in data
    assert len(data["qualitative_quotes"]) == 4

def test_create_action_plan_endpoint(client):
    payload = {"issue_id": "cat_office_furniture"}
    response = client.post("/api/action-plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["issue_id"] == "cat_office_furniture"
    assert data["severity_level"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    assert len(data["executive_summary"]) > 20
    assert len(data["recommended_actions"]) >= 3
    for act in data["recommended_actions"]:
        assert act["priority"] >= 1
        assert act["category"] in ["LOGISTICS", "SUPPLIER_QUALITY", "CATALOG_ACCURACY", "CUSTOMER_SERVICE"]
        assert len(act["title"]) > 0
        assert len(act["action"]) > 0
        assert len(act["rationale"]) > 0

def test_ask_copilot_endpoint(client):
    payload = {
        "issue_id": "cat_office_furniture",
        "question": "What is causing the delay in this category?"
    }
    response = client.post("/api/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["issue_id"] == "cat_office_furniture"
    assert len(data["answer"]) > 10
    assert "cited_metrics" in data
    assert len(data["recommended_next_step"]) > 0
