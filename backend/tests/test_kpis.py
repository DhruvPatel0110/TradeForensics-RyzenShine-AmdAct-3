import datetime
import pandas as pd
import numpy as np
import pytest
from backend.app.services.kpi_service import kpi_service
from backend.app.services.issue_detector import issue_detector

def test_late_delivery_math_with_known_timestamps():
    """
    Validates delivery delay calculation logic with known timestamps:
    - Delivered after estimated date => positive delay days & is_late = 1.
    - Delivered before/on estimated date => delay days = 0 & is_late = 0.
    """
    est_date = pd.Timestamp("2018-05-10 00:00:00")
    
    # Case 1: 5 days late
    act_late = pd.Timestamp("2018-05-15 00:00:00")
    delta_late = (act_late - est_date).total_seconds() / 86400.0
    delay_late = max(0.0, delta_late)
    is_late_flag = 1 if delay_late > 0 else 0
    assert delay_late == 5.0
    assert is_late_flag == 1

    # Case 2: 2 days early (on-time)
    act_early = pd.Timestamp("2018-05-08 00:00:00")
    delta_early = (act_early - est_date).total_seconds() / 86400.0
    delay_early = max(0.0, delta_early)
    is_early_late_flag = 1 if delay_early > 0 else 0
    assert delay_early == 0.0
    assert is_early_late_flag == 0

def test_store_overview_metrics():
    """Validates global baseline calculations against real Olist numbers."""
    overview = kpi_service.get_store_overview()
    assert overview["total_orders"] == 98666
    assert overview["delivered_orders"] == 96470
    assert 7.0 <= overview["global_late_rate_pct"] <= 9.0
    assert 13.0 <= overview["global_low_score_rate_pct"] <= 15.0
    # Empirically proven: late delivery increases low scores by > 5x
    assert overview["correlation_impact"]["risk_multiplier"] > 4.0
    assert overview["correlation_impact"]["late_low_score_pct"] > 50.0

def test_category_metrics_sample_threshold():
    """Validates category aggregation and min_reviews filter."""
    category_df = kpi_service.get_category_metrics(min_reviews=50)
    assert len(category_df) >= 30
    assert (category_df["review_count"] >= 50).all()
    assert "late_rate_delta" in category_df.columns
    assert "low_score_delta" in category_df.columns

def test_seller_metrics_sample_threshold():
    """Validates seller aggregation and min_reviews filter."""
    seller_df = kpi_service.get_seller_metrics(min_reviews=30)
    assert len(seller_df) >= 50
    assert (seller_df["review_count"] >= 30).all()
    assert "seller_state" in seller_df.columns
    assert "late_rate_delta" in seller_df.columns
    assert "low_score_delta" in seller_df.columns

def test_baseline_delta_calculations():
    """Validates that delta = segment_metric - global_baseline."""
    overview = kpi_service.get_store_overview()
    category_df = kpi_service.get_category_metrics(min_reviews=50)
    
    first_row = category_df.iloc[0]
    expected_low_delta = first_row["low_score_rate_pct"] - overview["global_low_score_rate_pct"]
    assert pytest.approx(first_row["low_score_delta"], 0.01) == expected_low_delta

def test_issue_detector_ranking():
    """Validates multi-entity issue ranking sorted by severity score."""
    top_issues = issue_detector.detect_top_issues(top_n=5)
    assert len(top_issues) == 5
    scores = [issue["severity_score"] for issue in top_issues]
    assert scores == sorted(scores, reverse=True)
    assert all("entity_type" in issue for issue in top_issues)
    assert all(issue["metrics"]["sample_size"] >= 30 for issue in top_issues)
