import google.generativeai as genai
from backend.config import settings
from backend.chat.retriever import Retriever

class QuizGenerator:

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.retriever = Retriever()

    def generate_quiz(self, topic):

        # Retrieve relevant chunks from ChromaDB
        chunks = self.retriever.retrieve(topic)

        # Convert chunks into context
        context = self.retriever.format_context(chunks)

        # If nothing found
        if not context:
            return "No relevant course material found for this topic."

        prompt = f"""
You are an AI Tutor.

Use ONLY the course material provided below.

COURSE MATERIAL:
{context}

Generate exactly 5 multiple-choice questions.

Format:

Q1:
Question
A)
B)
C)
D)

Answer: A

Rules:
1. Use only the provided course material.
2. Do not use outside knowledge.
3. Do not make up information.
4. Generate exactly 5 MCQs.
5. Include the correct answer after each question.
"""

        response = self.model.generate_content(prompt)

        return response.text