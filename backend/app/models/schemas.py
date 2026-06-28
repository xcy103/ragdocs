from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    """A document submitted for ingestion."""

    title: str
    content: str = Field(..., description="Raw text of the document.")


class DocumentOut(BaseModel):
    id: str
    title: str
    num_chunks: int


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class Source(BaseModel):
    document_id: str
    title: str
    chunk: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[Source]
