from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from typing import List, Optional, Dict, Any
import os
import time
import shutil
import re
import traceback
import logging
from backend.models.schemas import FlashcardRequest, FlashcardResponse
from backend.chat.flashcard_generator import FlashcardGenerator
from datetime import datetime
from backend.chat.notes_generator import NotesGenerator
from backend.chat.summary_generator import SummaryGenerator

from backend.config import settings
from backend.models.schemas import (
    HealthResponse, UploadResponse, StatsResponse, 
    InspectResponse, ResetResponse, ErrorResponse, ChunkInfo,
    ChatRequest, ChatResponse, HistoryResponse, AllSessionsResponse, 
    ClearHistoryResponse, HistoryMessage, ContextChunk, FaithfulnessCheck, TimingInfo, QuizRequest,
QuizResponse, QuizEvaluationRequest,
QuizEvaluationResponse,   NotesRequest, SummaryRequest
)
from backend.chat.quiz_generator import QuizGenerator
from backend.ingestion.pipeline import IngestionPipeline
from backend.database.vector_store import VectorStore
from backend.chat.rag_chain import RAGChain

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION + """
## AI-Powered RAG Tutor System
Upload course materials and chat with them.
The entire system is 100% powered by the Google Gemini API.
""",
    openapi_tags=[
        {"name": "System", "description": "Health and system status check"},
        {"name": "Ingestion", "description": "Upload and parse new course syllabi"},
        {"name": "Knowledge Base", "description": "Browse or reset vector database collections"},
        {"name": "RAG Chat", "description": "Chat with uploaded course material strictly backed by context"}
    ]
)

# ==================== SECURITY MIDDLEWARE ====================

# CORS - Restrict to specific origins in production
cors_origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Trusted Host - Prevent Host Header injection
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# GZIP compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains" if settings.ENFORCE_HTTPS else ""
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response

# Request logging & rate limiting
from collections import defaultdict
from datetime import datetime, timedelta

request_timestamps = defaultdict(list)

@app.middleware("http")
async def rate_limit_and_log(request: Request, call_next):
    # Simple rate limiting (5 requests per minute per IP)
    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)
    
    # Clean old timestamps
    request_timestamps[client_ip] = [
        ts for ts in request_timestamps[client_ip] if ts > cutoff
    ]
    
    # Check rate limit
    if len(request_timestamps[client_ip]) >= 100:  # 100 requests per minute
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"},
        )
    
    request_timestamps[client_ip].append(now)
    
    # Log request
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time}ms - {client_ip}"
    )
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message="An unexpected error occurred", detail=str(exc)).model_dump()
    )

# --- Services Initialization ---
pipeline = IngestionPipeline()
vector_store = VectorStore()
rag_chain = RAGChain()
quiz_generator = QuizGenerator()
flashcard_generator = FlashcardGenerator()
notes_generator = NotesGenerator()
summary_generator = SummaryGenerator()

@app.on_event("startup")
async def startup_event():
    print("+" + "="*38 + "+")
    print("|     AI Course Tutor API v1.0         |")
    print("+" + "="*38 + "+")
    print(f"|  LLM: Gemini Flash 3 ({settings.LLM_MODEL})   |")
    print(f"|  Embeddings: Gemini ({settings.EMBEDDING_MODEL})   |")
    print("|  Vector DB: ChromaDB (768 dims)      |")
    print("+" + "="*38 + "+")
    count = vector_store.get_count()
    sources = vector_store.list_sources()
    print(f"Knowledge base: {count} chunks ready")
    print(f"Sources: {len(sources)} documents loaded")
    
    if sources:
        print(f"Documents loaded: {len(sources)}")
        for source in sources:
            print(f"   * {source}")
    else:
        print("No documents loaded yet")
        print("   Upload a PDF via POST /upload to get started")

# --- System Endpoint ---

@app.get("/health", tags=["System"], response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        app_title=settings.APP_TITLE,
        app_version=settings.APP_VERSION,
        llm_model=settings.LLM_MODEL,
        llm_provider="Google",
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_type="Cloud (Gemini API)",
        vector_db="ChromaDB (768 dimensions)",
        total_chunks=vector_store.get_count(),
        loaded_documents=vector_store.list_sources(),
        timestamp=datetime.now().isoformat()
    )

# --- Ingestion Endpoint ---

@app.post("/upload", tags=["Ingestion"], response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are allowed.")
    filename = file.filename if file.filename else "unknown.pdf"
    clean_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    temp_path = settings.UPLOAD_DIR / clean_filename
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_size_mb = temp_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            os.remove(temp_path)
            raise HTTPException(status_code=413, detail="File too large.")
        result = pipeline.process_pdf(str(temp_path))
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return UploadResponse(
            status="success",
            filename=clean_filename,
            file_size_mb=result["file_size_mb"],
            pages_parsed=result["pages_parsed"],
            pages_with_text=result["pages_with_text"],
            chunks_created=result["chunks_created"],
            chunks_stored=result["chunks_stored"],
            total_time_seconds=result["total_time_seconds"],
            step_times=result["step_times"],
            message="File processed successfully"
        )
    finally:
        if temp_path.exists(): os.remove(temp_path)

# --- Knowledge Base Endpoints ---

@app.get("/stats", tags=["Knowledge Base"], response_model=StatsResponse)
async def stats():
    sources = vector_store.list_sources()
    return StatsResponse(
        total_chunks=vector_store.get_count(),
        collection_name=settings.COLLECTION_NAME,
        persist_dir=str(settings.CHROMA_PERSIST_DIR),
        status="active",
        documents=sources,
        document_count=len(sources),
        last_updated=datetime.now().isoformat()
    )

@app.get("/inspect", tags=["Knowledge Base"], response_model=InspectResponse)
async def inspect(limit: int = Query(5, le=20, ge=1)):
    try:
        res = vector_store.collection.get(limit=limit, include=["documents", "metadatas"])
        chunks = []
        for i in range(len(res["ids"])):
            chunks.append(ChunkInfo(
                chunk_id=res["ids"][i],
                source=res["metadatas"][i].get("source", "unknown"),
                chunk_index=res["metadatas"][i].get("chunk_index", 0),
                char_count=len(res["documents"][i]),
                text_preview=res["documents"][i][:150] + "..."
            ))
        return InspectResponse(
            total_chunks=vector_store.get_count(),
            collection_name=settings.COLLECTION_NAME,
            sample_chunks=chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reset", tags=["Knowledge Base"], response_model=ResetResponse)
async def reset():
    prev_count = vector_store.get_count()
    vector_store.reset_collection()
    return ResetResponse(status="success", message="Cleared", previous_chunk_count=prev_count)

# --- Week 2 RAG Chat Endpoints ---

@app.post("/chat", tags=["RAG Chat"], response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for retrieving syllabus material and generating accurate responses.
    """
    try:
        result = rag_chain.chat(question=request.question, session_id=request.session_id)
        
        # Convert internal dict structure into ChatResponse Pydantic model
        return ChatResponse(
            answer=result["answer"],
            question=result["question"],
            session_id=result["session_id"],
            sources=result["sources"],
            chunks_used=result["chunks_used"],
            context_relevance=[ContextChunk(**cr) for cr in result["context_relevance"]],
            faithfulness_check=FaithfulnessCheck(**result["faithfulness_check"]),
            model_used=result["model_used"],
            generation_success=result["generation_success"],
            timing=TimingInfo(**result["timing"]),
            timestamp=result["timestamp"],
            turn_number=result["turn_number"]
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as err:
        logger.error(f"Chat execution failed: {err}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal RAG Chat pipeline execution failed.")

@app.get("/chat/history/{session_id}", tags=["RAG Chat"], response_model=HistoryResponse)
async def get_history(session_id: str):
    """
    Retrieves all turn history and citations for a specific student's conversation session.
    """
    history = rag_chain.memory.get_history(session_id)
    messages = []
    for turn in history:
        messages.append(HistoryMessage(
            turn_number=turn["turn_number"],
            timestamp=turn["timestamp"],
            question=turn["question"],
            answer=turn["answer"],
            sources=turn["sources"],
            chunks_used=turn["chunks_used"]
        ))
    return HistoryResponse(
        session_id=session_id,
        total_turns=len(messages),
        messages=messages
    )

@app.delete("/chat/history/{session_id}", tags=["RAG Chat"], response_model=ClearHistoryResponse)
async def clear_history(session_id: str):
    """
    Wipes the conversation history for a specific student's conversation session.
    """
    success = rag_chain.memory.clear_session(session_id)
    if success:
        return ClearHistoryResponse(
            status="success",
            session_id=session_id,
            message="Conversation memory cleared successfully."
        )
    raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found in active memory.")

@app.get("/chat/sessions", tags=["RAG Chat"], response_model=AllSessionsResponse)
async def get_sessions():
    """
    Browse a list of all active conversational sessions held in memory.
    """
    sessions = rag_chain.memory.get_all_sessions()
    return AllSessionsResponse(
        total_sessions=len(sessions),
        sessions=sessions
    )
@app.post("/quiz", tags=["RAG Chat"])
async def generate_quiz(request: QuizRequest):

    quiz_text = quiz_generator.generate_quiz(request.topic)

    return {
        "topic": request.topic,
        "difficulty": request.difficulty,
        "quiz": quiz_text
    }

@app.post("/flashcards")
async def generate_flashcards(request: FlashcardRequest):

    cards = flashcard_generator.generate_flashcards(
        request.topic
    )

    return {
        "topic": request.topic,
        "flashcards": cards
    }
@app.post("/quiz/evaluate", response_model=QuizEvaluationResponse)
async def evaluate_quiz(request: QuizEvaluationRequest):

    score = 0

    for correct, user in zip(
        request.correct_answers,
        request.user_answers
    ):
        if correct.upper() == user.upper():
            score += 1

    total = len(request.correct_answers)

    percentage = (
        round((score / total) * 100, 2)
        if total > 0 else 0
    )

    return QuizEvaluationResponse(
        score=score,
        total=total,
        percentage=percentage
    )

@app.post("/notes")
async def generate_notes(request: NotesRequest):

    notes = notes_generator.generate_notes(
        request.topic
    )

    return {
        "topic": request.topic,
        "notes": notes
    }

@app.post("/summary")
async def generate_summary(request: SummaryRequest):

    summary = summary_generator.generate_summary(
        request.topic
    )

    return {
        "topic": request.topic,
        "summary": summary
    }