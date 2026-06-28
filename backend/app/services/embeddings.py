from functools import lru_cache

from fastembed import TextEmbedding

from app.config import get_settings


@lru_cache
def _model() -> TextEmbedding:
    # fastembed runs ONNX locally — no PyTorch/CUDA. Model is downloaded and cached
    # on first use. bge-small-en-v1.5 produces normalized 384-dim vectors.
    return TextEmbedding(model_name=get_settings().embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts into vectors using the local model.

    This is the ONLY embedding entry point. Swap the implementation here (e.g. to
    Voyage AI) without touching the rest of the app — just keep the output dimension
    in sync with the Qdrant collection (see CLAUDE.md).
    """
    return [vector.tolist() for vector in _model().embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


@lru_cache
def embedding_dim() -> int:
    return len(embed_query("dimension probe"))


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
