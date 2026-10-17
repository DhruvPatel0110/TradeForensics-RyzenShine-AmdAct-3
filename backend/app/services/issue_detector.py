import math
from typing import Dict, Any, List
import pandas as pd
from backend.app.services.kpi_service import kpi_service

class IssueDetector:
    """
    Ranks operational friction points across categories and sellers
    using the transparent mathematical severity formula:
    Severity = (Delta_low_score * 0.6 + Delta_late_delivery * 0.4) * log10(N_reviews)
    """

    def detect_top_issues(self, top_n: int = 50, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        category_df = kpi_service.get_category_metrics(min_reviews=30)
        seller_df = kpi_service.get_seller_metrics(min_reviews=30)
        baseline = kpi_service.get_store_overview()

        issues = []

        # 1. Process Category Issues (if entity_type is None or 'category')
        if entity_type is None or entity_type == "category":
            for _, row in category_df.iterrows():
                low_score_delta = max(0.0, float(row["low_score_delta"]))
                late_delta = max(0.0, float(row["late_rate_delta"]))
                sample_size = int(row["review_count"])

                if low_score_delta <= 0 and late_delta <= 0:
                    continue

                log_sample = math.log10(max(10, sample_size))
                severity_score = (low_score_delta * 0.6 + late_delta * 0.4) * log_sample

                if late_delta > low_score_delta:
                    issue_type = "LOGISTICS_BOTTLENECK"
                    primary_driver = f"Late delivery rate is +{late_delta:.1f}% above store baseline"
                else:
                    issue_type = "CATEGORY_SATISFACTION_DROP"
                    primary_driver = f"Low-rating share (<= 2 stars) is +{low_score_delta:.1f}% above store baseline"

                issues.append({
                    "issue_id": f"cat_{row['product_category_name_english']}",
                    "entity_type": "category",
                    "entity_name": row["product_category_name_english"],
                    "issue_type": issue_type,
                    "primary_driver": primary_driver,
                    "severity_score": round(severity_score, 2),
                    "metrics": {
                        "sample_size": sample_size,
                        "total_orders": int(row["total_orders"]),
                        "low_score_rate_pct": round(float(row["low_score_rate_pct"]), 1),
                        "store_baseline_low_score_pct": baseline["global_low_score_rate_pct"],
                        "low_score_delta": round(float(row["low_score_delta"]), 1),
                        "late_delivery_rate_pct": round(float(row["late_delivery_rate_pct"]), 1),
                        "store_baseline_late_rate_pct": baseline["global_late_rate_pct"],
                        "late_rate_delta": round(float(row["late_rate_delta"]), 1),
                        "avg_delay_days": round(float(row["avg_delay_days"]), 1)
                    }
                })

        # 2. Process Seller Issues (if entity_type is None or 'seller')
        if entity_type is None or entity_type == "seller":
            for _, row in seller_df.iterrows():
                low_score_delta = max(0.0, float(row["low_score_delta"]))
                late_delta = max(0.0, float(row["late_rate_delta"]))
                sample_size = int(row["review_count"])

                if low_score_delta <= 0 and late_delta <= 0:
                    continue

                log_sample = math.log10(max(10, sample_size))
                severity_score = (low_score_delta * 0.6 + late_delta * 0.4) * log_sample

                seller_short_id = str(row["seller_id"])[:8]
                location = f"{row['seller_city']}/{row['seller_state']}"

                if late_delta > low_score_delta:
                    issue_type = "SELLER_LOGISTICS_BOTTLENECK"
                    primary_driver = f"Seller {seller_short_id} has +{late_delta:.1f}% late deliveries ({location})"
                else:
                    issue_type = "SELLER_SATISFACTION_DROP"
                    primary_driver = f"Seller {seller_short_id} has +{low_score_delta:.1f}% negative reviews ({location})"

                issues.append({
                    "issue_id": f"seller_{row['seller_id']}",
                    "entity_type": "seller",
                    "entity_name": f"Seller {seller_short_id} ({location})",
                    "issue_type": issue_type,
                    "primary_driver": primary_driver,
                    "severity_score": round(severity_score, 2),
                    "metrics": {
                        "sample_size": sample_size,
                        "total_orders": int(row["total_orders"]),
                        "low_score_rate_pct": round(float(row["low_score_rate_pct"]), 1),
                        "store_baseline_low_score_pct": baseline["global_low_score_rate_pct"],
                        "low_score_delta": round(float(row["low_score_delta"]), 1),
                        "late_delivery_rate_pct": round(float(row["late_delivery_rate_pct"]), 1),
                        "store_baseline_late_rate_pct": baseline["global_late_rate_pct"],
                        "late_rate_delta": round(float(row["late_rate_delta"]), 1),
                        "avg_delay_days": round(float(row["avg_delay_days"]), 1)
                    }
                })

        # Sort descending by severity score
        issues.sort(key=lambda x: x["severity_score"], reverse=True)
        return issues[:top_n]

issue_detector = IssueDetector()
