import pytest
from pathlib import Path
import tempfile
import shutil
import chromadb
from backend.app.rag.vector_store import get_chroma_client, get_reviews_collection, get_embedding_function
from backend.app.rag.retriever import ReviewRetriever

@pytest.fixture
def temp_chroma_dir():
    temp_dir = Path(tempfile.mkdtemp(prefix="test_chroma_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_embedding_function_initialization():
    fn = get_embedding_function()
    assert fn is not None
    vectors = fn(["muito bom", "produto com defeito"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 384  # all-MiniLM-L6-v2 dimension

def test_chroma_client_and_collection(temp_chroma_dir):
    client = chromadb.PersistentClient(path=str(temp_chroma_dir))
    coll = get_reviews_collection(client=client)
    assert coll.name == "olist_customer_reviews"
    assert coll.count() == 0

    # Test inserting sample reviews
    coll.add(
        ids=["ord_1", "ord_2"],
        documents=["Produto chegou quebrado e com defeito grave", "Entrega atrasou mais de duas semanas"],
        metadatas=[
            {"category": "furniture", "review_score": 1, "complaint_topic": "DAMAGED_DEFECTIVE", "delay_days": 0.0, "order_id": "ord_1", "original_text": "Produto quebrado"},
            {"category": "telephony", "review_score": 1, "complaint_topic": "DELIVERY_DELAY", "delay_days": 14.0, "order_id": "ord_2", "original_text": "Atrasou 14 dias"}
        ]
    )
    assert coll.count() == 2

    # Test retriever queries
    retriever = ReviewRetriever()
    retriever._collection = coll

    # 1. Query for damaged
    damaged_quotes = retriever.get_representative_complaints(category="furniture", top_k=2)
    assert len(damaged_quotes) == 1
    assert damaged_quotes[0]["category"] == "furniture"
    assert damaged_quotes[0]["complaint_topic"] == "DAMAGED_DEFECTIVE"

    # 2. Query for delay
    delay_quotes = retriever.get_representative_complaints(topic="DELIVERY_DELAY", top_k=2)
    assert len(delay_quotes) == 1
    assert delay_quotes[0]["complaint_topic"] == "DELIVERY_DELAY"
    assert delay_quotes[0]["delay_days"] == 14.0
