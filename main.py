from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import get_settings

settings = get_settings()

"""
Asynccontextmanager is a decorator that allows us to define a function that can be used as an asynchronous context manager.
In this case, we are using it to define a lifespan function that will be called when the server starts and when it shuts down.
We can use this function to perform any setup or teardown tasks like connecting to the database or disconnecting from the database.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SERVER: Connecting to the database...")
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
@app.get("/", tags = ["Health"])
async def root():
    return {
        "status": "ok",
        "app": "Epistula AI",
        "version": settings.app_version
    }