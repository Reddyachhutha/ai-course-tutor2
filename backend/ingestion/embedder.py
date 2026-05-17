import time
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPICallError
from backend.config import settings

logger = logging.getLogger(__name__)

class Embedder:
    """
    Improved Embedder using 100% Google Gemini API (gemini-embedding-001).
    Includes batch processing, exponential backoff retry logic, and error handling.
    """
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model_name = settings.EMBEDDING_MODEL
            self.dimension = settings.EMBEDDING_DIMENSION
            print(f"Embedder ready: Gemini API ({self.model_name})")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            raise RuntimeError("Failed to initialize Embedder with Gemini API key.") from e

    def generate_embeddings(self, chunks: List[Dict[str, Any]], batch_size: int = 20) -> List[Dict[str, Any]]:
        """
        Generates embeddings for a list of chunk objects using Gemini API.
        
        Args:
            chunks (List[Dict[str, Any]]): List of chunk dicts with a "text" key.
            batch_size (int): Size of batches for processing (Gemini API optimal is 20).
            
        Returns:
            List[Dict[str, Any]]: The original chunks updated with "embedding" key.
        """
        if not chunks:
            logger.warning("No chunks to embed")
            return []

        total = len(chunks)
        valid_chunks = []
        for chunk in chunks:
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

        print(f"Embedding {total_valid} chunks in {num_batches} batches via Gemini API")

        for b in range(num_batches):
            start = b * batch_size
            end = min((b + 1) * batch_size, total_valid)
            batch_chunks = valid_chunks[start:end]
            batch_texts = [c["text"] for c in batch_chunks]
            
            print(f"Embedding batch {b+1}/{num_batches} via Gemini API...")
            
            # Implementation of exponential backoff retry loop
            retries = 3
            backoff_delay = 5.0
            embeddings = None
            
            for attempt in range(retries):
                try:
                    response = genai.embed_content(
                        model=self.model_name,
                        content=batch_texts,
                        task_type="retrieval_document",
                        output_dimensionality=self.dimension
                    )
                    embeddings = response.get("embedding")
                    break
                except ResourceExhausted as e:
                    logger.warning(f"Rate limit hit on batch {b+1} (Attempt {attempt+1}/{retries}): {e}. Waiting {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2.0
                except GoogleAPICallError as e:
                    logger.error(f"API Error on batch {b+1} (Attempt {attempt+1}/{retries}): {e}. Waiting {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2.0
                except Exception as e:
                    logger.error(f"Unexpected error on batch {b+1}: {e}")
                    raise

            if embeddings is None:
                logger.error(f"Failed to generate embeddings for batch {b+1} after all retries.")
                continue

            # Verify dimension and assign
            for j, emb in enumerate(embeddings):
                if len(emb) != self.dimension:
                    logger.error(f"Vector dimension mismatch! Expected {self.dimension}, got {len(emb)}")
                    continue
                batch_chunks[j]["embedding"] = emb
                success_count += 1

        print(f"Embedding complete: {success_count}/{total} chunks successfully embedded")
        return [c for c in valid_chunks if "embedding" in c]

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single query string for vector search.
        
        Args:
            query (str): The query string.
            
        Returns:
            List[float]: The 768-dimensional embedding vector.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty")
            
        retries = 3
        backoff_delay = 3.0
        
        for attempt in range(retries):
            try:
                response = genai.embed_content(
                    model=self.model_name,
                    content=query,
                    task_type="retrieval_query",
                    output_dimensionality=self.dimension
                )
                embedding = response.get("embedding")
                if embedding:
                    # Check dimension
                    if len(embedding) != self.dimension:
                        raise ValueError(f"Vector dimension mismatch! Expected {self.dimension}, got {len(embedding)}")
                    return embedding
                raise ValueError("Embedding key missing in response")
            except ResourceExhausted as e:
                logger.warning(f"Rate limit hit on query (Attempt {attempt+1}/{retries}). Waiting {backoff_delay}s...")
                time.sleep(backoff_delay)
                backoff_delay *= 2.0
            except GoogleAPICallError as e:
                logger.error(f"API Error on query (Attempt {attempt+1}/{retries}). Waiting {backoff_delay}s...")
                time.sleep(backoff_delay)
                backoff_delay *= 2.0
                
        raise RuntimeError("Failed to embed query after maximum retries.")
