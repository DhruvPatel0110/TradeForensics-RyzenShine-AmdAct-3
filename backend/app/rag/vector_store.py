import logging
from pathlib import Path
from typing import Optional
import chromadb
from chromadb.utils import embedding_functions
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "olist_customer_reviews"
DEFAULT_EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

_client: Optional[chromadb.PersistentClient] = None
_embedding_fn = None

def get_embedding_function():
    """Initializes and caches the local ONNX embedding function (all-MiniLM-L6-v2)."""
    global _embedding_fn
    if _embedding_fn is None:
        logger.info("Loading ChromaDB default ONNX embedding function...")
        _embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    return _embedding_fn

def get_chroma_client(persist_dir: Optional[Path] = None) -> chromadb.PersistentClient:
    """Returns a singleton ChromaDB PersistentClient."""
    global _client
    if _client is None:
        db_path = persist_dir or settings.CHROMA_PERSIST_DIR
        db_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Connecting to persistent ChromaDB at {db_path}...")
        _client = chromadb.PersistentClient(path=str(db_path))
    return _client

def get_reviews_collection(client: Optional[chromadb.PersistentClient] = None) -> chromadb.Collection:
    """Returns the customer reviews collection configured with cosine similarity."""
    chroma_client = client or get_chroma_client()
    embedding_fn = get_embedding_function()
    
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    return collection
