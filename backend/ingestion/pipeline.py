import os
import time
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from backend.ingestion.pdf_parser import extract_text_from_pdf
from backend.ingestion.chunker import chunk_text
from backend.ingestion.embedder import Embedder
from backend.database.vector_store import VectorStore
from backend.config import settings

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def process_pdf(self, file_path: str, progress_callback: Optional[Callable[[str, int], None]] = None) -> Dict[str, Any]:
        start_total = time.time()
        step_times = {}
        completed_steps = []
        
        if not file_path:
            return {"status": "error", "message": "File path is empty"}
            
        path = Path(file_path)
        filename = path.name
        
        if not path.exists():
            return {"status": "error", "message": f"File not found: {filename}"}

        logger.info(f"--- Starting ingestion for: {filename} ---")
        
        sources = self.vector_store.list_sources()
        is_duplicate = filename in sources
        if is_duplicate:
            print(f"File already ingested: {filename}. Updating existing records.")

        try:
            if progress_callback: progress_callback("parsing", 25)
            t_start = time.time()
            parse_res = extract_text_from_pdf(file_path)
            step_times["parsing"] = round(time.time() - t_start, 2)
            
            if not parse_res or not parse_res.get("text"):
                return {"status": "error", "message": "Parsing failed or returned no text", "completed_steps": completed_steps}
            completed_steps.append("parsing")
            
            if progress_callback: progress_callback("chunking", 50)
            t_start = time.time()
            chunks = chunk_text(parse_res["text"], filename)
            step_times["chunking"] = round(time.time() - t_start, 2)
            
            if not chunks:
                return {"status": "error", "message": "No usable text chunks extracted.", "completed_steps": completed_steps}
            completed_steps.append("chunking")
            
            if progress_callback: progress_callback("embedding", 75)
            t_start = time.time()
            chunks_with_embeddings = self.embedder.generate_embeddings(chunks)
            step_times["embedding"] = round(time.time() - t_start, 2)
            
            if not chunks_with_embeddings:
                return {"status": "error", "message": "Embedding failed.", "completed_steps": completed_steps}
            completed_steps.append("embedding")
            
            if progress_callback: progress_callback("storing", 100)
            t_start = time.time()
            stored_count = self.vector_store.upsert_chunks(chunks_with_embeddings)
            step_times["storing"] = round(time.time() - t_start, 2)
            completed_steps.append("storing")
            
            total_time = round(time.time() - start_total, 2)
            logger.info(f"--- Ingestion complete for: {filename} in {total_time}s ---")
            
            return {
                "status": "success",
                "filename": filename,
                "file_size_mb": parse_res["file_size_mb"],
                "pages_parsed": parse_res["pages"],
                "pages_with_text": parse_res["pages_with_text"],
                "pages_skipped": parse_res["pages_skipped"],
                "chunks_created": len(chunks),
                "chunks_stored": stored_count,
                "duplicate_upload": is_duplicate,
                "scanned_pdf": parse_res["scanned_pdf"],
                "warning": parse_res["warning"],
                "total_time_seconds": total_time,
                "step_times": step_times,
                "completed_steps": completed_steps
            }
        except Exception as e:
            logger.error(f"Pipeline failed for {filename}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "failed_at_step": completed_steps[-1] if completed_steps else "init",
                "completed_steps": completed_steps
            }
