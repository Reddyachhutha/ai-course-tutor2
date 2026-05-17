import logging
from typing import List, Dict, Any, Optional
from backend.ingestion.embedder import Embedder
from backend.database.vector_store import VectorStore
from backend.config import settings

logger = logging.getLogger(__name__)

class Retriever:
    """
    Retriever class responsible for embedding user questions and querying ChromaDB.
    """
    
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.top_k = settings.TOP_K_RESULTS
        print("Retriever ready (Gemini Embeddings)")

    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Embeds the query and fetches top K relevant chunks from vector store.
        """
        # Validate question
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")
        if len(question.strip()) < 3:
            raise ValueError("Question must be at least 3 characters long.")
            
        k = top_k or self.top_k
        logger.info(f"Retrieving top {k} contexts for query: '{question}'")

        try:
            # Embed question
            query_embedding = self.embedder.embed_query(question)
            
            # Query vector store
            results = self.vector_store.query(query_vector=query_embedding, n_results=k)
            
            if not results:
                return []
                
            # Format results and sort by relevance score descending
            formatted = []
            for item in results:
                formatted.append({
                    "text": item.get("text", ""),
                    "source": item.get("source", "unknown"),
                    "chunk_index": item.get("chunk_index", 0),
                    "relevance_score": item.get("relevance_score", 0.0),
                    "rank": item.get("rank", 0)
                })
            
            formatted.sort(key=lambda x: x["relevance_score"], reverse=True)
            return formatted
            
        except Exception as e:
            logger.error(f"Retriever query failed: {str(e)}")
            return []

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Formats list of retrieved chunks into a unified context string.
        """
        if not chunks:
            return "No relevant context found."
            
        formatted_parts = []
        for c in chunks:
            source = c.get("source", "unknown")
            score = c.get("relevance_score", 0.0)
            text = c.get("text", "")
            formatted_parts.append(
                f"[SOURCE]: {source} (Relevance: {score})\n{text}"
            )
            
        return "\n\n---\n\n".join(formatted_parts)

    def get_unique_sources(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Extracts sorted list of unique source filenames from retrieved chunks.
        """
        sources = set()
        for c in chunks:
            src = c.get("source")
            if src:
                sources.add(src)
        return sorted(list(sources))
