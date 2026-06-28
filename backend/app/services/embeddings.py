from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache
def _model() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts into vectors using the local model.

    This is the ONLY embedding entry point. Swap the implementation here (e.g. to
    Voyage AI) without touching the rest of the app — just keep the output dimension
    in sync with the Qdrant collection (see CLAUDE.md).
    """
    vectors = _model().encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


def embedding_dim() -> int:
    return _model().get_sentence_embedding_dimension()


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into overlapping character windows. No truncation — every char is kept."""
    if size <= 0:
        return [text]
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks
