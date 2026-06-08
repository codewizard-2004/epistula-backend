from utils.auth import verify_jwt
from fastapi import Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import get_settings

from routers.extract import router as extract_router
from routers.analyze import router as analyze_router
from routers.generate import router as generate_router
from routers.jobs import router as jobs_router

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter

from services.llm import llm_gemini

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from utils.limiter import limiter
from fastapi import Request

settings = get_settings()

"""
Asynccontextmanager is a decorator that allows us to define a function that can be used as an asynchronous context manager.
In this case, we are using it to define a lifespan function that will be called when the server starts and when it shuts down.
We can use this function to perform any setup or teardown tasks like connecting to the database or disconnecting from the database.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SERVER: Connecting to the database...")
    app.state.google_llm = llm_gemini
    print("SERVER: Initialized LLM instance...")
    print("SERVER: Epistula server starting...\n")
    yield
    print("SERVER: Disconnecting from the database...")
    print("SERVER: Epistula server shutting down...\n")


app = FastAPI(
    title = "Epistula AI backend",
    description = "Backend service for epistula AI\n.Resume Analysis, ATS scoring, cover letter generation, job dearch",
    version = settings.app_version,
    lifespan = lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

"""
Cross Origin Resource Sharing is a browser security mechanism that blocks web pages from making resquests to a different domain than the one that served the page.
We need to add the domain of vercel after hosting the frontend
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
Tags are used to group endpoints in the documentation.
We can use them to group endpoints by functionality or by resource.
"""
@app.get("/", tags = ["Health"], dependencies=[Depends(verify_jwt)])
@limiter.limit("1/second")
async def root(request: Request):
    return {
        "status": "ok",
        "app": "Epistula AI",
        "version": settings.app_version
    }

# add routers
app.include_router(extract_router)
app.include_router(analyze_router)
app.include_router(generate_router)
app.include_router(jobs_router)

