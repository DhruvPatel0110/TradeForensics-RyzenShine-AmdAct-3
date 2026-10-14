import logging
from typing import Tuple, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

NUMERICAL_FEATURES = [
    "delay_days",
    "transit_days",
    "freight_ratio",
    "total_price",
    "total_freight",
    "product_weight_g",
    "product_volume_cm3",
    "is_interstate",
    "item_count"
]

CATEGORICAL_FEATURES = [
    "complaint_topic"
]

def build_feature_matrix(
    df: pd.DataFrame, 
    is_training: bool = True
) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str]]:
    """
    Constructs clean numerical & encoded features for LightGBM training / inference.
    Handles missing values and categorical encoding.
    """
    feature_df = pd.DataFrame(index=df.index)
    
    # 1. Numerical Features with safe imputation
    feature_df["delay_days"] = df["delay_days"].fillna(0.0).astype(float)
    feature_df["transit_days"] = df["transit_days"].fillna(df["transit_days"].median()).astype(float)
    feature_df["freight_ratio"] = df["freight_ratio"].fillna(0.2).astype(float)
    feature_df["total_price"] = df["total_price"].fillna(df["total_price"].median()).astype(float)
    feature_df["total_freight"] = df["total_freight"].fillna(df["total_freight"].median()).astype(float)
    feature_df["product_weight_g"] = df["product_weight_g"].fillna(df["product_weight_g"].median()).astype(float)
    feature_df["product_volume_cm3"] = df["product_volume_cm3"].fillna(df["product_volume_cm3"].median()).astype(float)
    feature_df["is_interstate"] = df["is_interstate"].fillna(0).astype(int)
    feature_df["item_count"] = df["item_count"].fillna(1).astype(int)
    
    # 2. Categorical: one-hot encode complaint_topic
    topics = ["DELIVERY_DELAY", "DAMAGED_DEFECTIVE", "CATALOG_MISMATCH", "SERVICE_REFUND", "POSITIVE_SATISFACTION", "NO_COMMENT", "OTHER_GENERAL"]
    topic_series = df["complaint_topic"].fillna("NO_COMMENT") if "complaint_topic" in df.columns else pd.Series("NO_COMMENT", index=df.index)
    
    for t in topics:
        feature_df[f"topic_{t}"] = (topic_series == t).astype(int)
        
    feature_cols = list(feature_df.columns)
    
    target_series = None
    if is_training and "is_low_score" in df.columns:
        target_series = df["is_low_score"].astype(int)
        
    return feature_df, target_series, feature_cols
