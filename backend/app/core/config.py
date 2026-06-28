"""
Central configuration for the Chatbot Builder backend.
Loads everything from environment variables (.env) with sane defaults.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    # --- LLM ---
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    groq_fast_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_FAST_MODEL")
    # --- Auth ---
    jwt_secret_key: str = Field(default="dev-secret-change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    # --- Storage ---
    database_url: str = Field(default="sqlite:///./storage/app.db", alias="DATABASE_URL")
    chroma_persist_dir: str = Field(default="./storage/chroma_db", alias="CHROMA_PERSIST_DIR")
    upload_dir: str = Field(default="./storage/uploads", alias="UPLOAD_DIR")
    # --- Embeddings ---
    embedding_model: str = Field(default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    # --- Reranking ---
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="RERANKER_MODEL")
    enable_reranking: bool = Field(default=True, alias="ENABLE_RERANKING")

    # --- Chunking ---
    chunk_size: int = Field(default=800, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, alias="CHUNK_OVERLAP")
    # --- Retrieval ---
    vector_top_k: int = Field(default=20, alias="VECTOR_TOP_K")
    bm25_top_k: int = Field(default=20, alias="BM25_TOP_K")
    final_top_k: int = Field(default=6, alias="FINAL_TOP_K")
    hybrid_vector_weight: float = Field(default=0.6, alias="HYBRID_VECTOR_WEIGHT")
    hybrid_bm25_weight: float = Field(default=0.4, alias="HYBRID_BM25_WEIGHT")
    # --- GraphRAG ---
    enable_graph_rag: bool = Field(default=True, alias="ENABLE_GRAPH_RAG")
    graph_auto_escalate: bool = Field(default=True, alias="GRAPH_AUTO_ESCALATE")
    # --- Conversation Memory ---
    max_recent_turns: int = Field(default=12, alias="MAX_RECENT_TURNS")
    summarize_after_turns: int = Field(default=20, alias="SUMMARIZE_AFTER_TURNS")
    # --- CORS ---
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")
    class Config:
        env_file = ".env"
        populate_by_name = True
        extra = "ignore"
settings = Settings()
# Ensure storage directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_persist_dir, exist_ok=True)
os.makedirs("./storage/exports", exist_ok=True)
