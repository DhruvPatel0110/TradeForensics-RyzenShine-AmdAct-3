from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Statistical Root-Cause Forensics & Action Copilot for E-Commerce",
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Enable CORS for local React / Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint exposing system readiness without leaking secrets."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "team": settings.TEAM_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "groq_model": settings.GROQ_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
