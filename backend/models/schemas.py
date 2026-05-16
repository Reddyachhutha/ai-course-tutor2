from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional

class HealthResponse(BaseModel):
    status: str
    app_title: str
    app_version: str
    llm_model: str
    llm_provider: str
    embedding_model: str
    embedding_type: str
    vector_db: str
    total_chunks: int
    timestamp: str
    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    status: str
    filename: str
    file_size_mb: float
    pages_parsed: int
    pages_with_text: int
    chunks_created: int
    chunks_stored: int
    total_time_seconds: float
    step_times: Dict[str, float]
    message: str
    model_config = ConfigDict(from_attributes=True)

class StatsResponse(BaseModel):
    total_chunks: int
    collection_name: str
    persist_dir: str
    status: str
    last_updated: str
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: str = ""
    suggestion: str = ""
    model_config = ConfigDict(from_attributes=True)

class ResetResponse(BaseModel):
    status: str
    message: str
    previous_chunk_count: int
    model_config = ConfigDict(from_attributes=True)

class ChunkInfo(BaseModel):
    chunk_id: str
    source: str
    chunk_index: int
    char_count: int
    text_preview: str
    model_config = ConfigDict(from_attributes=True)

class InspectResponse(BaseModel):
    total_chunks: int
    collection_name: str
    sample_chunks: List[ChunkInfo]
    model_config = ConfigDict(from_attributes=True)
