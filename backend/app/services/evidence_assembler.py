import logging
from typing import Optional
from pathlib import Path
import pandas as pd

from backend.app.core.config import settings
from backend.app.services.kpi_service import kpi_service
from backend.app.ml.driver_explainer import driver_explainer
from backend.app.rag.retriever import review_retriever
from backend.app.llm.schemas import (
    EvidencePacket,
    DeterministicMetrics,
    CustomerQuote
)

logger = logging.getLogger(__name__)

class EvidenceAssembler:
    """
    Assembles grounded evidence packets for operational issues by fusing:
    1. Deterministic SQL KPIs (volumes, deltas, rates).
    2. LightGBM tabular ML predicted risk and feature drivers.
    3. ChromaDB vector store authentic Brazilian Portuguese customer quotes.
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.PROCESSED_DATA_DIR / "orders_analytical.parquet")
        self._df: Optional[pd.DataFrame] = None

    def _get_df(self) -> pd.DataFrame:
        if self._df is None:
            if not self.data_path.exists():
                raise FileNotFoundError(f"Analytical orders data not found at {self.data_path}")
            logger.info(f"Loading analytical dataframe into EvidenceAssembler from {self.data_path}...")
            self._df = pd.read_parquet(self.data_path)
        return self._df

    def assemble_evidence(self, issue_id: str) -> EvidencePacket:
        """
        Builds a comprehensive EvidencePacket for a given issue ID
        (e.g., 'cat_office_furniture' or 'seller_1ca7077d890b907f89be8c954a02686a').
        """
        df = self._get_df()
        store_overview = kpi_service.get_store_overview()

        # 1. Determine entity type and filter dataset
        if issue_id.startswith("cat_"):
            entity_type = "category"
            entity_name = issue_id[4:]
            segment_df = df[df["product_category_name_english"] == entity_name]
            quotes = review_retriever.get_representative_complaints(category=entity_name, top_k=4)
        elif issue_id.startswith("seller_"):
            entity_type = "seller"
            seller_id = issue_id[7:]
            segment_df = df[df["seller_id"] == seller_id]
            seller_short = seller_id[:8]
            
            # Extract seller location from segment if available
            location = "Brazil"
            if not segment_df.empty and "seller_city" in segment_df.columns and "seller_state" in segment_df.columns:
                city = segment_df["seller_city"].iloc[0]
                state = segment_df["seller_state"].iloc[0]
                location = f"{city}/{state}"
            entity_name = f"Seller {seller_short} ({location})"
            quotes = review_retriever.get_representative_complaints(seller_id=seller_id, top_k=4)
        else:
            raise ValueError(f"Invalid issue_id format '{issue_id}'. Expected 'cat_<name>' or 'seller_<id>'")

        # 2. Deterministic KPI computation
        total_orders = len(segment_df)
        review_count = int(segment_df["review_score"].notna().sum()) if not segment_df.empty else 0
        
        if review_count > 0:
            low_scores = int((segment_df["review_score"] <= 2).sum())
            low_score_rate = round((low_scores / review_count) * 100.0, 1)
        else:
            low_score_rate = 0.0

        if total_orders > 0:
            late_orders = int((segment_df["delay_days"] > 0).sum())
            late_rate = round((late_orders / total_orders) * 100.0, 1)
            delayed_orders = segment_df[segment_df["delay_days"] > 0]
            avg_delay = round(float(delayed_orders["delay_days"].mean()), 1) if not delayed_orders.empty else 0.0
        else:
            late_rate = 0.0
            avg_delay = 0.0

        base_low = store_overview["global_low_score_rate_pct"]
        base_late = store_overview["global_late_rate_pct"]
        low_delta = round(max(0.0, low_score_rate - base_low), 1)
        late_delta = round(max(0.0, late_rate - base_late), 1)

        # Classify issue type and primary driver
        if late_delta > low_delta:
            issue_type = "LOGISTICS_BOTTLENECK" if entity_type == "category" else "SELLER_LOGISTICS_BOTTLENECK"
            primary_driver = f"Late delivery rate is +{late_delta:.1f}% above store baseline ({avg_delay:.1f}d avg delay)"
        else:
            issue_type = "CATEGORY_SATISFACTION_DROP" if entity_type == "category" else "SELLER_SATISFACTION_DROP"
            primary_driver = f"Negative rating rate (<= 2 stars) is +{low_delta:.1f}% above store baseline"

        import math
        log_n = math.log10(max(10, review_count))
        severity = round((low_delta * 0.6 + late_delta * 0.4) * log_n, 2)

        deterministic_metrics = DeterministicMetrics(
            sample_size=review_count,
            total_orders=total_orders,
            low_score_rate_pct=low_score_rate,
            store_baseline_low_score_pct=base_low,
            low_score_delta=low_delta,
            late_delivery_rate_pct=late_rate,
            store_baseline_late_rate_pct=base_late,
            late_rate_delta=late_delta,
            avg_delay_days=avg_delay
        )

        # 3. Tabular ML Risk & Drivers (LightGBM)
        predicted_risk = driver_explainer.predict_segment_risk(segment_df)
        top_drivers = driver_explainer.get_segment_drivers(segment_df, top_k=4)

        ml_assessment = {
            "predicted_risk_pct": predicted_risk,
            "top_drivers": top_drivers
        }

        # 4. Qualitative Customer Quotes
        customer_quotes = [
            CustomerQuote(
                order_id=q["order_id"],
                review_snippet=q["review_snippet"],
                review_score=q["review_score"],
                delay_days=q["delay_days"],
                complaint_topic=q["complaint_topic"],
                similarity_score=q["similarity_score"]
            )
            for q in quotes
        ]

        return EvidencePacket(
            issue_id=issue_id,
            entity_type=entity_type,
            entity_name=entity_name,
            issue_type=issue_type,
            primary_driver=primary_driver,
            severity_score=severity,
            deterministic_kpis=deterministic_metrics,
            ml_risk_assessment=ml_assessment,
            qualitative_quotes=customer_quotes
        )

evidence_assembler = EvidenceAssembler()
