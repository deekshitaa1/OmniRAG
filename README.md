# OmniRAG

**Enterprise AI Knowledge Platform**

OmniRAG is a backend-first Retrieval-Augmented Generation (RAG) platform for ingesting enterprise knowledge, extracting document content, chunking it into retrieval-ready units, and preparing the knowledge layer for semantic search and AI-powered question answering.

> **Status:** Active development — core workspace, document upload, PDF extraction, chunking, PostgreSQL persistence, and pgvector-ready data modeling are implemented. Retrieval, embeddings, generation, authentication, and production deployment are being built next.

## What OmniRAG Does

OmniRAG is designed around a production-style ingestion pipeline:

```text
Document Upload
      ↓
Workspace Validation
      ↓
File Validation + SHA-256 Deduplication
      ↓
Persistent File Storage
      ↓
PDF Text Extraction
      ↓
Text Chunking
      ↓
PostgreSQL Chunk Persistence
      ↓
Vector Embeddings
      ↓
Semantic Retrieval
      ↓
RAG Answer Generation
```

## Current Features

- FastAPI REST API with OpenAPI/Swagger documentation
- Workspace management
- PDF and CSV document upload foundation
- Workspace-scoped document storage
- SHA-256 document checksums for duplicate detection
- PostgreSQL persistence with SQLAlchemy
- Document lifecycle states: `uploaded`, `processing`, `processed`, `indexed`, `failed`
- PDF text extraction with page-level output
- Configurable text chunking with overlap support
- Persistent `document_chunks` table
- pgvector-compatible `384` dimensional embedding column
- Docker Compose development environment
- Health endpoint for backend monitoring

## API

When the backend is running locally:

- Swagger UI: `http://127.0.0.1:8200/docs`
- OpenAPI JSON: `http://127.0.0.1:8200/openapi.json`
- Health: `http://127.0.0.1:8200/health`

### Workspace Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/workspaces` | List workspaces |
| POST | `/workspaces` | Create workspace |
| GET | `/workspaces/{workspace_id}` | Get workspace |

### Document Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/workspaces/{workspace_id}/documents` | Upload a document |

Example upload with cURL:

```bash
curl -X POST \
  "http://127.0.0.1:8200/workspaces/<WORKSPACE_ID>/documents" \
  -H "accept: application/json" \
  -F "file=@attention-is-all-you-need.pdf;type=application/pdf"
```

## Architecture

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
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   └── workspace.py
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
└── README.md
```

## Tech Stack

**Backend**
- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic / pydantic-settings

**Database**
- PostgreSQL
- pgvector

**Document Processing**
- PyPDF-based PDF extraction
- Custom text chunking
- SHA-256 checksums

**Infrastructure**
- Docker
- Docker Compose

## Database Model

The core knowledge model currently includes:

### Workspace

Logical tenant/container for enterprise knowledge.

### Document

Stores document metadata including:

- Workspace ID
- Filename
- Source type
- MIME type
- Storage path
- File size
- SHA-256 checksum
- Processing status
- Error information
- Creation/update timestamps

### DocumentChunk

Stores retrieval-ready text units:

- Document ID
- Chunk index
- Chunk text
- Character count
- Vector embedding (`Vector(384)`)
- Creation timestamp

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/deekshitaa1/OmniRAG.git
cd OmniRAG
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r ..\requirements.txt
```

### 4. Configure environment variables

Create `backend/.env`:

```env
APP_NAME=OmniRAG
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://omnirag:omnirag@localhost:55433/omnirag
```

Do not commit `.env` or credentials.

### 5. Start PostgreSQL

From the repository root:

```bash
docker compose up -d
```

Verify the database container:

```bash
docker ps
```

### 6. Start the API

From `backend/`:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8200
```

Open:

```text
http://127.0.0.1:8200/docs
```

## Ingestion Example

The current ingestion workflow can process a PDF into structured pages and chunks.

Example:

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
- [x] Chunk database model
- [x] pgvector-ready embedding column

### Phase 2 — Retrieval Engine

- [ ] Embedding generation service
- [ ] Batch embedding pipeline
- [ ] Vector persistence
- [ ] Similarity search
- [ ] Top-k retrieval
- [ ] Metadata filtering
- [ ] Hybrid keyword + vector retrieval

### Phase 3 — RAG Layer

- [ ] LLM provider abstraction
- [ ] Retrieval-augmented prompt construction
- [ ] Context window management
- [ ] Source citations
- [ ] Streaming responses
- [ ] Conversation/session management

### Phase 4 — Enterprise Platform

- [ ] Authentication and authorization
- [ ] Multi-tenant isolation
- [ ] Role-based access control
- [ ] Background ingestion workers
- [ ] Redis-based task queue
- [ ] Observability and structured logging
- [ ] Rate limiting
- [ ] API versioning
- [ ] Production deployment

## Engineering Goals

OmniRAG is being developed with a focus on:

- Modular service boundaries
- Strong data isolation between workspaces
- Idempotent document ingestion
- Deterministic document hashing
- Reliable ingestion state transitions
- Vector-search scalability
- Testability
- Production-oriented API design
- Clear separation between ingestion, retrieval, and generation

## Security Notes

Never commit:

- `.env` files
- API keys
- Database passwords
- Private certificates
- Local virtual environments
- Uploaded enterprise documents

The repository `.gitignore` excludes local environments, secrets, caches, and local document storage.

## Project Status

OmniRAG is currently in the **backend ingestion and knowledge-indexing phase**. The foundation is operational; the next major milestone is connecting the stored chunks to an embedding model and implementing vector retrieval for end-to-end RAG.

## Author

**Deekshita Rajesh Naik**

GitHub: https://github.com/deekshitaa1

---

Built with Python, FastAPI, PostgreSQL, and vector search technologies.
