from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from config import get_settings

settings = get_settings()

llm_gemini = ChatGoogleGenerativeAI(
    model = settings.gemini_model,
    api_key = settings.google_api
)

llm_ollama = ChatOllama(
    model = settings.ollama_model,
    verbose = True
)