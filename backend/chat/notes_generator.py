import google.generativeai as genai
from backend.config import settings
from backend.chat.retriever import Retriever

class NotesGenerator:

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        self.retriever = Retriever()

    def generate_notes(self, topic):

        chunks = self.retriever.retrieve(topic)
        context = self.retriever.format_context(chunks)

        if not context:
            return "No relevant course material found."

        prompt = f"""
Use ONLY the given course material.

COURSE MATERIAL:
{context}

Generate concise study notes in bullet points.
"""

        response = self.model.generate_content(prompt)

        return response.text