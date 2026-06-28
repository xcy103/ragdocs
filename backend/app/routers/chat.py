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
