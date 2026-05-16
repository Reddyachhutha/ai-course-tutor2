from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import os
import hashlib
import time
import re
import logging

logger = logging.getLogger(__name__)

def chunk_text(
    text: str, 
    source_name: str, 
    chunk_size: int = 500, 
    chunk_overlap: int = 50,
    min_chunk_size: int = 50
) -> List[Dict[str, Any]]:
    """
    Improved text chunker with quality filters, duplicate detection, and unique IDs.
    """
    if not text or not text.strip():
        logger.warning("Empty text received, no chunks created")
        return []

    text = text.strip()
    total_input_chars = len(text)

    if len(text) < chunk_size:
        return [{
            "text": text,
            "chunk_id": f"{os.path.basename(source_name)}_chunk_0_{int(time.time())}",
            "source": os.path.basename(source_name),
            "chunk_index": 0,
            "char_count": len(text),
            "word_count": len(text.split()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    raw_chunks = splitter.split_text(text)
    
    final_chunks = []
    seen_hashes = set()
    duplicates_removed = 0
    filtered_count = 0
    timestamp_str = str(int(time.time()))

    for i, chunk_text_content in enumerate(raw_chunks):
        chunk_text_content = chunk_text_content.strip()
        
        if len(chunk_text_content) < min_chunk_size:
            filtered_count += 1
            continue
            
        if re.match(r'^[\d\s\W]+$', chunk_text_content):
            filtered_count += 1
            continue

        chunk_hash = hashlib.md5(chunk_text_content.encode()).hexdigest()
        if chunk_hash in seen_hashes:
            duplicates_removed += 1
            continue
        
        seen_hashes.add(chunk_hash)
        
        word_count = len(chunk_text_content.split())
        chunk_id = f"{os.path.basename(source_name)}_chunk_{i}_{timestamp_str}"
        
        final_chunks.append({
            "text": chunk_text_content,
            "chunk_id": chunk_id,
            "source": os.path.basename(source_name),
            "chunk_index": i,
            "char_count": len(chunk_text_content),
            "word_count": word_count,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        })

    print("Chunking complete:")
    print(f"   Input chars: {total_input_chars}")
    print(f"   Chunks created: {len(raw_chunks)}")
    print(f"   Chunks filtered: {filtered_count}")
    print(f"   Duplicates removed: {duplicates_removed}")
    print(f"   Final chunks: {len(final_chunks)}")
        
    return final_chunks
