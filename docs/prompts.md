# Phase prompts for Claude Code

Copy a prompt into Claude Code to build that phase. Each assumes `CLAUDE.md` is read first.
Work one phase at a time; commit when it runs.

## Phase 1 — Document ingestion (mostly scaffolded)

> Verify the document ingestion path end-to-end. Start MongoDB and Qdrant with
> `docker compose up -d mongo qdrant`, install backend deps, run the API, then `POST /documents`
> with a sample doc and confirm the chunks land in Qdrant and the doc lands in MongoDB.
> Add a `DELETE /documents/{id}` endpoint that removes the doc from MongoDB and its chunks from
> Qdrant (filter by `document_id` payload). Add a pytest that mocks the embedder and DB clients.

## Phase 2 — Retrieval + RAG chat (mostly scaffolded)

> Verify `POST /chat`: ingest a couple of documents, ask a question whose answer is in them,
> and confirm the answer cites the right sources. Then add streaming: a `POST /chat/stream`
> endpoint that uses `client.messages.stream(...)` and returns Server-Sent Events. Add a
> `GET /chat/{conversation_id}` endpoint that returns the stored message history from MongoDB.

## Phase 3 — Frontend (React + Redux)

> Scaffold a Vite React app in `frontend/`. Use Redux Toolkit with two slices: `documents`
> (list + upload) and `chat` (messages, send, streaming). Build two pages: a document manager
> (upload text, list docs, delete) and a chat page that streams answers and shows cited sources
> under each reply. Point the API base URL at `http://localhost:8000` via an env var. Keep
> components small; use RTK Query or async thunks for the API calls.

## Phase 4 — Dockerize

> Write `backend/Dockerfile` (python:3.11-slim, install requirements, run uvicorn) and
> `frontend/Dockerfile` (node build + nginx serve). Uncomment and finish the `backend` service in
> `docker-compose.yml`, add a `frontend` service, and wire service-to-service URLs (mongo/qdrant
> by service name). Confirm `docker compose up` brings the whole stack online.

## Phase 5 — Deploy + CI/CD

> Write a `Jenkinsfile` with stages: checkout → install → test → build images → deploy. Document
> the AWS EC2 deploy steps in `docs/deploy.md` (security group ports, docker install, pulling the
> repo, `docker compose up -d`, env/secret handling). Keep `ANTHROPIC_API_KEY` out of the image —
> inject at runtime via the EC2 environment or a secrets manager.
