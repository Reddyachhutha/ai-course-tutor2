import google.generativeai as genai
from backend.config import settings
from backend.chat.retriever import Retriever

class FlashcardGenerator:

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.retriever = Retriever()

    def generate_flashcards(self, topic):

        chunks = self.retriever.retrieve(topic)
        context = self.retriever.format_context(chunks)

        if not context:
            return "No relevant course material found."

        prompt = f"""
Use ONLY the course material below.

COURSE MATERIAL:
{context}

Generate 5 flashcards.

Format:

Q: Question
A: Answer

Generate exactly 5 flashcards.
"""

        response = self.model.generate_content(prompt)

        return response.text