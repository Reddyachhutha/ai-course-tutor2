import chromadb
from chromadb.config import Settings
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Hardened wrapper for ChromaDB with robust error handling and management methods.
    Includes automated collection verification and dimension checks.
    """
    
    def __init__(self):
        self.db_path = str(settings.CHROMA_PERSIST_DIR)
        self.collection_name = settings.COLLECTION_NAME
        
        try:
            settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # AUTOMATED DIMENSION CHECK & SELF-HEALING
            count = self.collection.count()
            if count > 0:
                try:
                    # Peek to check the embedding dimension
                    peek_res = self.collection.peek(limit=1)
                    if peek_res and peek_res.get("embeddings") and len(peek_res["embeddings"]) > 0:
                        existing_dim = len(peek_res["embeddings"][0])
                        if existing_dim != settings.EMBEDDING_DIMENSION:
                            logger.warning(
                                f"Dimension mismatch detected in collection '{self.collection_name}'. "
                                f"Existing: {existing_dim}, Expected: {settings.EMBEDDING_DIMENSION}. Recreating collection..."
                            )
                            self.reset_collection()
                            count = 0
                except Exception as peek_err:
                    logger.error(f"Failed to verify dimension: {peek_err}. Resetting collection as precaution.")
                    self.reset_collection()
                    count = 0

            print(f"Connected to collection: {self.collection_name} ({count} chunks)")
        except Exception as e:
            logger.error(f"ChromaDB connection failed at {self.db_path}: {str(e)}")
            raise RuntimeError(f"ChromaDB connection failed at {self.db_path}") from e

    def upsert_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            print("No chunks to store")
            return 0
            
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for chunk in chunks:
            if "embedding" not in chunk or chunk["embedding"] is None:
                print(f"Skipped chunk missing embedding: {chunk.get('chunk_id')}")
                continue
            
            # Double-check dimension before storing
            if len(chunk["embedding"]) != settings.EMBEDDING_DIMENSION:
                print(f"Skipped chunk due to dimension mismatch: {chunk.get('chunk_id')}")
                continue
                
            ids.append(chunk["chunk_id"])
            embeddings.append(chunk["embedding"])
            documents.append(chunk["text"])
            meta = {k: v for k, v in chunk.items() if k not in ["text", "embedding"]}
            metadatas.append(meta)

        if not ids:
            return 0

        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            return len(ids)
        except Exception as e:
            logger.error(f"Error storing to ChromaDB: {str(e)}")
            raise

    def query(self, query_vector: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        if not query_vector:
            logger.warning("Query embedding is empty")
            return []
            
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=n_results
            )
            if not results["ids"] or not results["ids"][0]:
                print("No relevant chunks found for query")
                return []

            formatted_results = []
            for i in range(len(results["ids"][0])):
                dist = results["distances"][0][i]
                relevance = round(1 - dist, 3)
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i].get("source"),
                    "chunk_index": results["metadatas"][0][i].get("chunk_index"),
                    "char_count": len(results["documents"][0][i]),
                    "distance": round(dist, 3),
                    "relevance_score": relevance,
                    "rank": i + 1,
                    "chunk_id": results["ids"][0][i]
                })
            # Ensure return sorted by relevance descending
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return formatted_results
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return []

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        try:
            res = self.collection.get(ids=[chunk_id])
            if res["ids"]:
                return {
                    "chunk_id": res["ids"][0],
                    "text": res["documents"][0],
                    "metadata": res["metadatas"][0]
                }
            return None
        except Exception:
            return None

    def list_sources(self) -> List[str]:
        try:
            metas = self.collection.get(include=["metadatas"])["metadatas"]
            sources = sorted(list(set([m.get("source") for m in metas if m.get("source")])))
            print(f"Sources: {sources}")
            return sources
        except Exception:
            return []

    def get_count(self) -> int:
        return self.collection.count()

    def reset_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.warning(f"Collection '{self.collection_name}' has been reset.")
