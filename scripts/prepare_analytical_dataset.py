"""
TradeForensics — Dataset Processing Pipeline Execution Script
Team: RyzenShine | AMD Developer Hackathon ACT III
"""

import sys
import time
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings
from backend.app.data.loader import build_analytical_dataset
from scripts.verify_raw_data import verify_dataset

def main():
    print("=" * 75)
    print("TRADEFORENSICS — ANALYTICAL PIPELINE INGESTION")
    print(f"Project: {settings.PROJECT_NAME} | Team: {settings.TEAM_NAME}")
    print("=" * 75)

    # 1. Verify Raw Dataset
    print("\n[Step 1/2] Verifying raw dataset files...")
    if not verify_dataset():
        print("\n[ABORT] Raw dataset verification failed. Please supply files as described above.")
        sys.exit(1)

    # 2. Build Analytical Parquet
    print("\n[Step 2/2] Processing, cleaning & executing grain-safe joins...")
    start_time = time.time()
    try:
        df = build_analytical_dataset(
            raw_dir=settings.RAW_DATA_DIR, 
            output_dir=settings.PROCESSED_DATA_DIR
        )
        elapsed = time.time() - start_time
        print(f"\n[SUCCESS] Analytical dataset generated in {elapsed:.2f} seconds!")
        print("\n--- Analytical Summary ---")
        print(f"Total Unique Orders Processed: {len(df):,d}")
        delivered_count = df['is_delivered'].sum()
        late_count = df['is_late'].sum()
        print(f"Delivered Orders:             {delivered_count:,d} ({delivered_count/len(df)*100:.1f}%)")
        print(f"Late Delivered Orders:        {late_count:,d} ({late_count/delivered_count*100:.1f}% of delivered)")
        has_comment_count = int(df['has_comment'].fillna(0).sum())
        print(f"Reviews with Comments:        {has_comment_count:,d}")
        low_score_pct = float(df['is_low_score'].mean() * 100.0)
        print(f"Low-Score Share (<= 2 stars): {low_score_pct:.1f}%")
        print(f"Output File:                  {settings.PROCESSED_DATA_DIR / 'orders_analytical.parquet'}")
        print("---------------------------")
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
