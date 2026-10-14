from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "TradeForensics"
    TEAM_NAME: str = "RyzenShine"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # LLM Settings
    LLM_PROVIDER: str = Field(default="groq", description="groq, fireworks, or mock")
    GROQ_API_KEY: str = Field(default="", description="Groq API key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Default Groq model")
    
    FIREWORKS_API_KEY: str = Field(default="", description="Fireworks AMD GPU API key")
    FIREWORKS_BASE_URL: str = Field(default="https://api.fireworks.ai/inference/v1")
    FIREWORKS_MODEL: str = Field(default="accounts/fireworks/models/llama-v3p3-70b-instruct")
    
    # Storage Paths
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma_db"
    
    # Server Ports
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
