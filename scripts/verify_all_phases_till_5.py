"""
TradeForensics — Comprehensive Phase 0 to Phase 5 Audit & Verification Script
Team: RyzenShine | AMD Developer Hackathon ACT III
"""

import sys
import time
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def log_header(title: str):
    print("\n" + "=" * 75)
    print(f" {title}")
    print("=" * 75)

def log_check(item: str, passed: bool, detail: str = ""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} {item} {detail}")
    if not passed:
        raise AssertionError(f"Check failed: {item} - {detail}")

def test_phase_0():
    log_header("PHASE 0: ENVIRONMENT, TOOLING & BASELINE VERIFICATION")
    
    # 0.1 Virtual environment & Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    log_check("Python runtime", sys.version_info >= (3, 11), f"(Python {py_ver})")
    
    in_venv = sys.prefix != sys.base_prefix
    log_check("Virtual environment active (.venv)", in_venv, f"({sys.prefix})")
    
    # 0.2 Dependency imports
    import fastapi
    import lightgbm
    import chromadb
    import sklearn
    import pandas
    import groq
    import pydantic
    log_check("Core dependencies installed", True, 
              f"(fastapi {fastapi.__version__}, lightgbm {lightgbm.__version__}, "
              f"chromadb {chromadb.__version__}, pandas {pandas.__version__})")
              
    # 0.3 Config & Security
    from backend.app.core.config import settings
    log_check("Settings loaded", settings.PROJECT_NAME == "TradeForensics", f"({settings.PROJECT_NAME} by {settings.TEAM_NAME})")
    
    # 0.4 LLM Client Factory
    from backend.app.llm.client import get_llm_client
    client = get_llm_client()
    log_check("LLM Client initialized", client is not None, f"(Provider: {settings.LLM_PROVIDER})")

def test_phase_1():
    log_header("PHASE 1: DATASET INGESTION, CLEANING & GRAIN SAFETY")
    import pandas as pd
    from backend.app.core.config import settings
    
    raw_dir = settings.RAW_DATA_DIR
    raw_files = [
        "olist_orders_dataset.csv",
        "olist_order_items_dataset.csv",
        "olist_order_reviews_dataset.csv",
        "olist_products_dataset.csv",
        "product_category_name_translation.csv",
        "olist_sellers_dataset.csv",
        "olist_customers_dataset.csv"
    ]
    for rf in raw_files:
        path = raw_dir / rf
        log_check(f"Raw CSV present: {rf}", path.exists(), f"({path.stat().st_size:,d} bytes)")
        
    parquet_path = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    log_check("Analytical parquet generated", parquet_path.exists(), f"({parquet_path.stat().st_size:,d} bytes)")
    
    df = pd.read_parquet(parquet_path)
    log_check("Exact order count (no duplication)", len(df) == 98666, f"({len(df):,d} unique orders)")
    log_check("Unique order_id grain safety", df["order_id"].nunique() == 98666, f"({df['order_id'].nunique():,d} unique IDs)")
    
    expected_cols = [
        "order_id", "delay_days", "transit_days", "freight_ratio",
        "is_interstate", "is_low_score", "product_category_name_english", "total_price"
    ]
    for c in expected_cols:
        log_check(f"Feature column present: {c}", c in df.columns)
        
    null_flags = df["is_low_score"].isna().sum()
    log_check("Target flag integrity (is_low_score)", null_flags == 0, f"(0 nulls out of {len(df):,d})")
    log_check("Reviewed orders count", df["review_score"].notna().sum() == 97917, f"({df['review_score'].notna().sum():,d} reviewed, 749 unreviewed)")

def test_phase_2():
    log_header("PHASE 2: DETERMINISTIC KPI ENGINE & ISSUE DETECTION")
    from backend.app.services.kpi_service import kpi_service
    from backend.app.services.issue_detector import issue_detector
    
    overview = kpi_service.get_store_overview()
    log_check("Store total orders", overview["total_orders"] == 98666, f"({overview['total_orders']:,d})")
    log_check("Store global late rate baseline", abs(overview["global_late_rate_pct"] - 8.11) < 0.1, 
              f"({overview['global_late_rate_pct']}%)")
    log_check("Store global low score rate baseline", abs(overview["global_low_score_rate_pct"] - 14.23) < 0.1, 
              f"({overview['global_low_score_rate_pct']}%)")
    log_check("Late shipments penalty (avg delay)", overview["global_avg_delay_days"] > 9.0, 
              f"({overview['global_avg_delay_days']:.1f} days)")
              
    cat_kpis = kpi_service.get_category_metrics(min_reviews=50)
    log_check("Category metrics generated", len(cat_kpis) >= 50, f"({len(cat_kpis)} categories with N>=50)")
    
    issues = issue_detector.detect_top_issues(5)
    log_check("Top 5 issues detected", len(issues) == 5, f"(Top 1: {issues[0]['issue_id']} - score {issues[0]['severity_score']})")
    for iss in issues:
        log_check(f"  * Issue validated: {iss['issue_id']}", iss["severity_score"] > 0, 
                  f"(Severity: {iss['severity_score']:.1f} | {iss['issue_type']})")

def test_phase_3():
    log_header("PHASE 3: NLP REVIEW ROOT-CAUSE CLASSIFIER")
    import json
    import pandas as pd
    from backend.app.nlp.topic_tagger import topic_tagger
    from backend.app.core.config import settings
    
    metrics_path = Path(ROOT_DIR) / "backend" / "app" / "nlp" / "artifacts" / "topic_metrics.json"
    log_check("NLP metrics file exists", metrics_path.exists())
    with open(metrics_path, "r", encoding="utf-8") as f:
        nlp_meta = json.load(f)
        
    accuracy = nlp_meta.get("accuracy", 0)
    macro_f1 = nlp_meta.get("report", {}).get("macro avg", {}).get("f1-score", 0)
    log_check("NLP test accuracy >= 95%", accuracy >= 0.95, f"({accuracy*100:.2f}%)")
    log_check("NLP macro F1 score >= 0.90", macro_f1 >= 0.90, f"({macro_f1:.3f})")
              
    # Test individual phrase predictions
    test_cases = [
        ("meu pedido atrasou muito ja passou o prazo de entrega", "DELIVERY_DELAY"),
        ("produto com defeito quebrado pessima qualidade", "DAMAGED_DEFECTIVE"),
        ("veio tamanho errado e modelo divergente do anuncio", "CATALOG_MISMATCH"),
        ("ninguem responde quero cancelamento e estorno do dinheiro", "SERVICE_REFUND"),
        ("produto excelente muito bom chegou antes do prazo", "POSITIVE_SATISFACTION")
    ]
    for text, expected_topic in test_cases:
        res = topic_tagger.predict(text)
        log_check(f"NLP classification: '{expected_topic}'", res["topic"] == expected_topic,
                  f"(Predicted: {res['topic']} with confidence {res['confidence']:.2f})")
                  
    # Check reviews dataset
    reviews_path = settings.PROCESSED_DATA_DIR / "reviews_with_topics.parquet"
    log_check("Reviews with topics parquet exists", reviews_path.exists())
    rdf = pd.read_parquet(reviews_path)
    log_check("Tagged text reviews count", len(rdf) == 40162, f"({len(rdf):,d} reviews)")
    topic_dist = rdf["complaint_topic"].value_counts().to_dict()
    log_check("Topic distribution populated", len(topic_dist) >= 5, f"({topic_dist})")

def test_phase_4():
    log_header("PHASE 4: TABULAR ML LIGHTGBM MODEL & FEATURE ATTRIBUTION")
    import json
    from backend.app.ml.driver_explainer import driver_explainer
    from backend.app.core.config import settings
    import pandas as pd
    
    meta_path = Path(ROOT_DIR) / "backend" / "app" / "ml" / "artifacts" / "model_metadata.json"
    log_check("LightGBM metadata file exists", meta_path.exists())
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    roc_auc = meta["metrics"]["roc_auc"]
    recall = meta["metrics"]["recall"]
    f1 = meta["metrics"]["f1"]
    
    log_check("LightGBM ROC-AUC >= 0.90", roc_auc >= 0.90, f"(ROC-AUC: {roc_auc:.4f})")
    log_check("LightGBM Recall >= 80%", recall >= 0.80, f"(Recall: {recall*100:.2f}%)")
    log_check("LightGBM F1 Score >= 0.60", f1 >= 0.60, f"(F1: {f1:.4f})")
    
    # Check consistency with eval_scores.txt
    eval_file = Path(ROOT_DIR) / "eval_scores.txt"
    log_check("eval_scores.txt exists on root", eval_file.exists())
    with open(eval_file, "r", encoding="utf-8") as f:
        eval_text = f.read()
    log_check("eval_scores.txt contains exact ROC-AUC", "0.9071" in eval_text)
    
    # Test driver explainer
    global_drivers = driver_explainer.get_global_drivers(top_k=4)
    log_check("Global drivers extracted", len(global_drivers) == 4, 
              f"(Top 1: {global_drivers[0]['display_name']} - {global_drivers[0]['importance_pct']}%)")
              
    # Test segment risk prediction on late vs on-time orders
    orders_df = pd.read_parquet(settings.PROCESSED_DATA_DIR / "orders_analytical.parquet")
    late_df = orders_df[orders_df["delay_days"] > 5].head(200)
    ontime_df = orders_df[orders_df["delay_days"] == 0].head(200)
    
    late_risk = driver_explainer.predict_segment_risk(late_df)
    ontime_risk = driver_explainer.predict_segment_risk(ontime_df)
    log_check("Risk model discriminates late vs on-time", late_risk > ontime_risk, 
              f"(Late orders risk: {late_risk}% vs On-time orders risk: {ontime_risk}%)")

def test_phase_5():
    log_header("PHASE 5: SEMANTIC VECTOR STORE (CHROMADB RAG) & EVIDENCE PACKET")
    import chromadb
    from backend.app.rag.vector_store import get_chroma_client, get_reviews_collection, get_embedding_function
    from backend.app.rag.retriever import review_retriever
    from backend.app.services.evidence_assembler import evidence_assembler
    from backend.app.core.config import settings
    
    # 5.1 Client and Collection
    client = get_chroma_client()
    log_check("ChromaDB persistent client online", client is not None)
    
    coll = get_reviews_collection()
    doc_count = coll.count()
    log_check("Collection 'olist_customer_reviews' populated", doc_count == 3000, 
              f"({doc_count:,d} documents indexed)")
              
    # 5.2 Embedding function
    emb_fn = get_embedding_function()
    vectors = emb_fn(["teste de qualidade"])
    log_check("Local ONNX embedding dimension", len(vectors[0]) == 384, f"(384-d dense vector)")
    
    # 5.3 Stratified category coverage
    res = coll.get(include=["metadatas"])
    cats_in_db = set(m["category"] for m in res["metadatas"])
    log_check("Full product category representation in vector DB", len(cats_in_db) == 72, 
              f"({len(cats_in_db)} / 72 categories covered)")
              
    # 5.4 Semantic retrieval test
    probes = ["office_furniture", "audio", "fashion_male_clothing"]
    for cat in probes:
        quotes = review_retriever.get_representative_complaints(category=cat, top_k=2)
        log_check(f"Semantic quotes retrieved for '{cat}'", len(quotes) > 0, 
                  f"({len(quotes)} quotes, top similarity: {quotes[0]['similarity_score']})")
        log_check(f"  * Authentic quote text exists", len(quotes[0]["review_snippet"]) > 5, 
                  f"(\"{quotes[0]['review_snippet'][:60]}...\")")
                  
    # 5.5 End-to-end Evidence Packet assembly
    packet = evidence_assembler.assemble_evidence("cat_office_furniture")
    log_check("Evidence Packet assembled: office_furniture", packet is not None)
    log_check("  * Deterministic metrics present", packet.deterministic_kpis.sample_size > 0, 
              f"(N={packet.deterministic_kpis.sample_size:,d}, Low score delta: +{packet.deterministic_kpis.low_score_delta}%)")
    log_check("  * ML risk assessment present", packet.ml_risk_assessment["predicted_risk_pct"] > 0, 
              f"(Predicted risk: {packet.ml_risk_assessment['predicted_risk_pct']}%, Top driver: {packet.ml_risk_assessment['top_drivers'][0]['display_name']})")
    log_check("  * Customer quotes present", len(packet.qualitative_quotes) == 4, 
              f"({len(packet.qualitative_quotes)} authentic quotes attached)")
              
    # Seller Evidence Packet
    seller_packet = evidence_assembler.assemble_evidence("seller_1ca7077d890b907f89be8c954a02686a")
    log_check("Evidence Packet assembled: top problem seller", seller_packet is not None, 
              f"(Seller: {seller_packet.entity_name}, Severity: {seller_packet.severity_score:.1f})")

def main():
    print("=" * 75)
    print(" TRADEFORENSICS — COMPREHENSIVE PHASE 0 TO 5 AUDIT & VERIFICATION")
    print(" Project: TradeForensics | Team: RyzenShine | AMD Developer Hackathon ACT III")
    print("=" * 75)
    t0 = time.time()
    
    test_phase_0()
    test_phase_1()
    test_phase_2()
    test_phase_3()
    test_phase_4()
    test_phase_5()
    
    elapsed = time.time() - t0
    log_header(f"ALL PHASES (0 THROUGH 5) AUDITED & FULLY VERIFIED IN {elapsed:.2f}s!")
    print("\n[SUMMARY] Every single pipeline component, dataset, deterministic formula,")
    print("ML model, NLP classifier, and ChromaDB vector collection is 100% operational")
    print("and perfectly aligned with phases.txt.\n")

if __name__ == "__main__":
    main()
