from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Document, DocumentChunk
from ..services.embedder import embed_text

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str


@router.post("")
def search(request: SearchRequest, db: Session = Depends(get_db)):
    query_vec = embed_text(request.query)

    stmt = (
        select(
            DocumentChunk.id,
            DocumentChunk.content,
            Document.filename,
            DocumentChunk.embedding.cosine_distance(query_vec).label("distance"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_vec))
        .limit(5)
    )

    rows = db.execute(stmt).all()

    return {
        "query": request.query,
        "results": [
            {
                "chunk_id": row.id,
                "content": row.content,
                "filename": row.filename,
                "similarity_score": round(1 - row.distance, 4),
            }
            for row in rows
        ],
    }
