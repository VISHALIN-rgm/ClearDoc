"""Doculyze API — a single local FastAPI service.

Replaces API Gateway + 6 separate Lambda functions with one app:

    POST /upload            -> stores the file, kicks off the pipeline
    GET  /result/{id}       -> a single analysis (or {"status": "processing"})
    GET  /results           -> recent analyses, newest first
    POST /cancel/{id}       -> best-effort cancel of an in-flight job
    GET  /chat/{id}         -> this document's chat history
    POST /chat/{id}         -> ask a question about this document
    GET  /audio/{file}.mp3  -> the spoken summary (static files)
    GET  /health            -> liveness check

Run it with:
    uvicorn app:app --reload --port 8000
"""

import base64
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import cancellation
from groq_service import answer_question
from models import new_document_id
from pipeline import process_document
from storage import delete_result, get_result, list_results, save_result

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
AUDIO_DIR = BASE_DIR / "data" / "audio"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Fields that are internal to the pipeline/chat and never sent to the
# frontend via /result or /results — the full document text and chat
# transcript can be large, and the chat transcript has its own
# dedicated endpoint anyway. filePath is a server-side disk path, not
# something the frontend has any use for.
_INTERNAL_FIELDS = {"documentText", "chatHistory", "filePath"}

app = FastAPI(title="Doculyze API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves the gTTS-generated narration files the frontend plays back.
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")


def _public(item: dict) -> dict:
    return {k: v for k, v in item.items() if k not in _INTERNAL_FIELDS}


class UploadPayload(BaseModel):
    file: str  # base64-encoded file contents (optionally a data: URL)
    file_name: str = "document"


class ChatPayload(BaseModel):
    message: str


@app.post("/upload", status_code=202)
def upload(payload: UploadPayload, background_tasks: BackgroundTasks):
    file_b64 = payload.file
    if "," in file_b64 and file_b64.strip().startswith("data:"):
        file_b64 = file_b64.split(",", 1)[1]

    try:
        file_bytes = base64.b64decode(file_b64)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid file payload: {exc}") from exc

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    document_id = new_document_id()
    safe_name = (payload.file_name or "document").replace("/", "_").replace("\\", "_")
    file_path = UPLOADS_DIR / f"{document_id}_{safe_name}"
    file_path.write_bytes(file_bytes)

    background_tasks.add_task(process_document, document_id, str(file_path), safe_name)

    return {"documentId": document_id, "status": "processing"}


@app.get("/result/{document_id}")
def result(document_id: str):
    item = get_result(document_id)
    if not item:
        return {"documentId": document_id, "status": "processing"}
    return _public(item)


@app.get("/results")
def results():
    return [_public(item) for item in list_results()]


@app.delete("/result/{document_id}")
def delete(document_id: str):
    """Deletes a document's stored result, its uploaded file, and its
    generated audio narration. Also flags any in-flight job for that
    id so a pipeline that's mid-run doesn't resurrect the result after
    this returns."""
    item = get_result(document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found.")

    cancellation.request_cancel(document_id)

    file_path = item.get("filePath")
    if file_path:
        Path(file_path).unlink(missing_ok=True)

    (AUDIO_DIR / f"{document_id}.mp3").unlink(missing_ok=True)

    delete_result(document_id)
    return {"documentId": document_id, "deleted": True}


@app.post("/cancel/{document_id}")
def cancel(document_id: str):
    """Best-effort: flags the job so the pipeline stops at its next
    checkpoint (see pipeline.py). If the job already finished, this is
    a no-op and the existing result stands."""
    item = get_result(document_id)
    if item and item.get("status") not in ("processing", None):
        # Already finished (complete/failed/cancelled) — nothing to cancel.
        return _public(item)

    cancellation.request_cancel(document_id)
    return {"documentId": document_id, "status": "cancelling"}


@app.get("/chat/{document_id}")
def get_chat(document_id: str):
    item = get_result(document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"documentId": document_id, "history": item.get("chatHistory", [])}


@app.post("/chat/{document_id}")
def post_chat(document_id: str, payload: ChatPayload):
    item = get_result(document_id)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found.")
    if item.get("status") != "complete":
        raise HTTPException(status_code=409, detail="Document isn't ready yet.")

    question = payload.message.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message can't be empty.")

    history = item.get("chatHistory", [])

    try:
        reply = answer_question(
            document_text=item.get("documentText", ""),
            summary=item.get("summary", ""),
            history=history,
            question=question,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Chat failed: {exc}") from exc

    history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": reply},
    ]
    item["chatHistory"] = history
    save_result(item)

    return {"documentId": document_id, "reply": reply, "history": history}


@app.get("/")
def root():
    return {
        "service": "Doculyze API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
