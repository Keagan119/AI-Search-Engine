import io

import pypdf
from docx import Document as DocxDocument

CONTENT_TYPE_PDF = "application/pdf"
CONTENT_TYPE_TXT = "text/plain"
CONTENT_TYPE_DOCX = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)


def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type == CONTENT_TYPE_PDF:
        return _extract_pdf(file_bytes)
    if content_type == CONTENT_TYPE_TXT:
        return file_bytes.decode("utf-8", errors="replace")
    if content_type == CONTENT_TYPE_DOCX:
        return _extract_docx(file_bytes)
    raise ValueError(f"Unsupported content type: {content_type}")


def _extract_pdf(file_bytes: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(file_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)
