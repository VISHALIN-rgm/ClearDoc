# Architecture notes

```
 Browser (React, Vite dev server — single page)
        │  POST /upload  (base64 file)
        ▼
 FastAPI backend (localhost:8000)
        │  1. writes file to backend/data/uploads/
        │  2. returns {documentId, status: "processing"} immediately
        │  3. schedules pipeline.process_document() as a background task
        ▼
 pipeline.process_document()
        │
        ├─▶ extract_text()        (pypdf for PDFs, pytesseract OCR for images)
        │
        ├─▶ explain_document()    (Groq chat completion — structured JSON)
        │
        ├─▶ synthesize_speech()   (gTTS — spoken MP3 of the summary)
        │
        └─▶ save_result()         (writes to backend/data/results.json)

 Browser polls:
        GET /result/{documentId}  →  storage.get_result()  →  results.json
        GET /results              →  storage.list_results() →  results.json
        <audio src="/audio/{id}.mp3">  →  served by StaticFiles mount
```

**Why extraction is split by file type instead of one universal OCR
call:** PDFs usually already contain selectable text, so pulling it
directly with `pypdf` is faster and more accurate than OCR. Images
have no embedded text, so those go through `pytesseract` (a Python
wrapper around the Tesseract OCR engine) instead. Either path can
return an empty string without raising — the explain step is written
to handle that gracefully ("No readable text was found") rather than
the pipeline crashing.

**Why a background task instead of an orchestration service:** the
four steps are just Python function calls in a fixed order
(`pipeline.py`). Because there's no cross-service state to track,
there's no need for a workflow engine — `BackgroundTasks` (built into
FastAPI) is enough to let `/upload` return immediately while the work
continues after the response is sent.

**Why the pipeline doesn't branch on document type:** this is what
makes Doculyze an agent rather than a fixed script — the same
sequence — extract, explain, speak, save — runs regardless of what's
uploaded. The "what kind of document is this" judgment is left
entirely to the Groq prompt (`backend/prompts.py`), which asks the
model to identify the document type itself rather than the code
assuming it ahead of time. This keeps the system genuinely general
purpose instead of a set of if/else branches for a few hardcoded
categories.

**Why results are a local JSON file instead of a database:** for a
single-process local app, a small JSON file guarded by a lock is
enough to survive a server restart without adding a database
dependency. It only supports one writer at a time — a real deployment
serving multiple users concurrently would want to swap this for an
actual database (`storage.py` is the only place that would need to
change).

**Speech is best-effort:** `synthesize_speech()` never raises — if
gTTS can't reach Google (no internet, rate-limited, etc.) it logs a
warning and returns `None`, and the result is still saved with a
written explanation and no `audioUrl`. The frontend simply doesn't
render an audio player when that field is missing.

**Cost shape:** everything except the Groq call runs locally at no
cost. Groq's free tier covers this comfortably for demo/hackathon use;
check current limits at https://console.groq.com if you expect heavy
traffic.
