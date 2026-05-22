from functools import lru_cache
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()

class Settings:
    app_env: str = "DEVELOPMENT"
    app_version: str = "1.0.0"
    google_api: Optional[str] = os.getenv("GOOGLE_API_KEY")
    openrouter_api: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


    cors_origins: list[str] = ["*"]


@lru_cache()
def get_settings():
    return Settings()