# RAG-based Chatbot System

Full-stack Retrieval-Augmented Generation chatbot: **React + Redux** frontend, **FastAPI**
backend, **MongoDB** for documents/history, **Qdrant** for vector retrieval, **OpenAI** for
answer generation, containerized with **Docker** and deployable to **AWS EC2** with a **Jenkins**
CI/CD pipeline.

## Stack

| Layer       | Tech                                             |
|-------------|--------------------------------------------------|
| Frontend    | React, Redux Toolkit, Vite                       |
| Backend     | FastAPI (Python 3.11+)                            |
| Documents   | MongoDB (Motor async driver)                      |
| Vectors     | Qdrant                                            |
| Embeddings  | `fastembed` (ONNX) / `BAAI/bge-small-en-v1.5` (local, 384-dim) |
| Generation  | OpenAI (`gpt-4o-mini`)                           |
| Infra       | Docker, docker-compose, AWS EC2, Jenkins         |

## Build phases

The project is built in vertical slices, each independently demoable. Drive each phase with
Claude Code using the prompt in [`docs/prompts.md`](docs/prompts.md).

- [x] **Phase 0 — Scaffold**: repo structure, `CLAUDE.md`, docker-compose, backend skeleton.
- [x] **Phase 1 — Document ingestion**: `POST /documents` → chunk → embed → store in Qdrant + MongoDB. `GET /documents`, `DELETE /documents/{id}`.
- [x] **Phase 2 — Retrieval + RAG chat**: `POST /chat` → embed query → Qdrant top-k → OpenAI → answer with cited sources. `GET /chat/{conversation_id}` history. (Streaming output still TODO.)
- [ ] **Phase 3 — Frontend** *(in progress)*: React + Redux. Documents page + chat page wired to the APIs.
- [x] **Phase 4 — Dockerize** *(backend)*: backend `Dockerfile` + `compose.prod.yml`. Frontend image still TODO.
- [x] **Phase 5 — Deploy + CI/CD**: backend live on AWS EC2; Jenkins pipeline (build → push ECR → SSH deploy). See [`docs/deploy.md`](docs/deploy.md).

## Future work / TODO

- **Offline corpus ingestion script** (`scripts/ingest.py`): turn found materials (mostly PDFs,
  some text, some scanned/image) into documents and inject them via the `POST /documents` API
  (not by writing to Qdrant/Mongo directly — those aren't publicly exposed). Plan: extract text
  with `pdfplumber`; for scanned/image PDFs (esp. math with formulas), render pages and transcribe
  with a vision model (GPT-4o) into clean text/LaTeX. Decide granularity (one doc per PDF/page vs.
  per problem). The chatbot's domain/corpus is still undecided — keep it generic for now.
- **Multilingual embeddings**: if the corpus is Chinese (e.g. exam problems), switch the embedder
  from `BAAI/bge-small-en-v1.5` to a multilingual model (e.g. `intfloat/multilingual-e5-small`,
  also 384-dim) for much better retrieval. Currently English-only.
- **Streaming chat** (`POST /chat/stream`, SSE) and a small test suite.

## Quick start (local)

```bash
cp .env.example .env          # then fill in OPENAI_API_KEY
docker compose up -d mongo qdrant

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000/docs
```

## Layout

```
backend/app/
  config.py            # env-driven settings
  main.py              # FastAPI app + router wiring
  db/                  # mongo + qdrant clients
  services/            # embeddings, retrieval, chat (business logic)
  routers/             # documents, chat (HTTP layer)
  models/schemas.py    # pydantic request/response models
frontend/              # React + Redux (Phase 3)
```
