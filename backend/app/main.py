import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.api.overview import router as overview_router
from backend.app.api.issues import router as issues_router
from backend.app.api.copilot import router as copilot_router

logger = logging.getLogger(__name__)

# State cache for preloaded dataset and services
app_state = {
    "dataset_rows": 0,
    "vector_store_documents": 0,
    "ml_model_status": "initializing",
    "nlp_classifier_status": "initializing"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler to pre-warm models and load analytical parquet on startup,
    ensuring sub-50ms API response latency.
    """
    logger.info("Starting up TradeForensics API server...")
    
    # 1. Check & pre-warm analytical parquet dataset
    try:
        from backend.app.services.kpi_service import kpi_service
        overview = kpi_service.get_store_overview()
        app_state["dataset_rows"] = overview["total_orders"]
        logger.info(f"Analytical orders dataset pre-warmed: {overview['total_orders']:,d} orders.")
    except Exception as e:
        logger.warning(f"Could not pre-warm analytical dataset: {e}")

    # 2. Check LightGBM Tabular ML Model
    try:
        from backend.app.ml.driver_explainer import driver_explainer
        driver_explainer.get_global_drivers(top_k=1)
        app_state["ml_model_status"] = "ready"
        logger.info("LightGBM risk model pre-warmed and verified.")
    except Exception as e:
        app_state["ml_model_status"] = f"error: {e}"
        logger.warning(f"ML model failed to pre-warm: {e}")

    # 3. Check NLP Topic Classifier
    try:
        from backend.app.nlp.topic_tagger import topic_tagger
        topic_tagger.predict("test")
        app_state["nlp_classifier_status"] = "ready"
        logger.info("NLP topic classifier pre-warmed.")
    except Exception as e:
        app_state["nlp_classifier_status"] = f"error: {e}"
        logger.warning(f"NLP classifier failed to pre-warm: {e}")

    # 4. Check ChromaDB collection
    try:
        from backend.app.rag.vector_store import get_reviews_collection
        coll = get_reviews_collection()
        app_state["vector_store_documents"] = coll.count()
        logger.info(f"ChromaDB collection online with {app_state['vector_store_documents']:,d} customer reviews.")
    except Exception as e:
        logger.warning(f"ChromaDB pre-warm check failed: {e}")

    yield
    logger.info("Shutting down TradeForensics API server...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Evidence-Grounded Statistical Root-Cause Forensics & Action Copilot for E-Commerce",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Enable CORS for local React / Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(overview_router)
app.include_router(issues_router)
app.include_router(copilot_router)

@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint exposing system readiness without leaking secrets."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "team": settings.TEAM_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "dataset_rows": app_state["dataset_rows"],
        "vector_store_documents": app_state["vector_store_documents"],
        "ml_model_status": app_state["ml_model_status"],
        "nlp_classifier_status": app_state["nlp_classifier_status"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
