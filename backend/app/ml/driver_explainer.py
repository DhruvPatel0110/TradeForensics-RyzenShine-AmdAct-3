import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import pandas as pd
import numpy as np

from backend.app.ml.feature_builder import build_feature_matrix
from backend.app.core.config import settings

logger = logging.getLogger(__name__)
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

# Human-readable operational labels
FEATURE_DISPLAY_NAMES = {
    "delay_days": "Shipping Delay (Days past deadline)",
    "transit_days": "Total Transit Duration",
    "freight_ratio": "Freight Cost Ratio (High Shipping vs Price)",
    "total_price": "High Product Price Expectation",
    "total_freight": "Excessive Freight Cost",
    "product_weight_g": "Heavy Package Transit Vulnerability",
    "product_volume_cm3": "Bulky Item Packaging Complexity",
    "is_interstate": "Interstate Route Logistics Bottleneck",
    "item_count": "Multi-Item Order Split Risk",
    "topic_DELIVERY_DELAY": "Customer Review: Shipping Delay / Missed Deadline",
    "topic_DAMAGED_DEFECTIVE": "Customer Review: Defective / Damaged Item",
    "topic_CATALOG_MISMATCH": "Customer Review: Product / Size Description Mismatch",
    "topic_SERVICE_REFUND": "Customer Review: Refund / Customer Service Dispute",
    "topic_OTHER_GENERAL": "Customer Review: General Dissatisfaction"
}

# Features that explain negative dissatisfaction (exclude positive/neutral flags)
NEGATIVE_ROOT_CAUSE_FEATURES = {
    "delay_days", "transit_days", "freight_ratio", "total_price", "total_freight",
    "product_weight_g", "product_volume_cm3", "is_interstate", "item_count",
    "topic_DELIVERY_DELAY", "topic_DAMAGED_DEFECTIVE", "topic_CATALOG_MISMATCH",
    "topic_SERVICE_REFUND", "topic_OTHER_GENERAL"
}

class DriverExplainer:
    """
    Explains dissatisfaction risk and derives segment-specific feature driver attribution.
    """

    def __init__(self, artifacts_dir: Optional[Path] = None):
        self.artifacts_dir = artifacts_dir or ARTIFACTS_DIR
        self._model = None
        self._metadata = None
        self._global_stats = None

    def _load(self):
        if self._model is None:
            model_path = self.artifacts_dir / "lgbm_risk_model.pkl"
            meta_path = self.artifacts_dir / "model_metadata.json"
            if not model_path.exists():
                raise FileNotFoundError(
                    f"LightGBM model not found at {model_path}. Train the model first."
                )
            self._model = joblib.load(model_path)
            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)

    def get_global_drivers(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """Returns the top global operational root-cause drivers across the store."""
        self._load()
        importances = self._metadata.get("global_importances", {}) if self._metadata else {}
        
        # Filter for negative root cause features
        filtered = {k: v for k, v in importances.items() if k in NEGATIVE_ROOT_CAUSE_FEATURES}
        total = sum(filtered.values()) or 1.0
        
        drivers = []
        for feat, raw_pct in filtered.items():
            norm_pct = (raw_pct / total) * 100.0
            drivers.append({
                "feature": feat,
                "display_name": FEATURE_DISPLAY_NAMES.get(feat, feat),
                "importance_pct": round(norm_pct, 1)
            })
        drivers.sort(key=lambda x: x["importance_pct"], reverse=True)
        return drivers[:top_k]

    def predict_segment_risk(self, segment_df: pd.DataFrame) -> float:
        """Computes the mean predicted dissatisfaction risk probability for a segment."""
        if segment_df.empty:
            return 0.0
        self._load()
        X, _, _ = build_feature_matrix(segment_df, is_training=False)
        probs = self._model.predict_proba(X)[:, 1]
        return round(float(np.mean(probs)) * 100.0, 1)

    def get_segment_drivers(self, segment_df: pd.DataFrame, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Calculates normalized driver attribution for a specific category or seller segment.
        Combines global tree feature importances with segment-specific feature deviations.
        """
        if segment_df.empty:
            return self.get_global_drivers(top_k)

        self._load()
        global_importances = self._metadata.get("global_importances", {}) if self._metadata else {}
        X_seg, _, feature_cols = build_feature_matrix(segment_df, is_training=False)

        # Baseline comparative attribution
        segment_weights = {}
        for col in feature_cols:
            if col not in NEGATIVE_ROOT_CAUSE_FEATURES:
                continue
            
            base_gain = global_importances.get(col, 1.0)
            
            # Segment mean activity
            seg_mean = float(X_seg[col].mean())
            
            # If it's a binary topic or interstate flag, weight directly by its rate
            if col.startswith("topic_") or col == "is_interstate":
                intensity = max(0.05, seg_mean * 2.0)
            elif col in ["delay_days", "transit_days"]:
                # Delayed shipments carry high operational penalty
                intensity = max(0.1, 1.0 + (seg_mean / 10.0))
            elif col == "freight_ratio":
                intensity = max(0.1, 1.0 + (seg_mean / 0.2))
            else:
                intensity = 1.0
                
            segment_weights[col] = base_gain * intensity

        total_weight = sum(segment_weights.values()) or 1.0
        normalized = {
            col: (val / total_weight) * 100.0 
            for col, val in segment_weights.items()
        }

        sorted_drivers = sorted(normalized.items(), key=lambda x: x[1], reverse=True)
        top_drivers = []
        for feat, pct in sorted_drivers[:top_k]:
            top_drivers.append({
                "feature": feat,
                "display_name": FEATURE_DISPLAY_NAMES.get(feat, feat),
                "importance_pct": round(pct, 1)
            })

        return top_drivers

driver_explainer = DriverExplainer()
