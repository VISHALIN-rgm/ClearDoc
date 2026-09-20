"""The whole extract -> explain -> speak -> save pipeline.

Replaces the AWS Step Functions state machine: instead of Lambda steps
strung together with Wait/Choice states, this is one plain Python
function run in a background task. Same shape, same order of
operations, no orchestration service required:

    extract_text (local, no Textract)
        -> explain_document (Groq, no Bedrock)
            -> synthesize_speech (gTTS)
                -> save_result (local JSON store, no DynamoDB)

`cancellation.is_cancelled()` is checked between each step so a
`POST /cancel/{id}` takes effect at the next checkpoint rather than
only being noticed after the whole pipeline finishes.
"""

import logging
import time

import cancellation
from extraction import extract_text
from groq_service import explain_document
from storage import save_result
from tts_service import synthesize_speech

logger = logging.getLogger(__name__)


def _cancelled_item(document_id: str, file_name: str, file_path: str) -> dict:
    return {
        "documentId": document_id,
        "status": "cancelled",
        "documentName": file_name,
        "filePath": file_path,
        "createdAt": int(time.time()),
    }


def process_document(document_id: str, file_path: str, file_name: str) -> None:
    def bail_if_cancelled() -> bool:
        if not cancellation.is_cancelled(document_id):
            return False
        save_result(_cancelled_item(document_id, file_name, file_path))
        cancellation.clear(document_id)
        return True

    try:
        if bail_if_cancelled():
            return

        text = extract_text(file_path, file_name)

        if bail_if_cancelled():
            return

        explanation = explain_document(text)

        if bail_if_cancelled():
            return

        summary = explanation.get("summary", "")
        audio_url = synthesize_speech(summary, document_id)

        if bail_if_cancelled():
            return

        item = {
            "documentId": document_id,
            "status": "complete",
            "documentName": file_name,
            "filePath": file_path,
            "documentType": explanation.get("document_type", "document"),
            "summary": summary,
            "keyTerms": explanation.get("key_terms", []),
            "redFlags": explanation.get("red_flags", []),
            "actionItems": explanation.get("action_items", []),
            "suggestedQuestions": explanation.get("suggested_questions", []),
            "audioUrl": audio_url,
            "createdAt": int(time.time()),
            # Kept for the chat endpoint (see app.py) — not part of the
            # public /result response.
            "documentText": text,
            "chatHistory": [],
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Processing failed for document %s", document_id)
        item = {
            "documentId": document_id,
            "status": "failed",
            "documentName": file_name,
            "filePath": file_path,
            "error": str(exc),
            "createdAt": int(time.time()),
        }

    save_result(item)
    cancellation.clear(document_id)
