"""
TradeForensics — Train LightGBM Dissatisfaction Risk Model
Team: RyzenShine | AMD Developer Hackathon ACT III
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings
from backend.app.ml.train_risk_model import train_dissatisfaction_risk_model
from backend.app.ml.driver_explainer import driver_explainer

def main():
    print("=" * 70)
    print("TRADEFORENSICS — LIGHTGBM RISK & ATTRIBUTION ENGINE")
    print(f"Project: {settings.PROJECT_NAME} | Team: {settings.TEAM_NAME}")
    print("=" * 70)

    analytical_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    if not analytical_file.exists():
        print(f"[ERROR] Analytical dataset not found at {analytical_file}.")
        sys.exit(1)

    print("\n[Step 1/2] Training LightGBM Dissatisfaction Risk Classifier...")
    t0 = time.time()
    results = train_dissatisfaction_risk_model(analytical_file)
    elapsed = time.time() - t0
    print(f"\n[SUCCESS] LightGBM model trained in {elapsed:.2f} seconds!")
    print(f"Test Set ROC-AUC: {results['roc_auc']:.4f}")
    print(f"Test Set F1:      {results['f1']:.4f}")

    print("\n[Step 2/2] Testing Segment Driver Attribution on Detected Issues...")
    df = pd.read_parquet(analytical_file)
    
    test_categories = ["office_furniture", "audio", "fashion_male_clothing"]
    for cat in test_categories:
        cat_df = df[df["product_category_name_english"] == cat]
        if cat_df.empty:
            continue
        risk_score = driver_explainer.predict_segment_risk(cat_df)
        drivers = driver_explainer.get_segment_drivers(cat_df, top_k=3)
        
        print("\n" + "-" * 70)
        print(f"CATEGORY: '{cat}' (N={len(cat_df):,d} orders)")
        print(f"  * Predicted Dissatisfaction Risk: {risk_score:.1f}%")
        print("  * Top Operational Drivers:")
        for d in drivers:
            print(f"    - {d['display_name']:<40} ({d['importance_pct']:.1f}% attribution)")
    print("-" * 70)

if __name__ == "__main__":
    main()
