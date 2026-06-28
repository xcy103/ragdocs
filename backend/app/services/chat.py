from functools import lru_cache

from openai import AsyncOpenAI

from app.config import get_settings
from app.models.schemas import Source

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the provided context. "
    "If the context does not contain the answer, say you don't know rather than guessing. "
    "Cite the document titles you used."
)


@lru_cache
def _client() -> AsyncOpenAI:
    # Reads OPENAI_API_KEY from the environment if not passed explicitly.
    return AsyncOpenAI(api_key=get_settings().openai_api_key or None)


def _build_context(sources: list[Source]) -> str:
    blocks = [f"[{i + 1}] {s.title}\n{s.chunk}" for i, s in enumerate(sources)]
    return "\n\n".join(blocks)


async def generate_answer(message: str, sources: list[Source]) -> str:
    """Generate a grounded answer from retrieved context using the LLM."""
    context = _build_context(sources) or "(no relevant documents found)"
    user_content = (
        f"Context:\n{context}\n\n"
        f"Question: {message}\n\n"
        "Answer using only the context above."
    )

    response = await _client().chat.completions.create(
        model=get_settings().llm_model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content or ""
