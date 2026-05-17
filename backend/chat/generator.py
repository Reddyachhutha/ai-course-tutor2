import time
import logging
import re
from typing import List, Dict, Any
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument, GoogleAPICallError
from backend.config import settings

logger = logging.getLogger(__name__)

class Generator:
    """
    Generator class that orchestrates prompts and calls the Google Gemini API (gemini-2.0-flash).
    Includes anti-hallucination guardrails and conversational greetings logic.
    """
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model_name = settings.LLM_MODEL
            self.model = genai.GenerativeModel(self.model_name)
            print(f"Generator ready: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API for Generator: {str(e)}")
            raise RuntimeError("Failed to initialize Generator with Gemini API key.") from e

        # Strict System Prompt
        self.system_prompt_template = """
You are an intelligent and helpful AI tutor assistant.
Your job is to help students understand their course material.

STRICT RULES YOU MUST ALWAYS FOLLOW:
======================================
1. You MUST answer using ONLY the context provided below.
2. Do NOT use any outside knowledge or training data.
3. If the answer is NOT found in the context, respond EXACTLY:
   "I could not find information about this topic in your course material. Please refer to your instructor or check if the relevant section has been uploaded."
4. NEVER make up facts, dates, names, or information.
5. NEVER say "I think" or "I believe" -- only state what the context confirms.
6. Always be encouraging and supportive to the student.
7. Format your answer clearly using short paragraphs, bullet points, and bold text for key terms.
8. End every answer with:
   "This answer is based on your uploaded course material."

COURSE MATERIAL CONTEXT:
=========================
{context}
=========================
"""

    def _check_if_greeting(self, text: str) -> bool:
        """
        Check if the input question is a simple greeting or introductory question.
        Allows the system to bypass the strict RAG rejection template for conversational courtesy.
        """
        cleaned = re.sub(r'[^\w\s]', '', text.lower()).strip()
        greetings = {
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon", 
            "good evening", "howdy", "who are you", "what is your name",
            "what are you", "help", "menu", "how are you", "thanks", "thank you"
        }
        return cleaned in greetings or cleaned.startswith(("hi ", "hello ", "hey ", "thanks ", "thank you "))

    def _get_greeting_response(self, question: str) -> str:
        """Returns standard friendly tutor greeting response."""
        cleaned = re.sub(r'[^\w\s]', '', question.lower()).strip()
        if cleaned in {"thanks", "thank you", "thanks!", "thank you!"} or cleaned.startswith("thanks"):
            return (
                "You are very welcome! If you have any other questions about your syllabus "
                "or course content, please don't hesitate to ask.\n\n"
                "This answer is based on your uploaded course material."
            )
            
        return (
            "Hello! I am your personalized AI Course Tutor. I am here to help you study and "
            "understand your course material accurately.\n\n"
            "Please ask me any questions based on the uploaded syllabus, and I will search the "
            "material to explain it clearly!\n\n"
            "This answer is based on your uploaded course material."
        )

    def build_messages(self, question: str, context: str, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Builds conversation messages formatted correctly for Google Gemini API.
        Maps roles and appends system context as user's primary prompt.
        """
        filled_system = self.system_prompt_template.format(context=context)
        
        # Convert last 6 history turns to Gemini API format
        gemini_history = []
        for turn in history[-6:]:
            role = "model" if turn["role"] == "assistant" else "user"
            gemini_history.append({
                "role": role,
                "parts": [turn["content"]]
            })
            
        # Append system context + current user question
        gemini_history.append({
            "role": "user",
            "parts": [f"{filled_system}\n\nStudent Question: {question}"]
        })
        
        return gemini_history

    def generate(self, question: str, context: str, history: List[Dict[str, Any]] = []) -> Dict[str, Any]:
        """
        Generates structured response via Gemini Flash 3 API.
        Includes automated retries with backoff for rate limits.
        """
        # EDGE CASE 1: Simple greeting check (conversational courtesy)
        if self._check_if_greeting(question):
            return {
                "answer": self._get_greeting_response(question),
                "model": self.model_name,
                "generation_success": True
            }

        # EDGE CASE 2: No context found fallback
        if not context or context == "No relevant context found.":
            fallback = (
                "I could not find information about this topic in your course material. "
                "Please refer to your instructor or check if the relevant section has been uploaded."
            )
            return {
                "answer": fallback,
                "model": self.model_name,
                "generation_success": True
            }

        retries = 3
        backoff_delay = 5.0

        for attempt in range(retries):
            try:
                # Build messages in the format expected by the generate_content API
                messages = self.build_messages(question, context, history)
                
                response = self.model.generate_content(messages)
                
                # Clean and validate response text
                answer = response.text.strip() if response.text else ""
                
                if not answer:
                    raise ValueError("Generated response is empty.")
                    
                return {
                    "answer": answer,
                    "model": self.model_name,
                    "generation_success": True
                }

            except ResourceExhausted as e:
                if attempt < retries - 1:
                    logger.warning(f"Rate limit hit on generation (Attempt {attempt+1}/{retries}). Waiting {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2.0
                else:
                    logger.error(f"Gemini API Rate Limit hit: {e}")
                    return {
                        "answer": "The server is currently busy answering other students. Please try again in a few seconds.",
                        "model": self.model_name,
                        "generation_success": False
                    }
            except InvalidArgument as e:
                logger.error(f"Invalid API arguments: {e}")
                return {
                    "answer": "An error occurred formulating the response. Please rephrase your question.",
                    "model": self.model_name,
                    "generation_success": False
                }
            except GoogleAPICallError as e:
                if attempt < retries - 1:
                    logger.warning(f"Google API error on generation (Attempt {attempt+1}/{retries}): {e}. Waiting {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2.0
                else:
                    logger.error(f"Google API call error: {e}")
                    return {
                        "answer": "Failed to reach Google Gemini API. Please check your network connection.",
                        "model": self.model_name,
                        "generation_success": False
                    }
            except Exception as e:
                logger.error(f"Unexpected generator error: {e}")
                return {
                    "answer": "An unexpected error occurred in the generative system.",
                    "model": self.model_name,
                    "generation_success": False
                }

    def validate_answer(self, answer: str, context: str) -> Dict[str, Any]:
        """
        Validate answer's faithfulness and format attributes.
        """
        disclaimer_phrases = [
            "could not find information",
            "not found in your course material",
            "not covered"
        ]
        has_disclaimer = any(phrase in answer.lower() for phrase in disclaimer_phrases)
        
        return {
            "faithfulness": "faithful" if has_disclaimer or "This answer is based on your uploaded course material." in answer else "assumed_faithful",
            "answer_length": len(answer),
            "has_disclaimer": has_disclaimer
        }
