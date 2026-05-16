# 🏗️ Project Architecture Overview

This document explains how the AI Course Tutor works under the hood.

## 🎯 Vision
To simulate a 1-on-1 tutoring experience where the AI knows only what’s in the course material — nothing more, nothing less.

## 🧩 High-Level Flow

```text
Teacher uploads PDF
      ↓
System parses → chunks → embeds → stores
      ↓
Student asks: "Explain photosynthesis?"
      ↓
System finds relevant syllabus section
      ↓
AI answers strictly from that section
```

## 🔒 Anti-Hallucination Design
The system uses Retrieval-Augmented Generation (RAG):

1. **Retrieve** relevant content from the syllabus
2. **Augment** the prompt with that content
3. **Generate** answer using only that context

If the answer isn’t in the retrieved chunks → the AI says “Not covered.”

## ⚙️ Component Breakdown

### 1. PDF Parser (`pdf_parser.py`)
- Uses `PyPDF2` to extract text page-by-page
- Handles edge cases:
    - Scanned/image-based PDFs
    - Corrupted files
    - Password protection
    - Empty pages
- Returns clean, structured text

### 2. Chunker (`chunker.py`)
- Splits text into semantic units (~500 chars)
- Uses LangChain’s `RecursiveCharacterTextSplitter`
- Ensures no information loss at boundaries
- Filters out noise (empty/duplicate chunks)

### 3. Embedder (`embedder.py`)
- Uses local `all-MiniLM-L6-v2` model
- No API key needed — runs on your machine
- Converts each chunk into a 384-dimensional vector
- Enables semantic search (meaning over keywords)

### 4. Vector Store (`vector_store.py`)
- Stores vectors + original text + metadata
- Uses `ChromaDB` with persistent disk storage
- Supports fast similarity search
- Survives application restarts

### 5. Ingestion Pipeline (`pipeline.py`)
- Orchestrates all steps: Parse → Chunk → Embed → Store
- Tracks execution time per step
- Returns detailed results
- Built-in retry and error recovery

### 6. FastAPI Backend (`main.py`)
- RESTful API endpoints
- Input validation and error handling
- Swagger UI auto-generated docs
- Pydantic response models
- Global exception handler
- Request logging middleware

## 📊 Data Flow Diagram

```text
[Upload PDF] → /upload endpoint
                ↓
          validate file type/size
                ↓
           parse_pdf() → raw text
                ↓
          chunk_text() → list of chunks
                ↓
         embed_chunks() → vectors
                ↓
       upsert_chunks() → ChromaDB
                ↓
           return success JSON
```

## 🧪 Testing Strategy
- Unit tests for each module
- Integration test for full pipeline
- Edge case coverage:
    - Missing file
    - Wrong format
    - Empty input
    - Duplicate uploads
    - Large documents
- Performance timing included

## 📈 Success Metrics
| KPI | Target |
|-----|--------|
| Context Relevance | >95% |
| Answer Faithfulness | 100% (no hallucinations) |
| Latency (per turn) | <2 seconds |
| PDF parsing success rate | 98% |
| Developer onboarding time | <15 minutes |

## ➡️ What’s Next? (Week 2)
- Build `/chat` endpoint
- Implement retrieval + generation
- Add conversation memory
- Create Streamlit frontend
- Teacher analytics dashboard

This project proves that trustworthy educational AI is possible.
