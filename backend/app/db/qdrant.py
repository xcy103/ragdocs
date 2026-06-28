from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import get_settings

_client: AsyncQdrantClient | None = None


def get_qdrant() -> AsyncQdrantClient:
    """Return the async Qdrant client, creating it lazily."""
    global _client
    if _client is None:
        _client = AsyncQdrantClient(url=get_settings().qdrant_url)
    return _client


async def ensure_collection(dim: int) -> None:
    """Create the document-chunk collection if it does not exist.

    `dim` must match the embedding model's output dimension (see CLAUDE.md).
    """
    settings = get_settings()
    client = get_qdrant()
    existing = {c.name for c in (await client.get_collections()).collections}
    if settings.qdrant_collection not in existing:
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


async def close_qdrant() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
