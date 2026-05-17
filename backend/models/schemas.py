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


# --- Week 2 RAG Chat Schemas ---

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    session_id: str = Field(default="default")
    model_config = ConfigDict(from_attributes=True)

class ContextChunk(BaseModel):
    source: str
    relevance_score: float
    rank: int
    model_config = ConfigDict(from_attributes=True)

class FaithfulnessCheck(BaseModel):
    faithfulness: str
    answer_length: int
    has_disclaimer: bool
    model_config = ConfigDict(from_attributes=True)

class TimingInfo(BaseModel):
    retrieval_seconds: float
    generation_seconds: float
    memory_seconds: float
    total_seconds: float
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    answer: str
    question: str
    session_id: str
    sources: List[str]
    chunks_used: int
    context_relevance: List[ContextChunk]
    faithfulness_check: FaithfulnessCheck
    model_used: str
    generation_success: bool
    timing: TimingInfo
    timestamp: str
    turn_number: int
    model_config = ConfigDict(from_attributes=True)

class HistoryMessage(BaseModel):
    turn_number: int
    timestamp: str
    question: str
    answer: str
    sources: List[str]
    chunks_used: int
    model_config = ConfigDict(from_attributes=True)

class HistoryResponse(BaseModel):
    session_id: str
    total_turns: int
    messages: List[HistoryMessage]
    model_config = ConfigDict(from_attributes=True)

class AllSessionsResponse(BaseModel):
    total_sessions: int
    sessions: List[Dict[str, Any]]
    model_config = ConfigDict(from_attributes=True)

class ClearHistoryResponse(BaseModel):
    status: str
    session_id: str
    message: str
    model_config = ConfigDict(from_attributes=True)
