import time
import logging
from datetime import datetime
from typing import Dict, Any
from backend.chat.retriever import Retriever
from backend.chat.generator import Generator
from backend.chat.memory import ConversationMemory

logger = logging.getLogger(__name__)

class RAGChain:
    """
    RAGChain orchestrates the Retriever, Generator, and ConversationMemory 
    into a unified chat response pipeline with precise timing telemetry.
    """
    
    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()
        self.memory = ConversationMemory()
        print("RAGChain initialization complete: RAG Chat is fully operational.")

    def chat(self, question: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Executes end-to-end RAG workflow:
        Query -> Retrieve Context -> Format -> LLM Chat -> Save Turn -> Response
        """
        start_total = time.time()
        
        # 1. Input Validation
        if not question or not question.strip():
            raise ValueError("Student question cannot be empty.")
            
        question = question.strip()
        
        # 2. Retrieve Context (with Timing)
        t_start = time.time()
        # Greetings bypass retriever check internally to prevent retrieving context
        is_greeting = self.generator._check_if_greeting(question)
        
        if is_greeting:
            chunks = []
            formatted_context = ""
            sources = []
        else:
            chunks = self.retriever.retrieve(question)
            formatted_context = self.retriever.format_context(chunks)
            sources = self.retriever.get_unique_sources(chunks)
            
        retrieval_seconds = round(time.time() - t_start, 4)

        # 3. Generate Answer (with Timing)
        t_start = time.time()
        history = self.memory.get_context_messages(session_id)
        
        gen_res = self.generator.generate(
            question=question,
            context=formatted_context,
            history=history
        )
        generation_seconds = round(time.time() - t_start, 4)

        # 4. Save Turn to Memory (with Timing)
        t_start = time.time()
        turn_data = self.memory.add_turn(
            session_id=session_id,
            question=question,
            answer=gen_res["answer"],
            sources=sources,
            chunks_used=len(chunks)
        )
        memory_seconds = round(time.time() - t_start, 4)

        # 5. Faithfulness Check
        faithfulness_check = self.generator.validate_answer(
            answer=gen_res["answer"],
            context=formatted_context
        )

        total_seconds = round(time.time() - start_total, 4)

        # Build Context Chunks list matching response schemas
        context_chunks_response = []
        for i, c in enumerate(chunks):
            context_chunks_response.append({
                "source": c["source"],
                "relevance_score": c["relevance_score"],
                "rank": c["rank"]
            })

        return {
            "answer": gen_res["answer"],
            "question": question,
            "session_id": session_id,
            "sources": sources,
            "chunks_used": len(chunks),
            "context_relevance": context_chunks_response,
            "faithfulness_check": faithfulness_check,
            "model_used": gen_res["model"],
            "generation_success": gen_res["generation_success"],
            "timing": {
                "retrieval_seconds": retrieval_seconds,
                "generation_seconds": generation_seconds,
                "memory_seconds": memory_seconds,
                "total_seconds": total_seconds
            },
            "timestamp": turn_data["timestamp"],
            "turn_number": turn_data["turn_number"]
        }
