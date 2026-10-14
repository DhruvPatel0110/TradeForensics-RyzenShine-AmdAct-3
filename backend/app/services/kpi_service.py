from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from backend.app.core.config import settings

class KPIService:
    """
    Deterministic KPI Engine for TradeForensics.
    Calculates authoritative store-wide and segmented metrics without AI guessing.
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.PROCESSED_DATA_DIR / "orders_analytical.parquet")
        self._df: Optional[pd.DataFrame] = None

    def get_data(self) -> pd.DataFrame:
        if self._df is None:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Analytical dataset not found at: {self.data_path}. Run preparation script first.")
            self._df = pd.read_parquet(self.data_path)
        return self._df

    def get_store_overview(self) -> Dict[str, Any]:
        """Calculates global store-wide baseline KPIs and distributions."""
        df = self.get_data()
        
        total_orders = len(df)
        delivered_df = df[df["is_delivered"] == 1]
        delivered_orders = len(delivered_df)
        cancelled_orders = len(df[df["order_status"] == "canceled"])
        
        # Late delivery metrics
        late_orders = delivered_df[delivered_df["is_late"] == 1]
        late_count = len(late_orders)
        late_rate_pct = (late_count / delivered_orders * 100.0) if delivered_orders > 0 else 0.0
        avg_delay_days = float(late_orders["delay_days"].mean()) if late_count > 0 else 0.0
        
        # Review metrics
        reviews_valid = df[df["review_score"].notnull()]
        total_reviews = len(reviews_valid)
        low_score_count = len(df[df["is_low_score"] == 1])
        low_score_rate_pct = (low_score_count / total_reviews * 100.0) if total_reviews > 0 else 0.0
        avg_review_score = float(reviews_valid["review_score"].mean()) if total_reviews > 0 else 0.0
        
        # Correlation between delay and bad reviews
        on_time_df = delivered_df[delivered_df["is_late"] == 0]
        on_time_low_score_pct = (on_time_df["is_low_score"].mean() * 100.0) if len(on_time_df) > 0 else 0.0
        late_low_score_pct = (late_orders["is_low_score"].mean() * 100.0) if len(late_orders) > 0 else 0.0
        
        # Date coverage
        min_date = df["order_purchase_timestamp"].min()
        max_date = df["order_purchase_timestamp"].max()
        
        return {
            "total_orders": total_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "global_late_rate_pct": round(late_rate_pct, 2),
            "global_avg_delay_days": round(avg_delay_days, 1),
            "global_low_score_rate_pct": round(low_score_rate_pct, 2),
            "global_avg_review_score": round(avg_review_score, 2),
            "correlation_impact": {
                "on_time_low_score_pct": round(on_time_low_score_pct, 2),
                "late_low_score_pct": round(late_low_score_pct, 2),
                "risk_multiplier": round(late_low_score_pct / on_time_low_score_pct, 2) if on_time_low_score_pct > 0 else 0.0
            },
            "data_period": {
                "start": min_date.strftime("%Y-%m-%d") if pd.notnull(min_date) else None,
                "end": max_date.strftime("%Y-%m-%d") if pd.notnull(max_date) else None
            }
        }

    def get_category_metrics(self, min_reviews: int = 50) -> pd.DataFrame:
        """Calculates performance by product category with minimum sample guard."""
        df = self.get_data()
        baseline = self.get_store_overview()
        
        agg = df.groupby("product_category_name_english").agg(
            total_orders=("order_id", "count"),
            delivered_orders=("is_delivered", "sum"),
            late_orders=("is_late", "sum"),
            avg_delay_days=("delay_days", lambda s: s[s > 0].mean() if len(s[s > 0]) > 0 else 0.0),
            review_count=("review_score", "count"),
            avg_review_score=("review_score", "mean"),
            low_score_count=("is_low_score", "sum")
        ).reset_index()
        
        # Filter minimum reviews
        agg = agg[agg["review_count"] >= min_reviews].copy()
        
        # Rates
        agg["late_delivery_rate_pct"] = np.where(
            agg["delivered_orders"] > 0, 
            (agg["late_orders"] / agg["delivered_orders"]) * 100.0, 
            0.0
        )
        agg["low_score_rate_pct"] = (agg["low_score_count"] / agg["review_count"]) * 100.0
        
        # Baseline deltas
        agg["late_rate_delta"] = agg["late_delivery_rate_pct"] - baseline["global_late_rate_pct"]
        agg["low_score_delta"] = agg["low_score_rate_pct"] - baseline["global_low_score_rate_pct"]
        
        return agg

    def get_seller_metrics(self, min_reviews: int = 30) -> pd.DataFrame:
        """Calculates performance by seller with minimum sample guard."""
        df = self.get_data()
        baseline = self.get_store_overview()
        
        agg = df.groupby(["seller_id", "seller_state", "seller_city"]).agg(
            total_orders=("order_id", "count"),
            delivered_orders=("is_delivered", "sum"),
            late_orders=("is_late", "sum"),
            avg_delay_days=("delay_days", lambda s: s[s > 0].mean() if len(s[s > 0]) > 0 else 0.0),
            review_count=("review_score", "count"),
            avg_review_score=("review_score", "mean"),
            low_score_count=("is_low_score", "sum")
        ).reset_index()
        
        # Filter minimum reviews
        agg = agg[agg["review_count"] >= min_reviews].copy()
        
        # Rates
        agg["late_delivery_rate_pct"] = np.where(
            agg["delivered_orders"] > 0, 
            (agg["late_orders"] / agg["delivered_orders"]) * 100.0, 
            0.0
        )
        agg["low_score_rate_pct"] = (agg["low_score_count"] / agg["review_count"]) * 100.0
        
        # Baseline deltas
        agg["late_rate_delta"] = agg["late_delivery_rate_pct"] - baseline["global_late_rate_pct"]
        agg["low_score_delta"] = agg["low_score_rate_pct"] - baseline["global_low_score_rate_pct"]
        
        return agg

kpi_service = KPIService()
