# PILOT-AI v0.1-free: Software Documentation

## Overview
PILOT-AI is a zero-cost, self-contained AI-powered UK planning decision-support assistant. It is designed as a focus group prototype to demonstrate how Retrieval-Augmented Generation (RAG) can assist planning officers without incurring cloud costs or requiring paid API subscriptions.

## Architecture

The system is strictly divided into a Python FastAPI backend and a Next.js 14 frontend.

### 1. Backend (`/backend`)
The backend handles document ingestion, local semantic search, and communication with the LLM (Large Language Model).

*   **Framework:** FastAPI (Python 3.10+)
*   **Database (Relational):** SQLite + SQLAlchemy. Stores document metadata and a history of analyzed applications.
*   **Vector Database:** ChromaDB (Local). Stores document embeddings for semantic search.
*   **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`). Runs locally on the CPU to convert policy text into searchable mathematical vectors.
*   **LLM Integration:** 
    *   **Primary:** Groq API (`llama-3.3-70b-versatile`). Used for extremely fast, high-quality reasoning.
    *   **Fallback:** Google Gemini API (`gemini-1.5-flash`). Automatically used if the Groq API rate limits are hit.
*   **Document Processing:** Uses `pdfplumber` (with `PyMuPDF` fallback) to extract text from PDFs, and `tiktoken` for intelligent, sentence-boundary-aware hierarchical chunking.

### 2. Frontend (`/frontend`)
The frontend is the user interface designed for planning officers.

*   **Framework:** Next.js 14 (App Router) + React
*   **Styling:** Tailwind CSS (Custom brand palette: Navy, Teal, Sky, Ice)
*   **Key Components:**
    *   `ApplicationForm.tsx`: Captures planning application details and constraints.
    *   `AnalysisResult.tsx`: Renders the AI's compliance assessment, key issues, and recommendations.
    *   `CitationPanel.tsx`: A slide-out drawer that displays the exact, verbatim text retrieved from the local Vector DB to prove the AI's claims.

## Data Flow (The RAG Pipeline)

When a user submits a planning application via the UI, the following occurs:

1.  **Ingestion (Pre-requisite):** PDFs are uploaded, broken into ~500-token chunks, embedded using `all-MiniLM-L6-v2`, and saved in ChromaDB.
2.  **Query Generation:** The application details are sent to the backend.
3.  **Semantic Search:** The backend queries ChromaDB to find the 5 most semantically relevant policy chunks based on the application description and site constraints.
4.  **Prompt Assembly:** The backend creates a strict system prompt containing the retrieved chunks, the application details, and strict instructions to *only* use the provided context.
5.  **LLM Inference:** The prompt is sent to Groq (Llama 3.3 70B). The AI analyzes the application against the policies.
6.  **Verification:** The backend runs a "Phantom Citation Check" to ensure every `citation_id` returned by the LLM actually matches a chunk provided in the prompt.
7.  **Response:** The structured JSON response is sent to the frontend and rendered for the user.

## System Constraints & Security
*   **Zero Cloud Footprint:** No AWS, GCP, or Azure services are used for hosting or databases. Everything runs on localhost.
*   **Free-Tier LLMs:** Relies on generous free tiers provided by Groq and Google AI Studio.
*   **Data Privacy:** Uploaded PDFs and Application inputs never leave the local machine, *except* for the specific text chunks sent to the LLM during the analysis phase.

## File Structure Reference
```text
pilot-ai-free/
├── .env                  # API keys and config (DO NOT COMMIT)
├── backend/
│   ├── main.py           # FastAPI application entry point
│   ├── seed.py           # Auto-generates PDFs and seeds the database
│   ├── config.py         # Environment variable loading
│   ├── api/routes/       # API endpoints (health, applications, documents)
│   ├── models/           # SQLAlchemy schemas and Pydantic types
│   ├── services/         # Core business logic (RAG, LLM client, Ingestion)
│   ├── utils/            # Helpers (PDF extraction, hierarchical chunking)
│   └── data/             # Local SQLite DB and ChromaDB storage
└── frontend/
    ├── src/app/          # Next.js pages (dashboard, analyse, documents)
    ├── src/components/   # Reusable React UI components
    ├── src/lib/          # API client and TypeScript interfaces
    └── tailwind.config.ts# CSS styling configuration
```
