# OmniRAG

<p align="center">
  <strong>Enterprise AI Knowledge Platform</strong><br>
  <sub>Document ingestion • Vector retrieval • RAG • Enterprise knowledge</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/pgvector-5E35B1?style=flat-square&logo=postgresql&logoColor=white" alt="pgvector">
  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
</p>

OmniRAG is a backend-first Retrieval-Augmented Generation platform for turning enterprise documents into searchable, retrieval-ready knowledge. It provides workspace isolation, document ingestion, content extraction, deterministic chunking, PostgreSQL persistence, and a pgvector-ready data layer for semantic retrieval.

> **Project status:** Active development. The ingestion foundation is implemented; embeddings, vector retrieval, RAG generation, authentication, observability, and production deployment are next.

---

## Architecture

```text
                    OmniRAG Knowledge Pipeline

  ┌──────────────┐
  │ PDF / CSV    │
  │ Documents    │
  └──────┬───────┘
         │
         ▼
  ┌──────────────────────┐
  │ Workspace Validation │
  │ File Validation      │
  │ SHA-256 Deduplication│
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Persistent Storage    │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Document Extraction  │
  │ PDF → Structured Text│
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Text Chunking        │
  │ Size + Overlap        │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ PostgreSQL           │
  │ document_chunks      │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ Embedding Generation │
  │       NEXT           │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ pgvector Retrieval   │
  │       NEXT           │
  └──────────┬───────────┘
             │
             ▼
  ┌──────────────────────┐
  │ LLM + RAG Response   │
  │       NEXT           │
  └──────────────────────┘
```

## What Is Implemented

- FastAPI REST API with OpenAPI / Swagger
- Workspace creation and retrieval
- Workspace-scoped document uploads
- PDF and CSV upload foundation
- SHA-256 duplicate detection
- Persistent local document storage
- PostgreSQL + SQLAlchemy persistence
- Document processing lifecycle states
- Page-level PDF text extraction
- Configurable text chunking with overlap
- Persistent `document_chunks` model
- `Vector(384)` embedding field prepared for pgvector
- Docker-based PostgreSQL development environment
- Health endpoint

## Technology Stack

| Layer | Technology | Role |
|---|---|---|
| API | **FastAPI** | REST API and OpenAPI documentation |
| Runtime | **Python 3.12+** | Application runtime |
| Server | **Uvicorn** | ASGI application server |
| Validation | **Pydantic** | Request/configuration validation |
| ORM | **SQLAlchemy** | Database models and persistence |
| Database | **PostgreSQL** | Metadata and document knowledge storage |
| Vector DB | **pgvector** | Vector embeddings and similarity search |
| PDF | **PyPDF** | PDF text extraction |
| Storage | **Local filesystem** | Original document persistence during development |
| Containers | **Docker Compose** | Local infrastructure |

<p align="center">
  <img src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/DB-PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Vector-pgvector-5E35B1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Infra-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

## API

Local development endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `GET` | `/workspaces` | List workspaces |
| `POST` | `/workspaces` | Create workspace |
| `GET` | `/workspaces/{workspace_id}` | Get workspace |
| `POST` | `/workspaces/{workspace_id}/documents` | Upload document |

Swagger UI:

`http://127.0.0.1:8200/docs`

OpenAPI:

`http://127.0.0.1:8200/openapi.json`

### Upload Example

```bash
curl -X POST \
  "http://127.0.0.1:8200/workspaces/<WORKSPACE_ID>/documents" \
  -H "accept: application/json" \
  -F "file=@attention-is-all-you-need.pdf;type=application/pdf"
```

## Project Structure

```text
OmniRAG/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── documents.py
│   │   │       └── workspaces.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── workspace.py
│   │   │   ├── document.py
│   │   │   └── chunk.py
│   │   ├── schemas/
│   │   └── services/
│   │       └── ingestion/
│   │           ├── chunker.py
│   │           ├── pipeline.py
│   │           └── extractors/
│   │               └── pdf.py
│   ├── data/
│   └── storage/
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Model

### Workspace

Tenant-like logical boundary for enterprise knowledge.

### Document

Stores document metadata:

- Workspace ID
- Filename
- Source type
- MIME type
- Storage path
- File size
- SHA-256 checksum
- Processing status
- Error information
- Timestamps

### DocumentChunk

Stores retrieval-ready text units:

- Document ID
- Chunk index
- Text
- Character count
- `Vector(384)` embedding column
- Creation timestamp

## Document Lifecycle

```text
uploaded
   ↓
processing
   ↓
processed
   ↓
indexed
```

Failures transition into:

```text
failed
```

## Local Development

### 1. Clone

```bash
git clone https://github.com/deekshitaa1/OmniRAG.git
cd OmniRAG
```

### 2. Create virtual environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r ..\requirements.txt
```

### 4. Configure environment

Create `backend/.env`:

```env
APP_NAME=OmniRAG
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://omnirag:omnirag@localhost:55433/omnirag
```

Keep `.env` out of Git.

### 5. Start PostgreSQL

From the repository root:

```powershell
docker compose up -d
```

Verify:

```powershell
docker ps
```

### 6. Start OmniRAG

From `backend/`:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8200
```

Then open:

```text
http://127.0.0.1:8200/docs
```

## Ingestion Test

The current pipeline can extract a PDF and split it into chunks:

```python
from app.services.ingestion.extractors.pdf import extract_pdf_text
from app.services.ingestion.chunker import chunk_text

result = extract_pdf_text("data/raw/attention-is-all-you-need.pdf")
text = "\n\n".join(page["text"] for page in result["pages"])
chunks = chunk_text(text)

print("Pages:", result["page_count"])
print("Characters:", result["total_characters"])
print("Chunks:", len(chunks))
```

## Roadmap

### Phase 1 — Ingestion Foundation

- [x] Workspace API
- [x] Document upload API
- [x] File validation
- [x] SHA-256 deduplication
- [x] Persistent document storage
- [x] PDF extraction
- [x] Text chunking
- [x] Chunk persistence model
- [x] pgvector-ready schema

### Phase 2 — Retrieval Engine

- [ ] Embedding generation service
- [ ] Batch embedding pipeline
- [ ] Vector persistence
- [ ] Cosine / similarity search
- [ ] Top-k retrieval
- [ ] Metadata filtering
- [ ] Hybrid keyword + vector retrieval

### Phase 3 — RAG Engine

- [ ] LLM provider abstraction
- [ ] Retrieval-augmented prompt construction
- [ ] Context-window management
- [ ] Source citations
- [ ] Streaming responses
- [ ] Conversation management

### Phase 4 — Enterprise Platform

- [ ] Authentication / authorization
- [ ] Multi-tenant isolation
- [ ] RBAC
- [ ] Background ingestion workers
- [ ] Redis task queue
- [ ] Structured logging
- [ ] Metrics and tracing
- [ ] Rate limiting
- [ ] API versioning
- [ ] Production deployment

## Engineering Principles

OmniRAG is being built around production-oriented backend principles:

- Modular service boundaries
- Workspace-level data isolation
- Deterministic document hashing
- Idempotent ingestion
- Explicit processing states
- Persistent source metadata
- Vector-search scalability
- Testability
- Separation of ingestion, retrieval, and generation
- API-first architecture

## Security

Never commit:

- `.env` files
- API keys
- Database passwords
- Private certificates
- `.venv/`
- Uploaded enterprise documents
- Local caches or generated artifacts

The repository `.gitignore` excludes development environments, secrets, caches, and local document storage.

## Status

**Current milestone: Backend ingestion foundation complete.**

The next major milestone is **embedding generation → pgvector similarity search → grounded RAG answers**.

## Author

**Deekshita Rajesh Naik**

GitHub: https://github.com/deekshitaa1

---

<p align="center"><sub>Built with Python • FastAPI • PostgreSQL • pgvector • Docker</sub></p>
