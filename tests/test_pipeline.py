import os
import sys
from pathlib import Path

# Add project root to path so we can import backend
sys.path.append(str(Path(__file__).parent.parent))

from backend.ingestion.pipeline import IngestionPipeline
from backend.database.vector_store import VectorStore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_e2e_test():
    """
    Simulates a manual ingestion flow for testing.
    """
    print("🚀 Starting E2E Pipeline Test...")
    
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY") == "your_openrouter_api_key_here":
        print("❌ ERROR: OPENROUTER_API_KEY not set in .env. Test will fail.")
        return

    # 1. Initialize
    pipeline = IngestionPipeline()
    store = VectorStore()
    
    # 2. Get a sample PDF path (using current script as a dummy if no PDF provided)
    # Note: In a real test, you'd provide a small sample.pdf
    sample_pdf = "sample.pdf"
    if not os.path.exists(sample_pdf):
        print(f"⚠️ Sample PDF '{sample_pdf}' not found. Please place a small PDF in the root to test.")
        return

    # 3. Process
    try:
        print(f"Processing '{sample_pdf}'...")
        result = pipeline.process_pdf(sample_pdf)
        print(f"✅ Success: {result}")
        
        # 4. Verify in Store
        stats = store.get_stats()
        print(f"📊 Vector Store Stats: {stats}")
        
        if result["chunks_stored"] > 0:
            print("✅ Vectors stored correctly.")
        else:
            print("❌ No chunks were stored.")
            
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")

if __name__ == "__main__":
    run_e2e_test()
