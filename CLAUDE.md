# RAG-based Chatbot System — Project Guide

This file orients Claude Code (and any contributor) on **how to work in this repo**.
Read it before making changes.

## What this is

A full-stack Retrieval-Augmented Generation chatbot:

- **Frontend**: React + Redux Toolkit + Vite. Pages talk to the backend chat & document APIs.
- **Backend**: FastAPI (Python). RESTful APIs for document upload/storage, vector retrieval,
  and retrieval-augmented answer generation.
- **MongoDB**: stores raw documents, chunks, and chat history (metadata / source of truth).
- **Qdrant**: vector database for semantic retrieval over document chunks.
- **Embeddings**: local `fastembed` (ONNX, `BAAI/bge-small-en-v1.5`, 384-dim). No PyTorch, no external key.
- **LLM**: OpenAI (`gpt-4o-mini` by default) for answer generation. Requires `OPENAI_API_KEY`.
- **Infra**: Docker / docker-compose; deploy target is AWS EC2; CI/CD via Jenkins.

## Architecture (request flow)

```
Upload:  client → POST /documents → chunk → embed (local) → Qdrant + MongoDB
Chat:    client → POST /chat → embed query → Qdrant top-k → build context
                → OpenAI (gpt-4o-mini) → answer (+ cited sources) → MongoDB
```

The single boundary that matters: **embeddings are produced locally; only the final
generation step calls the LLM.** Keep it that way unless we deliberately switch embedding providers.

## Hard rules (do not violate)

- **LLM calls**: use the official `openai` Python SDK (`AsyncOpenAI`). The model is configurable
  via `LLM_MODEL` (default `gpt-4o-mini`). All generation goes through `app/services/chat.py`.
- **Secrets**: never hardcode `OPENAI_API_KEY` or any secret — and never put a real key in
  `.env.example` (it is committed). Real keys go in `.env` (gitignored) locally, or in the
  server's `.env`. `.env.example` only holds placeholder values.
- **Vector dimension**: the Qdrant collection dim MUST match the embedding model (384 for
  `bge-small-en-v1.5`). Changing the embedding model means recreating the collection.
- **No silent truncation**: if a document or context is too large, chunk it — don't cut it off.
- **Layering**: routers (HTTP) → services (logic) → db (drivers). Routers never touch DB drivers
  directly; services never parse `Request` objects.

## Conventions

- **Language**: all code, comments, identifiers, and commit messages are written in **English**.
  (Status reports to the project owner are delivered in Chinese, but nothing in the repo is.)
- Backend code lives under `backend/app/`. Pydantic models in `app/models/schemas.py`.
- Config via `app/config.py` (pydantic-settings); read everything from env.
- Type-hint all functions. Keep services pure and testable (pass clients in, don't import globals).
- Async FastAPI handlers; Motor (async MongoDB) and the async Qdrant client.
- Frontend lives under `frontend/`. Redux Toolkit slices per domain (`chat`, `documents`).

## Commands

```bash
# Bring up MongoDB + Qdrant
docker compose up -d mongo qdrant

# Backend (from backend/)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (from frontend/, once scaffolded)
npm install && npm run dev
```

## Env vars

See `.env.example`. Required: `OPENAI_API_KEY`, `MONGODB_URI`, `QDRANT_URL`.

## Definition of done for a change

- New endpoints have request/response Pydantic schemas.
- Anything touching retrieval keeps the Qdrant dim in sync with the embedding model.
- No secrets committed; `.env` stays gitignored.
- If you add a dependency, add it to `requirements.txt` (backend) or `package.json` (frontend).
