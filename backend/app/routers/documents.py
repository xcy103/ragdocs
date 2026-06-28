import uuid

from fastapi import APIRouter

from app.db.mongo import get_db
from app.models.schemas import DocumentIn, DocumentOut
from app.services.retrieval import index_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut)
async def create_document(doc: DocumentIn) -> DocumentOut:
    document_id = str(uuid.uuid4())
    num_chunks = await index_document(document_id, doc.title, doc.content)
    await get_db().documents.insert_one(
        {"_id": document_id, "title": doc.title, "content": doc.content, "num_chunks": num_chunks}
    )
    return DocumentOut(id=document_id, title=doc.title, num_chunks=num_chunks)


@router.get("", response_model=list[DocumentOut])
async def list_documents() -> list[DocumentOut]:
    cursor = get_db().documents.find({}, {"content": 0})
    return [
        DocumentOut(id=d["_id"], title=d["title"], num_chunks=d.get("num_chunks", 0))
        async for d in cursor
    ]
