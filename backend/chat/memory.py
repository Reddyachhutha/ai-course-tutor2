from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any

class ConversationMemory:
    """
    Manages in-memory chat session histories for students.
    Designed with a clean interface to easily replace with database storage in the future.
    """
    
    def __init__(self):
        self.sessions = defaultdict(list)

    def add_turn(
        self, 
        session_id: str, 
        question: str, 
        answer: str, 
        sources: List[str], 
        chunks_used: int
    ) -> Dict[str, Any]:
        """
        Appends a conversational turn to a session's history.
        """
        turn_number = len(self.sessions[session_id]) + 1
        turn = {
            "turn_number": turn_number,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "sources": sources,
            "chunks_used": chunks_used
        }
        self.sessions[session_id].append(turn)
        return turn

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the structured turn list for a session.
        """
        return self.sessions.get(session_id, [])

    def get_context_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves in-context message pairs formatted as:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        for model chat history feeds.
        """
        history = self.get_history(session_id)
        messages = []
        for turn in history:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        return messages

    def clear_session(self, session_id: str) -> bool:
        """
        Wipes a session's history completely.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Retrieves summaries of all active sessions in memory.
        """
        summary = []
        for sid, turns in self.sessions.items():
            summary.append({
                "session_id": sid,
                "total_turns": len(turns),
                "last_active": turns[-1]["timestamp"] if turns else None
            })
        return summary
