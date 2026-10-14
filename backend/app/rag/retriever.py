import logging
from typing import Dict, Any, List, Optional
from backend.app.rag.vector_store import get_reviews_collection

logger = logging.getLogger(__name__)

DEFAULT_COMPLAINT_PROBE = "atraso na entrega produto com defeito quebrado tamanho errado nao recebi estorno"

class ReviewRetriever:
    """
    Semantic Retrieval Engine for TradeForensics.
    Queries ChromaDB for the most representative, authentic customer complaints.
    """
    
    def __init__(self):
        self._collection = None

    def _get_coll(self):
        if self._collection is None:
            self._collection = get_reviews_collection()
        return self._collection

    def get_representative_complaints(
        self,
        category: Optional[str] = None,
        seller_id: Optional[str] = None,
        topic: Optional[str] = None,
        query: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k semantically relevant customer review quotes filtered
        by category, seller, or complaint topic.
        """
        coll = self._get_coll()
        total_docs = coll.count()
        if total_docs == 0:
            logger.warning("ChromaDB collection is empty. Returning empty quotes.")
            return []

        search_query = query or DEFAULT_COMPLAINT_PROBE
        
        # Build ChromaDB metadata filter
        filter_conditions = []
        if category:
            filter_conditions.append({"category": category})
        if seller_id:
            filter_conditions.append({"seller_id": seller_id})
        if topic:
            filter_conditions.append({"complaint_topic": topic})

        # Combine conditions
        where_filter = None
        if len(filter_conditions) == 1:
            where_filter = filter_conditions[0]
        elif len(filter_conditions) > 1:
            where_filter = {"$and": filter_conditions}

        # Query ChromaDB
        try:
            results = coll.query(
                query_texts=[search_query],
                n_results=top_k,
                where=where_filter
            )
        except Exception as e:
            logger.warning(f"ChromaDB query with filter failed ({e}), falling back to unfiltered search.")
            results = coll.query(
                query_texts=[search_query],
                n_results=top_k
            )

        # Parse and format quotes
        quotes = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine similarity = 1 - distance
                sim = round(max(0.0, 1.0 - float(dist)), 3)
                original_text = meta.get("original_text", doc)
                quotes.append({
                    "order_id": meta.get("order_id", ""),
                    "review_snippet": original_text,
                    "review_score": meta.get("review_score", 1),
                    "category": meta.get("category", ""),
                    "delay_days": meta.get("delay_days", 0.0),
                    "complaint_topic": meta.get("complaint_topic", "OTHER_GENERAL"),
                    "similarity_score": sim
                })

        return quotes

review_retriever = ReviewRetriever()
