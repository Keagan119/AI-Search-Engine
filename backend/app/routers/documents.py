from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, DocumentChunk
from ..services.chunker import chunk_text
from ..services.embedder import embed_texts
from ..services.extractor import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file.content_type}"
        )

    file_bytes = await file.read()
    text = extract_text(file_bytes, file.content_type)
    chunks = chunk_text(text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No text content could be extracted from the file.",
        )

    embeddings = embed_texts(chunks)

    doc = Document(filename=file.filename, content_type=file.content_type)
    db.add(doc)
    db.flush()

    for content, embedding in zip(chunks, embeddings):
        db.add(DocumentChunk(document_id=doc.id, content=content, embedding=embedding))

    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "chunks_created": len(chunks),
    }
