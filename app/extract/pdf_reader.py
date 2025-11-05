

import pdfplumber
from PyPDF2 import PdfReader
from io import BytesIO

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    # primary path
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if text.strip():
                return text
    except Exception:
        pass
    # fallback
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""
