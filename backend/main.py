from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import time
import shutil
import re
import traceback
import logging
from datetime import datetime

from backend.config import settings
from backend.models.schemas import (
    HealthResponse, UploadResponse, StatsResponse, 
    InspectResponse, ResetResponse, ErrorResponse, ChunkInfo
)
from backend.ingestion.pipeline import IngestionPipeline
from backend.database.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION + """
## AI-Powered RAG Tutor System
Upload course materials and get instant AI-powered answers.
""",
    openapi_tags=[
        {"name": "System", "description": "Health checks"},
        {"name": "Ingestion", "description": "Process materials"},
        {"name": "Knowledge Base", "description": "Manage stored knowledge"}
    ]
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} in {process_time}ms")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message="An unexpected error occurred", detail=str(exc)).model_dump()
    )

pipeline = IngestionPipeline()
vector_store = VectorStore()

@app.on_event("startup")
async def startup_event():
    print("+" + "="*38 + "+")
    print("|     AI Course Tutor API v1.0         |")
    print("+" + "="*38 + "+")
    print("|  LLM: Gemini Flash 3                 |")
    print("|  Embeddings: all-MiniLM-L6-v2        |")
    print("|  Vector DB: ChromaDB                 |")
    print("+" + "="*38 + "+")
    count = vector_store.get_count()
    print(f"Knowledge base: {count} chunks ready")

@app.get("/health", tags=["System"], response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        app_title=settings.APP_TITLE,
        app_version=settings.APP_VERSION,
        llm_model="Gemini Flash 3",
        llm_provider="Google",
        embedding_model="all-MiniLM-L6-v2",
        embedding_type="Local",
        vector_db="ChromaDB",
        total_chunks=vector_store.get_count(),
        timestamp=datetime.now().isoformat()
    )

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

@app.get("/stats", tags=["Knowledge Base"], response_model=StatsResponse)
async def stats():
    return StatsResponse(
        total_chunks=vector_store.get_count(),
        collection_name=settings.COLLECTION_NAME,
        persist_dir=str(settings.CHROMA_PERSIST_DIR),
        status="active",
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
