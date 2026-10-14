import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from backend.app.core.config import settings
from backend.app.nlp.preprocessor import clean_review_tokens, get_lexicon_label

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def train_complaint_classifier(data_path: Path) -> Dict[str, Any]:
    """
    Trains a TF-IDF + Balanced Logistic Regression classifier on Portuguese
    review comments to classify operational complaint root causes.
    """
    logger.info(f"Loading analytical reviews from {data_path}...")
    df = pd.read_parquet(data_path)
    
    # Filter reviews with cleaned text comments
    reviews_df = df[df["has_comment"] == 1].copy()
    logger.info(f"Total reviews with text comments: {len(reviews_df):,d}")
    
    # Preprocess tokens
    reviews_df["clean_tokens"] = reviews_df["cleaned_comment"].apply(clean_review_tokens)
    
    # Extract anchor labels using domain rules
    logger.info("Generating weakly supervised training labels from domain lexicons...")
    reviews_df["pseudo_label"] = reviews_df["clean_tokens"].apply(get_lexicon_label)
    
    # Filter confidently labeled samples
    labeled_df = reviews_df[reviews_df["pseudo_label"].notnull()].copy()
    logger.info(f"Confidently anchored training samples: {len(labeled_df):,d}")
    print(f"\n[NLP] Anchor Class Distribution:\n{labeled_df['pseudo_label'].value_counts()}\n")
    
    X = labeled_df["clean_tokens"]
    y = labeled_df["pseudo_label"]
    
    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Vectorizer
    logger.info("Fitting TF-IDF Vectorizer (ngram_range=(1,2), max_features=5000)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Model
    logger.info("Training LogisticRegression(class_weight='balanced', max_iter=1000)...")
    clf = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        C=1.5,
        random_state=42
    )
    clf.fit(X_train_vec, y_train)
    
    # Evaluation
    y_pred = clf.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print("=" * 65)
    print(f"NLP CLASSIFIER EVALUATION REPORT (Test Set Accuracy: {acc*100:.2f}%)")
    print("=" * 65)
    for cls_name, metrics in report.items():
        if isinstance(metrics, dict):
            print(f"{cls_name:<25} Precision: {metrics['precision']:.3f} | Recall: {metrics['recall']:.3f} | F1: {metrics['f1-score']:.3f} (N={metrics['support']})")
    print("=" * 65)
    
    # Save artifacts
    model_path = ARTIFACTS_DIR / "topic_model.pkl"
    vec_path = ARTIFACTS_DIR / "tfidf_vectorizer.pkl"
    metrics_path = ARTIFACTS_DIR / "topic_metrics.json"
    
    joblib.dump(clf, model_path)
    joblib.dump(vectorizer, vec_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": round(acc, 4),
            "classes": clf.classes_.tolist(),
            "training_samples": len(labeled_df),
            "report": report
        }, f, indent=2)
        
    logger.info(f"Artifacts successfully saved to {ARTIFACTS_DIR}")
    return {
        "accuracy": acc,
        "classes": clf.classes_.tolist(),
        "model_path": str(model_path),
        "vectorizer_path": str(vec_path)
    }

if __name__ == "__main__":
    data_file = settings.PROCESSED_DATA_DIR / "orders_analytical.parquet"
    train_complaint_classifier(data_file)
