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
- **Embeddings**: local `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim). No external key.
- **LLM**: Anthropic Claude (`claude-opus-4-8`) for answer generation. Requires `ANTHROPIC_API_KEY`.
- **Infra**: Docker / docker-compose; deploy target is AWS EC2; CI/CD via Jenkins.

## Architecture (request flow)

```
Upload:  client → POST /documents → chunk → embed (local) → Qdrant + MongoDB
Chat:    client → POST /chat → embed query → Qdrant top-k → build context
                → Claude (claude-opus-4-8) → answer (+ cited sources) → MongoDB
```

The single boundary that matters: **embeddings are produced locally; only the final
generation step calls Claude.** Keep it that way unless we deliberately switch embedding providers.

## Hard rules (do not violate)

- **Claude calls**: use the official `anthropic` Python SDK only. Never raw `requests`/`httpx`
  to the Anthropic API, never an OpenAI-compatible shim.
- **Model**: default `claude-opus-4-8`. Adaptive thinking only — `thinking={"type": "adaptive"}`.
  Do **not** pass `budget_tokens`, `temperature`, `top_p`, or `top_k` (they 400 on this model).
- **Secrets**: never hardcode `ANTHROPIC_API_KEY` or any secret. Read from env / `.env`
  (gitignored). `.env.example` documents the names with placeholder values.
- **Vector dimension**: the Qdrant collection dim MUST match the embedding model (384 for
  `all-MiniLM-L6-v2`). Changing the embedding model means recreating the collection.
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

See `.env.example`. Required: `ANTHROPIC_API_KEY`, `MONGODB_URI`, `QDRANT_URL`.

## Definition of done for a change

- New endpoints have request/response Pydantic schemas.
- Anything touching retrieval keeps the Qdrant dim in sync with the embedding model.
- No secrets committed; `.env` stays gitignored.
- If you add a dependency, add it to `requirements.txt` (backend) or `package.json` (frontend).
