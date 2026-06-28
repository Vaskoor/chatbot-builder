"""
Chatbot Builder — main application entry point.
 
Run with: uvicorn app.main:app --reload --port 8000
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.models import user, bot, document, graph, conversation  # noqa: F401 (ensures models register)
from app.routers import auth, bots, documents, chat, graph as graph_router
logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="Chatbot Builder API",
    description=(
        "A dynamic, multi-tenant RAG chatbot builder: upload files/folders to build "

        "a per-user chatbot with hybrid search, cross-encoder reranking, GraphRAG "
        "multi-hop reasoning, and persistent per-user conversation memory."
    ),
    version="1.0.0",
)
origins = ["*"] if settings.cors_origins == "*" else [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(bots.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(graph_router.router)
@app.get("/api/health")
def health():
    return {"status": "ok"}
@app.get("/")
def root():
    return {
        "service": "Chatbot Builder API",
        "docs": "/docs",
        "health": "/api/health",
    }
