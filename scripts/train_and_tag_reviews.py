"""
TradeForensics — Train NLP Model & Tag Review Corpus
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
from backend.app.nlp.train_topic_model import train_complaint_classifier
from backend.app.nlp.topic_tagger import topic_tagger

def main():
    print("=" * 70)
    print("TRADEFORENSICS — NLP COMPLAINT CLASSIFIER PIPELINE")
    print(f"Project: {settings.PROJECT_NAME} | Team: {settings.TEAM_NAME}")
    print("=" * 70)

    analytical_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    if not analytical_file.exists():
        print(f"[ERROR] Analytical dataset not found at {analytical_file}.")
        print("Please run scripts/prepare_analytical_dataset.py first.")
        sys.exit(1)

    # 1. Train Classifier
    print("\n[Step 1/2] Training TF-IDF + Logistic Regression Complaint Classifier...")
    t0 = time.time()
    train_results = train_complaint_classifier(analytical_file)
    print(f"[SUCCESS] Model trained in {time.time() - t0:.2f} seconds!")
    print(f"Test Accuracy: {train_results['accuracy']*100:.2f}% across {len(train_results['classes'])} classes.")

    # 2. Tag Entire Review Corpus
    print("\n[Step 2/2] Running high-throughput batch inference over all customer reviews...")
    t1 = time.time()
    df = pd.read_parquet(analytical_file)
    total_records = len(df)
    
    texts = df["cleaned_comment"].fillna("").tolist()
    batch_preds = topic_tagger.predict_batch(texts)
    
    df["complaint_topic"] = [p["topic"] for p in batch_preds]
    df["topic_confidence"] = [p["confidence"] for p in batch_preds]
    
    # Save updated analytical dataset
    df.to_parquet(analytical_file, index=False)
    
    # Save standalone reviews dataset
    reviews_only = df[df["has_comment"] == 1][[
        "order_id", "review_score", "is_low_score", 
        "review_comment", "cleaned_comment", 
        "product_category_name_english", "seller_id",
        "delay_days", "complaint_topic", "topic_confidence"
    ]].copy()
    
    reviews_out = settings.PROCESSED_DATA_DIR / "reviews_with_topics.parquet"
    reviews_only.to_parquet(reviews_out, index=False)
    
    elapsed = time.time() - t1
    print(f"[SUCCESS] Tagged {total_records:,d} orders in {elapsed:.2f} seconds ({total_records/elapsed:,.0f} records/sec)!")
    
    print("\n" + "=" * 70)
    print("REAL-WORLD COMPLAINT TOPIC DISTRIBUTION (Reviews with Comments):")
    print("=" * 70)
    topic_counts = reviews_only["complaint_topic"].value_counts()
    for topic, count in topic_counts.items():
        pct = (count / len(reviews_only)) * 100
        print(f"{topic:<25} {count:<10,d} ({pct:.1f}%)")
    print("-" * 70)
    print(f"Total Text Reviews Tagged: {len(reviews_only):,d}")
    print(f"Saved: {analytical_file}")
    print(f"Saved: {reviews_out}")
    print("=" * 70)

if __name__ == "__main__":
    main()
