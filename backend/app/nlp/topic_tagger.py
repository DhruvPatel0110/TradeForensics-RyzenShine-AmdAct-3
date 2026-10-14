import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import numpy as np

from backend.app.nlp.preprocessor import clean_review_tokens

logger = logging.getLogger(__name__)
ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

class TopicTagger:
    """
    Production inference engine for tagging Portuguese review comments
    with root-cause operational complaint categories.
    """
    
    def __init__(self, artifacts_dir: Optional[Path] = None):
        self.artifacts_dir = artifacts_dir or ARTIFACTS_DIR
        self._model = None
        self._vectorizer = None
        self._classes = None

    def _load(self):
        if self._model is None:
            model_path = self.artifacts_dir / "topic_model.pkl"
            vec_path = self.artifacts_dir / "tfidf_vectorizer.pkl"
            if not model_path.exists() or not vec_path.exists():
                raise FileNotFoundError(
                    f"NLP artifacts not found in {self.artifacts_dir}. Train model first."
                )
            self._model = joblib.load(model_path)
            self._vectorizer = joblib.load(vec_path)
            self._classes = self._model.classes_.tolist()

    def predict(self, text: Optional[str]) -> Dict[str, Any]:
        """Classifies a single review comment string."""
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "topic": "NO_COMMENT",
                "confidence": 1.0,
                "probabilities": {}
            }
        
        self._load()
        clean = clean_review_tokens(text)
        if not clean:
            return {
                "topic": "OTHER_GENERAL",
                "confidence": 0.5,
                "probabilities": {}
            }
            
        vec = self._vectorizer.transform([clean])
        probs = self._model.predict_proba(vec)[0]
        best_idx = int(np.argmax(probs))
        best_topic = self._classes[best_idx]
        best_conf = float(probs[best_idx])
        
        # If model is uncertain (confidence < 0.35 across 5 classes), label as OTHER_GENERAL
        if best_conf < 0.35:
            best_topic = "OTHER_GENERAL"

        prob_dict = {cls: round(float(p), 4) for cls, p in zip(self._classes, probs)}
        return {
            "topic": best_topic,
            "confidence": round(best_conf, 4),
            "probabilities": prob_dict
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Vectorized high-throughput batch classification."""
        self._load()
        results = []
        clean_texts = []
        valid_indices = []

        for i, t in enumerate(texts):
            if not t or not isinstance(t, str) or not t.strip():
                continue
            clean = clean_review_tokens(t)
            if clean:
                clean_texts.append(clean)
                valid_indices.append(i)

        # Default placeholder for all items
        batch_out = [{"topic": "NO_COMMENT", "confidence": 1.0} for _ in range(len(texts))]

        if clean_texts:
            X_vec = self._vectorizer.transform(clean_texts)
            probs = self._model.predict_proba(X_vec)
            best_indices = np.argmax(probs, axis=1)
            
            for orig_idx, pred_idx, prob_row in zip(valid_indices, best_indices, probs):
                topic = self._classes[pred_idx]
                conf = float(prob_row[pred_idx])
                if conf < 0.35:
                    topic = "OTHER_GENERAL"
                batch_out[orig_idx] = {
                    "topic": topic,
                    "confidence": round(conf, 4)
                }

        return batch_out

topic_tagger = TopicTagger()
