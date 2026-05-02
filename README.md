# E-Commerce Product Intelligence System

A production-ready End-to-End Multi-Modal Graph-Based RAG System for E-Commerce Product Intelligence.

## 🎯 Features

- **Multi-Modal Support**: Text search, image search, and hybrid search
- **RAG Pipeline**: Retrieval-Augmented Generation with context-aware responses
- **Knowledge Graph**: Product relationships using NetworkX
- **Vector Search**: FAISS for similarity matching
- **LLM Integration**: Google Gemini for response generation
- **REST API**: FastAPI backend with clean endpoints

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  • Search Bar  • Image Upload  • Chat Interface  • Results   │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   /ingest   │  │   /search   │  │      /query         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                                 │
│  RAG Pipeline:                                                 │
│  Query → Embedding → Vector Store → Graph → LLM → Response   │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FAISS     │     │  NetworkX   │     │   Gemini    │
│  (Vectors)  │     │   (Graph)   │     │    (LLM)    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- Gemini API Key

### Setup

1. **Clone and navigate to project:**
```bash
cd TSEC
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Build and run with Docker:**
```bash
docker-compose up --build
```

4. **Access the application:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your API key
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ingest` | Ingest products into the system |
| POST | `/api/v1/search` | Search products (text/image) |
| POST | `/api/v1/query` | Ask questions with RAG |
| POST | `/api/v1/recommend` | Get product recommendations |
| GET | `/health` | Health check |

### API Usage Examples

**Search:**
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "wireless headphones under 5000", "top_k": 10}'
```

**Query with RAG:**
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best budget headphones for running?"}'
```

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: FastAPI, Python 3.10
- **Embeddings**: sentence-transformers, CLIP
- **Vector Store**: FAISS
- **Graph**: NetworkX
- **LLM**: Google Gemini
- **Docker**: Multi-container setup

## 📁 Project Structure

```
TSEC/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/   # API routes
│   │   ├── core/            # Config
│   │   ├── models/          # Data models
│   │   └── services/        # Business logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API calls
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── data/
│   └── products.json        # Sample data (200 products)
├── docker-compose.yml
└── README.md
```

## 🎨 Sample Queries

- "Show me wireless headphones under 5000"
- "Best budget smartphones for gaming"
- "What are good running shoes for beginners?"
- "Is this product good for outdoor use?"

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GEMINI_API_KEY | Google Gemini API key | Required |
| EMBEDDING_MODEL | Text embedding model | all-MiniLM-L6-v2 |
| CLIP_MODEL | Image embedding model | openai/clip-vit-base-patch32 |
| TOP_K | Number of results | 10 |
| INDEX_PATH | FAISS index path | data/faiss_index |

## 🔧 Development

**Run tests:**
```bash
cd backend
pytest
```

**Lint code:**
```bash
# Backend
cd backend && flake8 app/

# Frontend
cd frontend && npm run lint
```

## 📄 License

MIT License

## 🙏 Acknowledgments

- sentence-transformers for text embeddings
- OpenAI CLIP for image embeddings
- Google Gemini for LLM