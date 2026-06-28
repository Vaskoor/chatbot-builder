# 🤖 Chatbot Builder

> **A dynamic, multi-tenant Retrieval-Augmented Generation (RAG) chatbot builder with hybrid search, GraphRAG, interactive maps, and persistent conversation memory.**  
> Build AI assistants powered by your own documents and knowledge base using **FastAPI**, **Next.js**, and modern LLM technologies.

<p align="center">
  <img src="https://via.placeholder.com/1200x600?text=Chatbot+Builder" alt="Chatbot Builder Banner">
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black?logo=next.js)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-38BDF8?logo=tailwindcss)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-orange)
![License](https://img.shields.io/badge/License-Private-red)

</p>

---

# 📖 Overview

**Chatbot Builder** is a production-ready platform for creating intelligent AI chatbots using your own data.

Instead of relying solely on an LLM's internal knowledge, the platform retrieves relevant information from uploaded documents before generating answers, ensuring responses are accurate, grounded, and context-aware.

The application supports:

- 📚 Knowledge base management
- 🧠 Hybrid Retrieval (Vector + BM25)
- 🔍 Cross-Encoder Re-ranking
- 🌐 GraphRAG for multi-hop reasoning
- 💬 Persistent conversation memory
- 🗺️ Interactive maps with route visualization
- 📂 Multiple document formats
- 👥 Multi-tenant architecture
- 🔐 Authentication & authorization

---

# ✨ Features

## 🤖 AI Chatbots

- Create unlimited AI chatbots
- Separate knowledge base for every chatbot
- Personalized system prompts
- Dynamic chatbot configuration

---

## 📚 Document Knowledge Base

Upload and manage documents including:

- PDF
- DOCX
- TXT
- Markdown
- CSV
- Excel
- Images (OCR)

Documents are automatically:

- Parsed
- Chunked
- Embedded
- Indexed

---

## 🔍 Hybrid Search

Instead of relying on only vector similarity, the retrieval engine combines:

- Semantic Vector Search
- BM25 Keyword Search

Benefits:

- Better recall
- Better precision
- Better factual grounding

---

## 🎯 Cross Encoder Re-ranking

Retrieved chunks are re-ranked using a Cross Encoder model.

Pipeline:

```
User Query
      │
      ▼
Vector Search
      │
      ▼
BM25 Search
      │
      ▼
Merge Results
      │
      ▼
Cross Encoder
      │
      ▼
Top Relevant Chunks
```

---

## 🧠 GraphRAG

The platform extracts:

- Entities
- Relationships
- Places
- Organizations
- Activities
- Permits

This enables multi-hop reasoning.

Example:

> What permits are required for Everest Base Camp and where can I obtain them?

The graph database links:

Everest Base Camp

↓

Permit

↓

Office

↓

Location

↓

Opening Hours

---

## 💬 Persistent Conversation Memory

Every conversation is stored.

Features:

- Chat history
- Rolling summaries
- Long-term memory
- Efficient context management

This allows conversations to remain coherent even after hundreds of messages.

---

## 🗺️ Interactive Maps

If an answer contains itinerary information, the frontend automatically renders:

- OpenStreetMap
- Leaflet
- OSRM road routing
- Markers
- Route lines
- Popups

Perfect for:

- Tourism
- Delivery
- Navigation
- Trip planning

---

## 📂 Smart File Management

Supports:

- Multiple uploads
- Re-uploading documents
- Version replacement
- History preservation

---

## 🔐 Authentication

- JWT Authentication
- Refresh Tokens
- Secure Password Hashing
- Protected APIs

---

## ⚡ Multi Tenant

Each user can create:

```
User A

├── Travel Bot
├── HR Bot
└── Company Assistant

User B

├── Medical Bot
├── Finance Bot
└── Legal Assistant
```

Each chatbot has:

- Separate documents
- Separate embeddings
- Separate conversations
- Separate GraphRAG
- Separate settings

---

# 🏗 Architecture

```
                    +-----------------------+
                    |      Next.js UI       |
                    +----------+------------+
                               |
                               |
                      REST API / JWT
                               |
                               ▼
                    +-----------------------+
                    |      FastAPI API      |
                    +----------+------------+
                               |
       -----------------------------------------------------
      |             |               |            |          |
      ▼             ▼               ▼            ▼          ▼
 Authentication  Document      Retrieval     GraphRAG   Chat Memory
                 Processing
      |             |               |
      |             ▼               |
      |        Chunking             |
      |             ▼               |
      |      Embedding Model        |
      |             ▼               |
      |         ChromaDB            |
      |                             |
      |                             ▼
      |                    Hybrid Search
      |               (Vector + BM25)
      |                             |
      |                             ▼
      |                 Cross Encoder
      |                     Re-ranking
      |                             |
      ------------------------------|
                                    ▼
                             LLM (Groq)
                                    |
                                    ▼
                            Final Response
```

---

# ⚙️ Technology Stack

| Layer | Technology |
|---------|------------|
| Frontend | Next.js |
| UI | React |
| Styling | Tailwind CSS |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Vector Database | ChromaDB |
| Authentication | JWT |
| LLM | Groq |
| Embeddings | Sentence Transformers |
| Re-ranking | Cross Encoder |
| Graph Storage | SQLite |
| Maps | Leaflet |
| Routing | OSRM |
| State Management | Zustand |
| API Cache | React Query |

---

# 🧠 AI Models

## Large Language Model

```
llama-3.3-70b-versatile
```

Fast Model

```
llama-3.1-8b-instant
```

Embedding Model

```
all-MiniLM-L6-v2
```

Cross Encoder

```
cross-encoder/ms-marco-MiniLM-L-6-v2
```

---

# 🚀 Retrieval Pipeline

```
                User Question
                      │
                      ▼
             Query Preprocessing
                      │
                      ▼
             Hybrid Retrieval
       ┌──────────────────────────┐
       │                          │
       ▼                          ▼
Vector Similarity            BM25 Search
       │                          │
       └────────────┬─────────────┘
                    ▼
             Merge Candidates
                    ▼
         Cross Encoder Re-ranking
                    ▼
            Top Relevant Chunks
                    ▼
              GraphRAG Search
                    ▼
            Context Construction
                    ▼
                Groq LLM
                    ▼
            Final AI Response
```

---

# 🗂 Project Structure

```
chatbot-builder
│
├── backend
│   ├── app
│   │   ├── core
│   │   ├── models
│   │   ├── routers
│   │   ├── schemas
│   │   ├── services
│   │   ├── utils
│   │   └── main.py
│   │
│   ├── storage
│   │   ├── uploads
│   │   ├── chroma_db
│   │   └── app.db
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend
│   ├── app
│   ├── components
│   ├── lib
│   ├── hooks
│   ├── types
│   ├── public
│   └── package.json
│
└── README.md
```

---

# 🚀 Quick Start

## Clone Repository

```bash
git clone https://github.com/your-username/chatbot-builder.git

cd chatbot-builder
```

---

# Backend Setup

```bash
cd backend

python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

Create `.env`

```bash
cp .env.example .env
```

Run server

```bash
uvicorn app.main:app --reload --port 8000
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Open

```
http://localhost:3000
```

---

# Environment Variables

```env
GROQ_API_KEY=

GROQ_MODEL=llama-3.3-70b-versatile

GROQ_FAST_MODEL=llama-3.1-8b-instant

JWT_SECRET_KEY=change-me

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=1440

REFRESH_TOKEN_EXPIRE_DAYS=30

DATABASE_URL=sqlite:///./storage/app.db

CHROMA_PERSIST_DIR=./storage/chroma_db

UPLOAD_DIR=./storage/uploads

EMBEDDING_MODEL=all-MiniLM-L6-v2

RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

ENABLE_RERANKING=True

CHUNK_SIZE=400

CHUNK_OVERLAP=60

VECTOR_TOP_K=10

BM25_TOP_K=10

FINAL_TOP_K=4

HYBRID_VECTOR_WEIGHT=0.6

HYBRID_BM25_WEIGHT=0.4

ENABLE_GRAPH_RAG=True

GRAPH_AUTO_ESCALATE=True

MAX_RECENT_TURNS=6

SUMMARIZE_AFTER_TURNS=20

CORS_ORIGINS=*
```

---

# 🌍 Deployment

## Frontend

- Vercel

## Backend

- Render

Recommended Environment Variables:

- GROQ_API_KEY
- NEXT_PUBLIC_API_URL
- JWT_SECRET_KEY
- DATABASE_URL

---

# 📌 Roadmap

- [x] Multi-tenant bots
- [x] Hybrid Retrieval
- [x] Cross Encoder Re-ranking
- [x] GraphRAG
- [x] Conversation Memory
- [x] JWT Authentication
- [x] Interactive Maps
- [x] File Uploads
- [ ] Streaming Responses
- [ ] Voice Chat
- [ ] Agent Workflows
- [ ] Tool Calling
- [ ] Slack Integration
- [ ] Discord Integration
- [ ] WhatsApp Integration
- [ ] Docker Deployment
- [ ] Kubernetes Support

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push your branch
5. Open a Pull Request

---

# 📄 License

This project is currently **Private** and intended for educational and demonstration purposes.

---

# 👨‍💻 Author

**Bhaskar Kaphle**

GitHub: https://github.com/Vaskoor

Email: vaskkaphle@gmail.com

---

<p align="center">

**⭐ If you found this project useful, consider giving it a star! ⭐**

</p>