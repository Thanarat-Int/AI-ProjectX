# Implementation Plan - FinSight: Autonomous Financial Analyst Agent

## Goal Description
To simulate a "Production Grade" AI Engineering project that aligns with the SCBX "AI Engineer" Job Description.
The project **"FinSight"** will be an automated system that analyzes financial assets (Stocks/Crypto) using traditional ML for quantitative analysis and GenAI for qualitative reasoning.

**Project Philosophy: API-First & Cloud Native**
To answer the need for **Future UX/UI Collaboration** and **Real-World Deployment**, this project is designed with a **Decoupled Architecture**:
1.  **The Brain (Backend API):** A FastAPI server that handles all Data, ML, and AI logic. It exposes clean JSON endpoints.
2.  **The Face (Frontend):** A Streamlit dashboard that consumes the API. *Note: In the future, a UX/UI team can build a React/Vue app that connects to this SAME API without changing a single line of backend code.*
3.  **The Container (Deployment):** Dockerized application. This ensures it runs on any server (Cloud Run, AWS EC2, On-Premise) exactly as it does on your local machine.

## User Review Required
> [!IMPORTANT]
> **Tech Stack Selection:** We will use **strictly free tiers**.
> - **LLM:** Gemini 1.5 Flash (Free API) via Google AI Studio.
> - **Backend:** FastAPI (Python) - High performance, easy to document (Swagger UI).
> - **Frontend:** Streamlit - For our rapid prototyping.
> - **Containerization:** Docker - For "Write Once, Run Anywhere".
> - **Data:** Yahoo Finance (`yfinance`).

## Proposed Changes

### Core System Architecture

#### [Backend API - `src/api/`]
*   **Framework:** FastAPI.
*   **Endpoints:**
    *   `GET /health`: Health check for load balancers.
    *   `GET /market-data/{ticker}`: Returns OHLCV data.
    *   `POST /analyze`: Payload `{ticker: "AAPL"}` -> Returns `{signal: "BUY", reasoning: "..."}`.
*   **Logic:** Orchestrates the pipeline (Data -> Feature Eng -> ML Model -> GenAI -> JSON Response).

#### [Frontend - `src/frontend/`]
*   **Framework:** Streamlit.
*   **Behavior:** It does NOT run models directly. It sends HTTP requests to `http://backend:8000` and renders the JSON response. This mimics a real production pattern.

#### [Ops & Infrastructure]
*   **Docker:** 
    *   `Dockerfile.backend`: Builds the API.
    *   `Dockerfile.frontend`: Builds the UI.
    *   `docker-compose.yml`: Spins up the entire stack locally.

### Files to Create

#### [Structure]
#### [NEW] [requirements.txt](file:///C:/Users/THANARAT/.gemini/antigravity/brain/aaec8635-4ac5-4a48-9a58-6fd6db4aa74b/requirements.txt)
- Dependencies: `fastapi`, `uvicorn`, `httpx`, `yfinance`, `pandas`, `scikit-learn`, `google-generativeai`, `streamlit`, `ta`.

#### [NEW] [src/api/main.py](file:///C:/Users/THANARAT/.gemini/antigravity/brain/aaec8635-4ac5-4a48-9a58-6fd6db4aa74b/src/api/main.py)
- The FastAPI application entry point.

#### [NEW] [src/core/](file:///C:/Users/THANARAT/.gemini/antigravity/brain/aaec8635-4ac5-4a48-9a58-6fd6db4aa74b/src/core/)
- `data.py`: Fetcher logic.
- `analysis.py`: ML and GenAI logic integration.

#### [NEW] [src/frontend/dashboard.py](file:///C:/Users/THANARAT/.gemini/antigravity/brain/aaec8635-4ac5-4a48-9a58-6fd6db4aa74b/src/frontend/dashboard.py)
- Streamlit app acting as the API client.

#### [NEW] [docker-compose.yml](file:///C:/Users/THANARAT/.gemini/antigravity/brain/aaec8635-4ac5-4a48-9a58-6fd6db4aa74b/docker-compose.yml)
- Orchestraion file.

## Verification Plan

### Automated Tests
*   **API Tests:** Use `pytest` to hit internal logic.

### Manual Deployment Verification
1.  Run `docker-compose up --build`.
2.  Open `http://localhost:8000/docs` to test the API directly (Backend verification).
3.  Open `http://localhost:8501` to use the App (Frontend verification).
