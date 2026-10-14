import json
import logging
from pathlib import Path
from typing import Dict, Any
import joblib
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, 
    classification_report, 
    precision_score, 
    recall_score, 
    f1_score
)

from backend.app.core.config import settings
from backend.app.ml.feature_builder import build_feature_matrix

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def train_dissatisfaction_risk_model(data_path: Path) -> Dict[str, Any]:
    """
    Trains a LightGBM Classifier to predict customer dissatisfaction risk (review <= 2)
    using order operational features, freight ratios, and NLP complaint topics.
    """
    logger.info(f"Loading data from {data_path} for LightGBM risk model training...")
    df = pd.read_parquet(data_path)
    
    # Build feature matrix and target
    X, y, feature_cols = build_feature_matrix(df, is_training=True)
    logger.info(f"Features constructed: {len(feature_cols)} dimensions across {len(X):,d} records.")
    
    # Stratified train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train LightGBM Classifier
    logger.info("Fitting LGBMClassifier(n_estimators=150, learning_rate=0.05, max_depth=6)...")
    clf = LGBMClassifier(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=6,
        class_weight="balanced",
        random_state=42,
        verbosity=-1
    )
    clf.fit(X_train, y_train)
    
    # Predictions and evaluation
    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    auc = float(roc_auc_score(y_test, y_pred_proba))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print("=" * 65)
    print(f"LIGHTGBM DISSATISFACTION RISK MODEL EVALUATION")
    print("=" * 65)
    print(f"ROC-AUC Score: {auc:.4f}")
    print(f"Precision:     {prec:.4f}")
    print(f"Recall:        {rec:.4f}")
    print(f"F1 Score:      {f1:.4f}")
    print("=" * 65)
    
    # Extract feature importance (gain and split)
    importance_gain = clf.booster_.feature_importance(importance_type="gain")
    total_gain = float(np.sum(importance_gain)) if np.sum(importance_gain) > 0 else 1.0
    
    importance_dict = {}
    for col, gain in zip(feature_cols, importance_gain):
        importance_dict[col] = round((float(gain) / total_gain) * 100.0, 2)
        
    sorted_importances = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
    print("\nTOP 8 GLOBAL FEATURE DRIVERS (% GAIN IMPORTANCE):")
    for feat, pct in sorted_importances[:8]:
        print(f"  * {feat:<25} {pct:>6.2f}%")
        
    # Save artifacts
    model_path = ARTIFACTS_DIR / "lgbm_risk_model.pkl"
    meta_path = ARTIFACTS_DIR / "model_metadata.json"
    
    joblib.dump(clf, model_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_type": "LightGBMClassifier",
            "features": feature_cols,
            "metrics": {
                "roc_auc": round(auc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4)
            },
            "global_importances": dict(sorted_importances)
        }, f, indent=2)
        
    logger.info(f"Model saved to {model_path}")
    return {
        "roc_auc": auc,
        "f1": f1,
        "model_path": str(model_path),
        "feature_importances": dict(sorted_importances)
    }

if __name__ == "__main__":
    analytical_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    train_dissatisfaction_risk_model(analytical_file)
