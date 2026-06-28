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
- [ ] **Phase 1 — Document ingestion**: `POST /documents` → chunk → embed → store in Qdrant + MongoDB. `GET /documents` to list.
- [ ] **Phase 2 — Retrieval + RAG chat**: `POST /chat` → embed query → Qdrant top-k → OpenAI → answer with cited sources. Persist chat history in MongoDB.
- [ ] **Phase 3 — Frontend**: React + Redux. Document upload page + chat page wired to the APIs. Streaming responses.
- [ ] **Phase 4 — Dockerize**: multi-container compose (frontend, backend, mongo, qdrant); Dockerfiles for FE/BE.
- [ ] **Phase 5 — Deploy + CI/CD**: AWS EC2 deploy; Jenkins pipeline for build → test → deploy.

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
