import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from backend.app.core.config import settings
from backend.app.rag.vector_store import get_reviews_collection, get_chroma_client

logger = logging.getLogger(__name__)

def index_reviews(
    data_path: Optional[Path] = None,
    max_records: int = 10000,
    batch_size: int = 256,
    force_reindex: bool = False
) -> Dict[str, Any]:
    """
    Indexes authentic customer reviews with comments into ChromaDB.
    Prioritizes dissatisfied/complaint reviews (score <= 2 and topic != 'POSITIVE_SATISFACTION').
    """
    parquet_path = data_path or (settings.PROCESSED_DATA_DIR / "reviews_with_topics.parquet")
    if not parquet_path.exists():
        raise FileNotFoundError(f"Reviews dataset not found at {parquet_path}. Run NLP tagging first.")
        
    if force_reindex:
        client = get_chroma_client()
        try:
            client.delete_collection(name="olist_customer_reviews")
            logger.info("Deleted existing collection for clean re-indexing.")
        except Exception:
            pass

    collection = get_reviews_collection()
    current_count = collection.count()
    
    if current_count > 0 and not force_reindex:
        logger.info(f"ChromaDB collection already contains {current_count:,d} documents. Skipping re-indexing.")
        return {
            "status": "already_indexed",
            "document_count": current_count
        }

    logger.info(f"Loading reviews from {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    
    # Filter non-empty clean comments
    valid_df = df[df["cleaned_comment"].str.len() > 5].copy()
    
    # Stratified prioritization: Ensure every category and problem seller has authentic complaints
    low_score_df = valid_df[valid_df["is_low_score"] == 1]
    
    # Ensure all 72 product categories have authentic complaint representation
    cat_sample = low_score_df.groupby("product_category_name_english").head(35)
    
    # Ensure top friction sellers have representation
    try:
        from backend.app.services.issue_detector import issue_detector
        top_issues = issue_detector.detect_top_issues(50)
        top_sellers = [i["issue_id"].replace("seller_", "") for i in top_issues if i["entity_type"] == "seller"]
        seller_sample = low_score_df[low_score_df["seller_id"].isin(top_sellers)]
    except Exception as e:
        logger.warning(f"Could not load seller sample: {e}")
        seller_sample = pd.DataFrame()
        
    combined = pd.concat([cat_sample, seller_sample]).drop_duplicates(subset=["order_id"])
    
    # If more records requested, append remaining complaints
    if len(combined) < max_records:
        remaining_low = low_score_df[~low_score_df["order_id"].isin(combined["order_id"])]
        needed = max_records - len(combined)
        combined = pd.concat([combined, remaining_low.head(needed)], ignore_index=True)
        
    index_df = combined.head(max_records)
        
    total_docs = len(index_df)
    logger.info(f"Preparing to index {total_docs:,d} customer review documents in batches of {batch_size}...")
    print(f"\n[RAG Indexer] Indexing {total_docs:,d} reviews into ChromaDB...")
    
    start_time = time.time()
    for i in range(0, total_docs, batch_size):
        batch = index_df.iloc[i : i + batch_size]
        
        ids = [str(oid) for oid in batch["order_id"]]
        documents = batch["cleaned_comment"].tolist()
        
        metadatas = []
        for _, row in batch.iterrows():
            metadatas.append({
                "order_id": str(row["order_id"]),
                "category": str(row["product_category_name_english"]),
                "seller_id": str(row["seller_id"]),
                "review_score": int(row["review_score"]),
                "delay_days": round(float(row["delay_days"]), 1),
                "complaint_topic": str(row["complaint_topic"]),
                "original_text": str(row["review_comment"])[:300]
            })
            
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        indexed_so_far = min(i + batch_size, total_docs)
        if indexed_so_far % 1000 == 0 or indexed_so_far == total_docs:
            print(f"  * Progress: {indexed_so_far:,d} / {total_docs:,d} documents indexed...")
            
    elapsed = time.time() - start_time
    total_in_db = collection.count()
    print(f"[RAG Indexer] Finished in {elapsed:.2f}s! Total documents in vector store: {total_in_db:,d}")
    
    return {
        "status": "success",
        "indexed_count": total_docs,
        "total_in_db": total_in_db,
        "elapsed_seconds": round(elapsed, 2)
    }

if __name__ == "__main__":
    index_reviews(force_reindex=False)
