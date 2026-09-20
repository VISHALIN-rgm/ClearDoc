# Doculyze

**Any document in. Plain language out — and read aloud.**

Doculyze is an AI agent that reads a document — any document — and
explains it back to you in plain language: what it says, what
matters, and what to watch out for. Upload a PDF, image, or text file
and get a structured breakdown: summary, key terms, flagged risks, and
suggested next actions. The summary is also spoken aloud, so you can
listen instead of read.

It behaves like an agent rather than a fixed script: nothing in the
pipeline is told ahead of time what kind of document it's looking at
or what to look for in it. Given raw text, it decides for itself what
the document is, what's worth flagging, and how severe each flag is —
the same four-step pipeline handles a bill, a lease, a syllabus, or
anything else without a single if/else branch on document type.

This runs entirely on your own machine: a local Python backend plus
a React frontend, no cloud account or infrastructure required. The
only external services it calls out to are [Groq](https://groq.com)
for the explanation step and Google's free TTS endpoint for speech.

## Architecture

```
 ┌──────────┐   POST /upload    ┌───────────────────┐
 │  React   │──────────────────▶│  FastAPI backend   │
 │ frontend │                   │  (localhost:8000)  │
 │(Vite dev │◀──────────────────│                     │
 │  server) │  GET /result/{id} └──────────┬──────────┘
 └──────────┘                              │
                                            ▼
                              ┌─────────────────────────┐
                              │   pipeline.py             │
                              │                            │
                              │  1. extract_text()         │  local (pypdf / pytesseract)
                              │        │                   │
                              │        ▼                   │
                              │  2. explain_document()      │  Groq (LLM)
                              │        │                   │
                              │        ▼                   │
                              │  3. synthesize_speech()      │  gTTS (text-to-speech)
                              │        │                   │
                              │        ▼                   │
                              │  4. save_result()            │  local JSON file
                              └─────────────────────────┘
```

Flow: the frontend posts the file (base64) to `/upload` → the backend
saves it to disk and immediately returns a `documentId`, then keeps
working in the background → text is pulled out locally (no cloud OCR
service) → the extracted text is sent to Groq for a structured,
plain-language explanation → the summary is turned into an MP3
narration → everything is saved to a small local JSON store → the
frontend polls `GET /result/{documentId}` until it's ready, including
an `audioUrl` it plays back.

**Uploading opens a dashboard, not an inline card.** The moment a file
is picked, the app switches from the upload screen to a dedicated
document view on the same page — a processing screen with a cancel
(✕) button, then the explanation alongside a chat panel once it's
ready. Cancelling stops the frontend from waiting immediately, and
best-effort stops the backend pipeline at its next checkpoint (see
`cancellation.py`).

**Chat is scoped to the one document.** `POST /chat/{documentId}`
answers using only that document's extracted text and explanation —
if the answer isn't in the document, the model is instructed to say
so rather than guess. Each document also gets a few Groq-generated
suggested questions shown as starter chips.

**Recent documents get a history panel with delete.** `GET /results`
backs a slide-out panel of past documents; each has a delete (trash)
icon that calls `DELETE /result/{documentId}` to remove its stored
result, uploaded file, and audio narration together.

**Why a background task instead of an orchestration service:** the
whole pipeline is one Python function (`pipeline.py`) run after the
HTTP response is sent, so there's no separate workflow service to
deploy or reason about — the four steps just run in order, in-process.

**Why the pipeline doesn't branch on document type:** the same
sequence — extract, explain, speak, save — runs regardless of what's
uploaded. The "what kind of document is this" judgment is left
entirely to the Groq prompt (`backend/prompts.py`), which asks the
model to identify the document type itself rather than the code
assuming it ahead of time.

## Repo layout

```
doculyze/
├── backend/    FastAPI app + the extract/explain/speak/save pipeline (Python)
├── frontend/   React + Vite single-page app (glassmorphism UI)
├── docs/       architecture notes, sample docs, demo script
└── scripts/    local run + seed helpers
```

### Backend modules

| Module | Does |
|---|---|
| `app.py` | FastAPI routes: `POST /upload`, `GET/POST /chat/{id}`, `POST /cancel/{id}`, `DELETE /result/{id}`, `GET /result/{id}`, `GET /results`, serves `/audio/*` |
| `cancellation.py` | In-memory cancel flags the pipeline checks between steps |
| `extraction.py` | Pulls text out of PDFs (`pypdf`) and images (`pytesseract` OCR) |
| `groq_service.py` | Sends extracted text to Groq, parses the structured JSON explanation |
| `tts_service.py` | Turns the summary into speech (`gTTS`), saved as an MP3 |
| `pipeline.py` | Runs the four steps above in order, in a background task |
| `storage.py` | Local JSON-file result store (keyed by `documentId`) |
| `prompts.py` | The system prompt sent to Groq |

## Prerequisites

- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com/keys)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed
  on your system, **only if** you want to upload scanned images —
  PDF and `.txt` uploads don't need it.
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt install tesseract-ocr`
  - Windows: [installer here](https://github.com/UB-Mannheim/tesseract/wiki)
- An internet connection (Groq's API and Google's TTS endpoint are both
  remote calls — nothing in the pipeline runs fully offline)

## Run the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # paste in your GROQ_API_KEY
uvicorn app:app --reload --port 8000
```

The API is now at `http://localhost:8000` (check `GET /health`).

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env            # defaults to http://localhost:8000, change if needed
npm run dev                     # local dev, http://localhost:5173
npm run build                   # production build (dist/) — serve with any static host
```

The app is a single page — hero, upload box, results, and the
How It Works / Why Doculyze / Use Cases / FAQ sections all live on one
scroll, with in-page anchor navigation.

## Run both at once

```bash
./scripts/run.sh
```

Starts the backend on :8000 and the frontend dev server on :5173, and
stops both when you press Ctrl+C. The first run still needs
`backend/.env` and `frontend/.env` set up as above, and both
`pip install` / `npm install` already done.

## Local test data

`scripts/seed_test_data.sh` uploads a couple of sample documents from
`docs/sample-documents/` straight to the running backend via `curl`,
so you can watch the pipeline run end-to-end without using the UI.

```bash
./scripts/seed_test_data.sh
```

## Running backend tests

```bash
cd backend
pip install -r requirements.txt   # includes pytest + httpx
python3 -m pytest tests/ -v
```

All tests mock the Groq and gTTS calls, so they run offline and don't
need a real API key.

