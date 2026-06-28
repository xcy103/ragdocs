import uuid

from qdrant_client.models import PointStruct

from app.config import get_settings
from app.db.qdrant import ensure_collection, get_qdrant
from app.models.schemas import Source
from app.services.embeddings import chunk_text, embed_query, embed_texts, embedding_dim


async def index_document(document_id: str, title: str, content: str) -> int:
    """Chunk, embed, and store a document's chunks in Qdrant. Returns chunk count."""
    settings = get_settings()
    await ensure_collection(embedding_dim())

    chunks = chunk_text(content, settings.chunk_size, settings.chunk_overlap)
    vectors = embed_texts(chunks)
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"document_id": document_id, "title": title, "chunk": chunk},
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    await get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points)
    return len(chunks)


async def retrieve(query: str) -> list[Source]:
    """Return the top-k most relevant chunks for a query."""
    settings = get_settings()
    hits = await get_qdrant().search(
        collection_name=settings.qdrant_collection,
        query_vector=embed_query(query),
        limit=settings.top_k,
    )
    return [
        Source(
            document_id=h.payload["document_id"],
            title=h.payload["title"],
            chunk=h.payload["chunk"],
            score=h.score,
        )
        for h in hits
    ]
