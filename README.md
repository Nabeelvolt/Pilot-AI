# PILOT-AI Demo v0.1-free
## AI-Powered Planning Decision Support — Zero Cost Edition

This prototype runs entirely free. No credit card. No cloud account.
No Azure. No OpenAI. No subscriptions.

## What powers it
- **LLM:** Groq API (Llama 3.3 70B) — free tier, no credit card needed
- **Fallback LLM:** Google Gemini 1.5 Flash — free tier, no credit card needed  
- **Embeddings:** sentence-transformers all-MiniLM-L6-v2 — runs on your CPU
- **Vector DB:** ChromaDB — runs locally on disk
- **Database:** SQLite — single file, zero config

## Prerequisites
- Python 3.11+
- Node.js 18+
- Two free API keys (both take under 2 minutes, no payment needed):
  - Groq: https://console.groq.com (free, no credit card)
  - Gemini: https://aistudio.google.com (free, no credit card)

## Setup

### 1. Get your free API keys
- Groq: go to console.groq.com, sign up, copy your API key
- Gemini: go to aistudio.google.com, sign up, click "Get API Key", copy it

### 2. Configure
cp .env.example .env
# Edit .env: paste your GROQ_API_KEY and GEMINI_API_KEY

### 3. Start backend (first terminal)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# First run auto-generates sample planning documents and indexes them
# This takes 2-4 minutes on first run (downloads embedding model ~90MB)
# You will see: "=== Seeding complete. System ready. ==="

### 4. Start frontend (second terminal)
cd frontend
npm install
npm run dev
# Visit http://localhost:3000

## First run time
- Embedding model download: ~90MB, one-time only, cached after
- Sample document ingestion: ~2-4 minutes
- Every subsequent start: instant

## For focus group facilitators

### Before the session
1. Start backend, wait for "System ready" message
2. Start frontend
3. Open http://localhost:3000/about — walk participants through this first
4. On /analyse, click "Use Demo Application" to pre-fill the Lincoln example
5. Submit and walk through the results together

### What to highlight
- The citation panel (click any "Source" button) — show the actual policy text
- The confidence bar explanation — manage expectations
- The AI Transparency footer — show it costs £0.00
- The processing time — typically 8-25 seconds on free tier

### If Groq rate limit is hit
The system automatically falls back to Gemini. Both are free.
The console will show: "Groq rate limit hit — falling back to Gemini"

### Known demo limitations (be transparent)
- Only 3 planning documents loaded — production has hundreds
- Embeddings are 384-dim (smaller than production 3072-dim) — retrieval is good not perfect
- No GIS or mapping integration in this demo
- No user accounts or session memory
- Processing: 8-25 seconds on Groq free tier, up to 45s on Gemini

## Running cost
£0.00 per month. Forever. This is genuinely free.
