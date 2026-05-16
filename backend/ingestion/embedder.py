import os
import time
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Embedder:
    """
    Improved Embedder using local sentence-transformers (all-MiniLM-L6-v2).
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Local embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise RuntimeError(
                "Failed to load embedding model.\n"
                "Run: uv add sentence-transformers"
            ) from e

    def generate_embeddings(self, chunks: List[Dict[str, Any]], batch_size: int = 32) -> List[Dict[str, Any]]:
        if not chunks:
            logger.warning("No chunks to embed")
            return []

        total = len(chunks)
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            text = chunk.get("text", "").strip()
            if not text:
                logger.warning(f"Skipped empty chunk: {chunk.get('chunk_id', 'unknown')}")
                continue
            if len(text) > 1000:
                chunk["text"] = text[:1000]
                chunk["truncated"] = True
                logger.warning(f"Truncated long chunk: {chunk.get('chunk_id', 'unknown')}")
            valid_chunks.append(chunk)

        if not valid_chunks:
            return []

        total_valid = len(valid_chunks)
        num_batches = (total_valid + batch_size - 1) // batch_size
        success_count = 0

        print(f"Embedding {total_valid} chunks in {num_batches} batches")

        for b in range(num_batches):
            start = b * batch_size
            end = min((b + 1) * batch_size, total_valid)
            batch_chunks = valid_chunks[start:end]
            batch_texts = [c["text"] for c in batch_chunks]
            
            print(f"Batch {b+1}/{num_batches}: {start}-{end} chunks...")
            
            start_time = time.time()
            try:
                embeddings = self.model.encode(
                    batch_texts, 
                    normalize_embeddings=True, 
                    convert_to_numpy=True
                )
                
                if len(embeddings[0]) != 384:
                    raise ValueError(f"Unexpected embedding dimension: {len(embeddings[0])}")

                for j, emb in enumerate(embeddings):
                    batch_chunks[j]["embedding"] = emb.tolist()
                    success_count += 1
                
                duration = round(time.time() - start_time, 2)
                print(f"Batch {b+1} done in {duration}s")
                
            except Exception as e:
                logger.error(f"Batch {b+1} failed: {str(e)}. Attempting individually...")
                for chunk in batch_chunks:
                    try:
                        embedding = self._embed_single_with_retry(chunk["text"])
                        chunk["embedding"] = embedding.tolist()
                        success_count += 1
                    except Exception as single_e:
                        logger.error(f"Failed to embed chunk {chunk.get('chunk_id')}: {str(single_e)}")

        print(f"Embedding complete: {success_count}/{total} chunks")
        return valid_chunks

    def _embed_single_with_retry(self, text: str) -> np.ndarray:
        try:
            return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
        except Exception:
            time.sleep(1)
            return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True)
