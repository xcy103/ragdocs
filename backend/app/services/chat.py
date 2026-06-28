from functools import lru_cache

import anthropic

from app.config import get_settings
from app.models.schemas import Source

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the provided context. "
    "If the context does not contain the answer, say you don't know rather than guessing. "
    "Cite the document titles you used."
)


@lru_cache
def _client() -> anthropic.AsyncAnthropic:
    # Reads ANTHROPIC_API_KEY from the environment.
    return anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key or None)


def _build_context(sources: list[Source]) -> str:
    blocks = [f"[{i + 1}] {s.title}\n{s.chunk}" for i, s in enumerate(sources)]
    return "\n\n".join(blocks)


async def generate_answer(message: str, sources: list[Source]) -> str:
    """Generate a grounded answer from retrieved context using Claude."""
    context = _build_context(sources) or "(no relevant documents found)"
    user_content = (
        f"Context:\n{context}\n\n"
        f"Question: {message}\n\n"
        "Answer using only the context above."
    )

    response = await _client().messages.create(
        model=get_settings().claude_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": user_content}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
