"""
TradeForensics — ChromaDB Review Ingestion & Indexing Script
Team: RyzenShine | AMD Developer Hackathon ACT III
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import settings
from backend.app.rag.indexer import index_reviews
from backend.app.rag.retriever import review_retriever

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    print("=" * 70)
    print("TRADEFORENSICS — CHROMADB VECTOR STORE INDEXER")
    print(f"Project: {settings.PROJECT_NAME} | Team: {settings.TEAM_NAME}")
    print("=" * 70)

    # 1. Ingest & Index
    print("\n[Step 1/2] Indexing customer complaints into ChromaDB...")
    t0 = time.time()
    result = index_reviews(max_records=3000, batch_size=128, force_reindex=True)
    print(f"[STATUS] {result['status'].upper()} — Total Documents in DB: {result.get('total_in_db', result.get('document_count', 0)):,d}")

    # 2. Test Retrieval
    print("\n[Step 2/2] Testing Semantic Complaint Retrieval on Detected Friction Categories...")
    test_categories = ["office_furniture", "audio", "fashion_male_clothing"]
    
    for cat in test_categories:
        print("\n" + "-" * 70)
        print(f"CATEGORY PROBE: '{cat}'")
        quotes = review_retriever.get_representative_complaints(category=cat, top_k=2)
        if not quotes:
            print("  (No direct quotes found)")
            continue
        for q in quotes:
            print(f"  * [Score {q['review_score']}* | Delay: {q['delay_days']}d | {q['complaint_topic']} | Sim: {q['similarity_score']}]")
            print(f"    \"{q['review_snippet']}\"")
            
    print("-" * 70)
    print("[SUCCESS] ChromaDB Semantic Retrieval Pipeline is fully operational!")

if __name__ == "__main__":
    main()
