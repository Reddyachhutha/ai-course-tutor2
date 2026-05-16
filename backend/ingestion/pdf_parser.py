import PyPDF2
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import re
import os

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Improved PDF parser with extensive error handling and text cleaning.
    """
    path = Path(file_path)
    filename = path.name

    # EDGE CASE 1: File does not exist
    if not path.exists():
        logger.error(f"❌ File not found: {file_path}")
        return None

    # EDGE CASE 2: File is not a PDF
    if path.suffix.lower() != ".pdf":
        logger.error(f"❌ Not a PDF file: {filename}")
        return None

    # EDGE CASE 6: Empty PDF file (check size)
    file_size_mb = os.path.getsize(path) / (1024 * 1024)
    if file_size_mb == 0:
        logger.error(f"❌ PDF has no content (0 bytes): {filename}")
        return None

    full_text_list = []
    pages_with_text = 0
    pages_skipped = 0
    total_pages = 0

    try:
        with open(path, "rb") as file:
            try:
                # EDGE CASE 3: Corrupted PDF
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
            except PyPDF2.errors.PdfReadError as e:
                logger.error(f"❌ Corrupted PDF: {filename} - {str(e)}")
                return None

            # EDGE CASE 6: PDF has no pages
            if total_pages == 0:
                logger.error(f"❌ PDF has no pages: {filename}")
                return None

            # EDGE CASE 4: Password protected PDF
            if reader.is_encrypted:
                try:
                    # Try with empty string
                    reader.decrypt("")
                except Exception:
                    logger.error(f"❌ Password protected PDF cannot be parsed: {filename}")
                    return None

            for i in range(total_pages):
                try:
                    page = reader.pages[i]
                    text = page.extract_text()
                    
                    if not text or not text.strip():
                        pages_skipped += 1
                        continue

                    # TEXT CLEANING
                    # Remove null bytes
                    text = text.replace('\x00', '')
                    # Remove non-printable characters
                    text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)
                    # Remove excessive whitespace (3+ newlines to 2)
                    text = re.sub(r'\n{3,}', '\n\n', text)
                    # Strip per page
                    text = text.strip()

                    if text:
                        full_text_list.append(text)
                        pages_with_text += 1
                    else:
                        pages_skipped += 1
                except Exception as page_err:
                    logger.warning(f"⚠️ Error on page {i+1}: {page_err}")
                    pages_skipped += 1

    except Exception as e:
        logger.error(f"❌ Unexpected error parsing {filename}: {str(e)}")
        return None

    full_text = "\n\n".join(full_text_list)
    char_count = len(full_text)
    word_count = len(full_text.split())

    # EDGE CASE 5: Scanned PDF detection
    is_scanned = False
    warning = None
    if total_pages > 0 and char_count < 100 * total_pages:
        is_scanned = True
        warning = "PDF appears to be scanned/image-based. Text extraction may be incomplete."
        logger.warning(f"⚠️ Warning: Scanned PDF detected - {filename}")

    return {
        "text": full_text,
        "pages": total_pages,
        "pages_with_text": pages_with_text,
        "pages_skipped": pages_skipped,
        "filename": filename,
        "file_path": str(path.absolute()),
        "file_size_mb": round(file_size_mb, 2),
        "char_count": char_count,
        "word_count": word_count,
        "scanned_pdf": is_scanned,
        "warning": warning
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = extract_text_from_pdf(sys.argv[1])
        if res:
            print(f"✅ Extracted {res['char_count']} chars from {res['pages']} pages.")
        else:
            print("❌ Parsing failed.")
