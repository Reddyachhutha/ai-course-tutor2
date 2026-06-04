import google.generativeai as genai
from backend.config import settings

class QuizGenerator:

    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.LLM_MODEL)

    def generate_quiz(self, topic):

        prompt = f"""
Generate 5 multiple choice questions about {topic}.

Format:

Q1:
Question
A)
B)
C)
D)

Answer: A

Generate exactly 5 questions.
"""

        response = self.model.generate_content(prompt)

        return response.text