# PLAN: AI Tutor Ingestion Pipeline

## Overview
This plan covers the implementation of the Week 1 goal for the `ai-tutor` project: a complete PDF-to-Vector ingestion pipeline.

**Project Type**: BACKEND
**Primary Agent**: `backend-specialist`

## Success Criteria
- [ ] `uv` environment initialized and all dependencies installed.
- [ ] PDFs can be parsed into clean text.
- [ ] Text is chunked with metadata (filename, page).
- [ ] Embeddings generated via OpenRouter (MiniMax M2).
- [ ] Vectors stored in local persistent ChromaDB.
- [ ] FastAPI endpoint `/upload` successfully processes a PDF.

## Tech Stack
- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **Package Manager**: `uv`
- **NLP/RAG**: LangChain, PyPDF2
- **Vector DB**: ChromaDB (Local)
- **Embeddings**: OpenRouter (Minimax M2)

## File Structure
```text
ai-tutor/
├── .env                  # Secrets & Config
├── pyproject.toml        # uv configuration
├── backend/
│   ├── main.py           # FastAPI Entry point
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py # Text extraction
│   │   ├── chunker.py    # Recursive splitting
│   │   ├── embedder.py   # OpenRouter integration
│   │   └── pipeline.py   # Orchestrator
│   └── database/
│       ├── __init__.py
│       └── vector_store.py # ChromaDB wrapper
└── tests/
    └── test_pipeline.py  # E2E Test script
```

## Task Breakdown

### Phase 1: Environment Setup
- **Task 1.1**: Initialize `uv` and install dependencies.
  - **Agent**: `backend-specialist`
  - **Skill**: `python-patterns`
  - **Verify**: `uv run python -c "import fastapi, langchain, chromadb"`
- **Task 1.2**: Create `.env` template.
  - **Agent**: `backend-specialist`

### Phase 2: Ingestion Logic
- **Task 2.1**: Implement `pdf_parser.py`.
  - **Verify**: Run with sample PDF, check text output.
- **Task 2.2**: Implement `chunker.py`.
  - **Verify**: Check metadata fields (page, source).
- **Task 2.3**: Implement `embedder.py`.
  - **Verify**: Print vector length (should be 1536 or model-specific dim).

### Phase 3: Storage & API
- **Task 3.1**: Implement `vector_store.py`.
  - **Verify**: Check `chroma_data/` directory creation.
- **Task 3.2**: Implement `pipeline.py` (Orchestrator).
- **Task 3.3**: Implement `main.py` (FastAPI).
  - **Verify**: Test `/health` and `/stats` endpoints.

### Phase 4: Verification
- **Task 4.1**: Create and run `tests/test_pipeline.py`.
  - **Verify**: Successful upload and similarity search.

## Phase X: Verification Checklist
- [ ] Security: No hardcoded secrets.
- [ ] Lint: `ruff check .`
- [ ] Type Check: `mypy .`
- [ ] E2E: Sample PDF processed and searchable.
