import uuid
from datetime import datetime, timezone

from fastapi import APIRouter

from app.db.mongo import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat import generate_answer
from app.services.retrieval import retrieve

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    conversation_id = req.conversation_id or str(uuid.uuid4())
    sources = await retrieve(req.message)
    answer = await generate_answer(req.message, sources)

    await get_db().messages.insert_one(
        {
            "conversation_id": conversation_id,
            "message": req.message,
            "answer": answer,
            "sources": [s.model_dump() for s in sources],
            "created_at": datetime.now(timezone.utc),
        }
    )
    return ChatResponse(conversation_id=conversation_id, answer=answer, sources=sources)


@router.get("/{conversation_id}")
async def get_history(conversation_id: str) -> list[dict]:
    """Return the stored turns of a conversation, oldest first."""
    cursor = (
        get_db()
        .messages.find({"conversation_id": conversation_id}, {"_id": 0})
        .sort("created_at", 1)
    )
    return [doc async for doc in cursor]
