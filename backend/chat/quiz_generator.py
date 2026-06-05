import google.generativeai as genai
from backend.config import settings
from backend.chat.retriever import Retriever

class QuizGenerator:

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.retriever = Retriever()

    def generate_quiz(self, topic):
        print("NEW QUIZ GENERATOR RUNNING")

        # Retrieve relevant chunks from ChromaDB
        chunks = self.retriever.retrieve(topic)

        # Convert chunks into context
        context = self.retriever.format_context(chunks)

        # If nothing found
        if not context:
            return "No relevant course material found for this topic."

        prompt = f"""
You are an AI tutor.

Use ONLY the given course material.

COURSE MATERIAL:
{context}

Generate 5 multiple choice questions.

Return ONLY valid JSON in this format:

{{
  "questions": [
    {{
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}

Rules:
- Only use given context
- No extra text
- Strict JSON only
"""

        response = self.model.generate_content(prompt)

        return response.text