# RAG Knowledge Assistant (Free-first)

A small, production-style RAG service with a Web UI (Streamlit) and FastAPI backend. It is structured to add/switch LLM providers easily, and it supports a **no-LLM** mode that returns retrieved passages with citations.

## Features
- Retrieval-only Q&A with citations (no LLM, no paid APIs)
- LLM provider abstraction: OpenAI, Gemini, or none (future-ready)
- Local BM25 index (no embeddings)
- Simple ingest pipeline for PDF/TXT/MD

## Quickstart

1) Create a virtual environment and install deps
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

2) Configure environment
```powershell
Copy-Item .env.example .env
```
Keys are optional for now. Free mode does not call any API.

3) Ingest documents
```powershell
python scripts\ingest.py --data-dir data
```
Put your PDF/TXT/MD files under `data/` before running ingest.

4) Run the API
```powershell
uvicorn backend.app.main:app --reload
```

5) Run the app (Streamlit)
```powershell
streamlit run frontend\app.py
```

6) Run the Neon web app (Next.js + Tailwind)
```powershell
cd web
npm install
npm run dev
```
Set `NEXT_PUBLIC_API_URL` to your API endpoint if needed (default is `http://localhost:8000/ask`).

## Project structure
- `backend/` FastAPI app
- `frontend/` Streamlit UI
- `scripts/` ingestion scripts
- `storage/` local vector store

## Notes
- Free mode uses BM25 (lexical retrieval) over your chunks.
- No-LLM mode returns the top passages with citations (no generation).
- To enable LLMs later, set `ENABLE_LLM=true` and add provider code/deps.
- Mock HR tool data lives in `data/hr.json` (used for enterprise-style questions).

