from functools import lru_cache
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Settings:
    app_env: str = "DEVELOPMENT"
    app_version: str = "3.0.0"
    google_api: Optional[str] = os.getenv("GOOGLE_API_KEY")
    openrouter_api: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
    supabase_jwt_secret: Optional[str] = os.getenv("SUPABASE_JWT_SECRET")


    cors_origins: list[str] = ["*"]


@lru_cache()
def get_settings():
    return Settings()