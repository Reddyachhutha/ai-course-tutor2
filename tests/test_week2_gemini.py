import os
import sys
import time
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.config import settings
from backend.ingestion.embedder import Embedder
from backend.database.vector_store import VectorStore
from backend.chat.retriever import Retriever
from backend.chat.generator import Generator
from backend.chat.memory import ConversationMemory
from backend.chat.rag_chain import RAGChain

class GeminiRAGTestSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.start_time = time.time()
        cls.results = []
        print("="*40)
        print("Week 2 Gemini RAG Chat Test Suite")
        print("="*40)

    def run_test_case(self, name, func):
        t_start = time.time()
        try:
            func()
            duration = round(time.time() - t_start, 2)
            self.results.append((name, "PASS", duration))
            print(f"{name:<35} PASS  {duration}s")
        except Exception as e:
            duration = round(time.time() - t_start, 2)
            self.results.append((name, "FAIL", duration))
            print(f"{name:<35} FAIL  {duration}s - {str(e)}")

    def test_01_embedder_gemini(self):
        def check():
            emb = Embedder()
            vector = emb.embed_query("What is cell division?")
            self.assertEqual(len(vector), 768)
            self.assertIsInstance(vector[0], float)
        self.run_test_case("01 Embedder Dimensions (768)", check)

    def test_02_retriever_basic(self):
        def check():
            ret = Retriever()
            # Clear & populate dummy chunk for retrieval test
            ret.vector_store.reset_collection()
            
            dummy_chunks = [{
                "text": "Photosynthesis is the process by which plants use sunlight to synthesize nutrients.",
                "chunk_id": "photo_1",
                "source": "biology_syllabus.pdf",
                "chunk_index": 0
            }]
            embedded = ret.embedder.generate_embeddings(dummy_chunks)
            ret.vector_store.upsert_chunks(embedded)
            
            results = ret.retrieve("How do plants synthesize nutrients?")
            self.assertGreater(len(results), 0)
            self.assertEqual(results[0]["source"], "biology_syllabus.pdf")
            self.assertGreater(results[0]["relevance_score"], 0.0)
            
            ret.vector_store.reset_collection()
        self.run_test_case("02 Retriever Chroma Query", check)

    def test_03_retriever_validation(self):
        def check():
            ret = Retriever()
            with self.assertRaises(ValueError):
                ret.retrieve("")
            with self.assertRaises(ValueError):
                ret.retrieve("ab")
        self.run_test_case("03 Retriever Validation Checks", check)

    def test_04_retriever_formatting(self):
        def check():
            ret = Retriever()
            chunks = [{
                "text": "Cell theory states that all living organisms are composed of cells.",
                "source": "cell_biology.pdf",
                "chunk_index": 1,
                "relevance_score": 0.892,
                "rank": 1
            }]
            context = ret.format_context(chunks)
            self.assertIn("[SOURCE]: cell_biology.pdf", context)
            self.assertIn("Relevance: 0.892", context)
            self.assertIn("Cell theory", context)
            
            empty_context = ret.format_context([])
            self.assertEqual(empty_context, "No relevant context found.")
        self.run_test_case("04 Retriever Context Formatting", check)

    def test_05_generator_init(self):
        def check():
            gen = Generator()
            self.assertEqual(gen.model_name, settings.LLM_MODEL)
            self.assertIsNotNone(gen.model)
        self.run_test_case("05 Generator Model Init", check)

    def test_06_generator_execution(self):
        def check():
            gen = Generator()
            context = (
                "[SOURCE]: cell_biology.pdf (Relevance: 0.95)\n"
                "Mitochondria are double-membraned organelles responsible for generating adenosine triphosphate (ATP)."
            )
            res = gen.generate(
                question="What is the function of mitochondria?",
                context=context
            )
            self.assertTrue(res["generation_success"])
            self.assertIn("ATP", res["answer"])
            self.assertIn("Mitochondria", res["answer"])
            self.assertIn("This answer is based on your uploaded course material.", res["answer"])
        self.run_test_case("06 Generator Execution (RAG)", check)

    def test_07_generator_empty_context(self):
        def check():
            gen = Generator()
            res = gen.generate(
                question="Explain quantum physics?",
                context="No relevant context found."
            )
            self.assertTrue(res["generation_success"])
            self.assertIn("I could not find information about this topic in your course material", res["answer"])
        self.run_test_case("07 Generator Empty Context Fallback", check)

    def test_08_memory_storage(self):
        def check():
            mem = ConversationMemory()
            self.assertEqual(len(mem.get_history("session_123")), 0)
            
            mem.add_turn(
                session_id="session_123",
                question="Hi",
                answer="Hello there!",
                sources=["intro.pdf"],
                chunks_used=1
            )
            history = mem.get_history("session_123")
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]["question"], "Hi")
            self.assertEqual(history[0]["answer"], "Hello there!")
            self.assertEqual(history[0]["turn_number"], 1)
        self.run_test_case("08 Memory Turn Appends", check)

    def test_09_memory_formatting(self):
        def check():
            mem = ConversationMemory()
            mem.add_turn(
                session_id="session_456",
                question="Q1",
                answer="A1",
                sources=[],
                chunks_used=0
            )
            msg = mem.get_context_messages("session_456")
            self.assertEqual(len(msg), 2)
            self.assertEqual(msg[0]["role"], "user")
            self.assertEqual(msg[0]["content"], "Q1")
            self.assertEqual(msg[1]["role"], "assistant")
            self.assertEqual(msg[1]["content"], "A1")
        self.run_test_case("09 Memory Context Message Feeds", check)

    def test_10_full_rag_chain(self):
        def check():
            chain = RAGChain()
            chain.retriever.vector_store.reset_collection()
            
            dummy_chunks = [{
                "text": "Python was created by Guido van Rossum and released in 1991.",
                "chunk_id": "py_1",
                "source": "cs101.pdf",
                "chunk_index": 0
            }]
            embedded = chain.retriever.embedder.generate_embeddings(dummy_chunks)
            chain.retriever.vector_store.upsert_chunks(embedded)
            
            res = chain.chat(
                question="Who created Python and when?",
                session_id="student_1"
            )
            self.assertTrue(res["generation_success"])
            self.assertIn("Guido van Rossum", res["answer"])
            self.assertIn("1991", res["answer"])
            self.assertEqual(res["chunks_used"], 1)
            self.assertEqual(res["sources"], ["cs101.pdf"])
            self.assertGreater(res["timing"]["total_seconds"], 0.0)
            
            chain.retriever.vector_store.reset_collection()
        self.run_test_case("10 End-to-End RAG Chain Run", check)

    @classmethod
    def tearDownClass(cls):
        passed = sum(1 for r in cls.results if r[1] == "PASS")
        failed = len(cls.results) - passed
        total_time = round(time.time() - cls.start_time, 2)
        
        print("="*40)
        print(f"Results: {passed}/10 passed")
        print(f"Total time: {total_time}s")
        if passed == 10:
            print("All Week 2 tests passed successfully!")
        else:
            print(f"{failed} test(s) failed. Fix before running in production.")
        print("="*40)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(GeminiRAGTestSuite)
    unittest.TextTestRunner(verbosity=0).run(suite)
