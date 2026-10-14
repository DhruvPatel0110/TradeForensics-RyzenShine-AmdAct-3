import pytest
import pandas as pd
from backend.app.ml.feature_builder import build_feature_matrix
from backend.app.ml.driver_explainer import driver_explainer
from backend.app.core.config import settings

def test_feature_builder():
    analytical_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    df = pd.read_parquet(analytical_file).head(100)
    X, y, cols = build_feature_matrix(df, is_training=True)
    
    assert len(X) == 100
    assert len(y) == 100
    assert "delay_days" in cols
    assert "freight_ratio" in cols
    assert "topic_DELIVERY_DELAY" in cols
    assert X.isnull().sum().sum() == 0

def test_driver_explainer_global():
    global_drivers = driver_explainer.get_global_drivers(top_k=5)
    assert len(global_drivers) == 5
    assert all("feature" in d for d in global_drivers)
    assert all("display_name" in d for d in global_drivers)
    assert all(d["importance_pct"] >= 0 for d in global_drivers)

def test_segment_risk_prediction():
    analytical_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    df = pd.read_parquet(analytical_file)
    
    # Test on a specific category
    cat_df = df[df["product_category_name_english"] == "office_furniture"]
    risk = driver_explainer.predict_segment_risk(cat_df)
    assert 0.0 <= risk <= 100.0
    
    # Test segment driver attribution
    drivers = driver_explainer.get_segment_drivers(cat_df, top_k=3)
    assert len(drivers) == 3
    assert all(d["importance_pct"] > 0 for d in drivers)

def test_late_orders_risk_higher_than_ontime():
    """Sanity check: Model should predict higher dissatisfaction risk for delayed orders."""
    analytical_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    df = pd.read_parquet(analytical_file)
    
    ontime_sample = df[(df["is_delivered"] == 1) & (df["is_late"] == 0)].sample(500, random_state=42)
    late_sample = df[(df["is_delivered"] == 1) & (df["is_late"] == 1)].sample(500, random_state=42)
    
    ontime_risk = driver_explainer.predict_segment_risk(ontime_sample)
    late_risk = driver_explainer.predict_segment_risk(late_sample)
    
    assert late_risk > ontime_risk
