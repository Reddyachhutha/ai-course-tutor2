import os
import sys
import time
import shutil
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.config import settings
from backend.ingestion.pdf_parser import extract_text_from_pdf
from backend.ingestion.chunker import chunk_text
from backend.ingestion.embedder import Embedder
from backend.database.vector_store import VectorStore

class ImprovedTestSuite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.start_time = time.time()
        cls.results = []
        print("="*30)
        print("Week 1 Improved Test Suite")
        print("="*30)

    def run_test_case(self, name, func):
        t_start = time.time()
        try:
            func()
            duration = round(time.time() - t_start, 2)
            self.results.append((name, "PASS", duration))
            print(f"{name:<30} PASS  {duration}s")
        except Exception as e:
            duration = round(time.time() - t_start, 2)
            self.results.append((name, "FAIL", duration))
            print(f"{name:<30} FAIL  {duration}s - {str(e)}")

    def test_01_config_loads(self):
        def check():
            self.assertIsNotNone(settings.GOOGLE_API_KEY)
            self.assertNotEqual(settings.GOOGLE_API_KEY, "")
            self.assertTrue(hasattr(settings, "MAX_CHUNK_SIZE"))
        self.run_test_case("TEST 01 Config Loads", check)

    def test_02_directories_exist(self):
        def check():
            self.assertTrue(settings.UPLOAD_DIR.exists())
            self.assertTrue(settings.CHROMA_PERSIST_DIR.exists())
        self.run_test_case("TEST 02 Directories Exist", check)

    def test_03_pdf_parser_missing_file(self):
        def check():
            res = extract_text_from_pdf("nonexistent_file_12345.pdf")
            self.assertIsNone(res)
        self.run_test_case("TEST 03 Parser Missing File", check)

    def test_04_pdf_parser_wrong_extension(self):
        def check():
            temp_file = Path("test.txt")
            temp_file.write_text("dummy content")
            res = extract_text_from_pdf(str(temp_file))
            self.assertIsNone(res)
            os.remove(temp_file)
        self.run_test_case("TEST 04 Parser Wrong Ext", check)

    def test_05_chunker_empty_input(self):
        def check():
            self.assertEqual(chunk_text("", "test.pdf"), [])
            self.assertEqual(chunk_text(None, "test.pdf"), [])
        self.run_test_case("TEST 05 Chunker Empty Input", check)

    def test_06_chunker_short_text(self):
        def check():
            res = chunk_text("Short text", "test.pdf")
            self.assertEqual(len(res), 1)
            self.assertIn("chunk_id", res[0])
            self.assertEqual(res[0]["source"], "test.pdf")
        self.run_test_case("TEST 06 Chunker Short Text", check)

    def test_07_chunker_quality(self):
        def check():
            text = "Sample content " * 100 # Approx 1500 chars
            res = chunk_text(text, "quality_test.pdf")
            for chunk in res:
                self.assertIn("chunk_id", chunk)
                self.assertEqual(chunk["source"], "quality_test.pdf")
                self.assertLessEqual(chunk["char_count"], 600)
                self.assertGreaterEqual(chunk["char_count"], 50)
        self.run_test_case("TEST 07 Chunker Quality", check)

    def test_08_embedder_dimensions(self):
        def check():
            emb = Embedder()
            # We mock the generate_embeddings for a quick check or use real one
            # all-MiniLM-L6-v2 is 384
            res = emb.generate_embeddings([{"text": "test question", "chunk_id": "1"}])
            self.assertEqual(len(res[0]["embedding"]), 384)
            self.assertIsInstance(res[0]["embedding"][0], float)
        self.run_test_case("TEST 08 Embedder Dims", check)

    def test_09_embedder_empty_input(self):
        def check():
            emb = Embedder()
            self.assertEqual(emb.generate_embeddings([]), [])
        self.run_test_case("TEST 09 Embedder Empty", check)

    def test_10_vector_store_full_cycle(self):
        def check():
            vs = VectorStore()
            vs.reset_collection()
            emb = Embedder()
            
            # Create 5 chunks
            texts = [f"This is test sentence {i} for vector store validation." for i in range(5)]
            chunks = []
            for i, t in enumerate(texts):
                chunks.append({
                    "text": t,
                    "chunk_id": f"test_chunk_{i}",
                    "source": "test_cycle.pdf",
                    "chunk_index": i
                })
            
            # Embed
            chunks_with_emb = emb.generate_embeddings(chunks)
            
            # Upsert
            vs.upsert_chunks(chunks_with_emb)
            self.assertEqual(vs.get_count(), 5)
            
            # Query
            query_emb = chunks_with_emb[0]["embedding"]
            results = vs.query(query_emb, n_results=3)
            self.assertGreater(len(results), 0)
            self.assertIn("relevance_score", results[0])
            
            # Cleanup
            vs.reset_collection()
            
        self.run_test_case("TEST 10 Vector Store Cycle", check)

    @classmethod
    def tearDownClass(cls):
        passed = sum(1 for r in cls.results if r[1] == "PASS")
        failed = len(cls.results) - passed
        total_time = round(time.time() - cls.start_time, 2)
        
        print("="*30)
        print(f"Results: {passed}/10 passed")
        print(f"Total time: {total_time}s")
        if passed == 10:
            print("All tests passed! Week 1 is rock solid.")
        else:
            print(f"{failed} test(s) failed. Fix before Week 2.")
        print("="*30)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ImprovedTestSuite)
    unittest.TextTestRunner(verbosity=0).run(suite)
