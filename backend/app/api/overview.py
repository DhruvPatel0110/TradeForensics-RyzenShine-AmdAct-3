import logging
from typing import Dict, Any, List
from fastapi import APIRouter
import pandas as pd

from backend.app.core.config import settings
from backend.app.services.kpi_service import kpi_service
from backend.app.ml.driver_explainer import driver_explainer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/overview", tags=["Store Overview"])

# In-memory cache for fast dashboard responses
_cached_overview = None

def _compute_overview_data() -> Dict[str, Any]:
    global _cached_overview
    if _cached_overview is not None:
        return _cached_overview

    logger.info("Computing store overview metrics & distributions...")
    df = pd.read_parquet(settings.PROCESSED_DATA_DIR / "orders_analytical.parquet")
    store_overview = kpi_service.get_store_overview()

    # 1. Delay distribution buckets with dissatisfaction rate
    bins = [-1, 0, 3, 7, 14, 999]
    labels = ["On Time", "1-3 Days Late", "4-7 Days Late", "8-14 Days Late", "15+ Days Late"]
    df["delay_bucket"] = pd.cut(df["delay_days"], bins=bins, labels=labels)
    
    bucket_summary = df.groupby("delay_bucket", observed=False).agg(
        order_count=("order_id", "count"),
        low_score_rate_pct=("is_low_score", lambda x: round(float(x.mean()) * 100.0, 1))
    ).reset_index()
    
    total_orders = len(df)
    delay_distribution = []
    for _, row in bucket_summary.iterrows():
        cnt = int(row["order_count"])
        delay_distribution.append({
            "bucket": str(row["delay_bucket"]),
            "order_count": cnt,
            "pct_of_orders": round((cnt / total_orders) * 100.0, 1),
            "low_score_rate_pct": float(row["low_score_rate_pct"])
        })

    # 2. Top categories benchmark (top 8 by volume)
    cat_df = kpi_service.get_category_metrics(min_reviews=50)
    top_categories = []
    for _, r in cat_df.sort_values("total_orders", ascending=False).head(8).iterrows():
        top_categories.append({
            "category": str(r["product_category_name_english"]),
            "total_orders": int(r["total_orders"]),
            "review_count": int(r["review_count"]),
            "late_delivery_rate_pct": round(float(r["late_delivery_rate_pct"]), 1),
            "low_score_rate_pct": round(float(r["low_score_rate_pct"]), 1),
            "low_score_delta": round(float(r["low_score_delta"]), 1),
            "avg_delay_days": round(float(r["avg_delay_days"]), 1)
        })

    # 3. Global ML Feature Root-Cause Drivers (LightGBM)
    global_drivers = driver_explainer.get_global_drivers(top_k=5)

    # 4. Composite Store Health Score (0-100)
    # Baseline health: 100 - (late_rate * 2.5) - (low_score_rate * 2.0)
    late_rate = store_overview["global_late_rate_pct"]
    low_rate = store_overview["global_low_score_rate_pct"]
    health_score = round(max(0.0, min(100.0, 100.0 - (late_rate * 2.0) - (low_rate * 1.5))), 1)

    _cached_overview = {
        "kpis": {
            "total_orders": store_overview["total_orders"],
            "delivered_orders": store_overview["delivered_orders"],
            "cancelled_orders": store_overview["cancelled_orders"],
            "global_late_rate_pct": late_rate,
            "global_low_score_rate_pct": low_rate,
            "global_avg_delay_days": store_overview["global_avg_delay_days"],
            "global_avg_review_score": store_overview["global_avg_review_score"],
            "store_health_score": health_score,
            "correlation_impact": {
                "on_time_low_score_pct": float(store_overview["correlation_impact"]["on_time_low_score_pct"]),
                "late_low_score_pct": float(store_overview["correlation_impact"]["late_low_score_pct"]),
                "risk_multiplier": float(store_overview["correlation_impact"]["risk_multiplier"])
            },
            "data_period": store_overview["data_period"]
        },
        "delay_distribution": delay_distribution,
        "top_categories": top_categories,
        "global_drivers": global_drivers
    }
    return _cached_overview

@router.get("", response_model=Dict[str, Any])
def get_overview():
    """Returns store-wide KPI cards, delay penalty curves, top categories, and ML drivers."""
    return _compute_overview_data()
