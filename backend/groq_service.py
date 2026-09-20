"""explain and chat steps — Groq instead of Amazon Bedrock.

explain_document(): sends the extracted document text to a
Groq-hosted LLM and parses the structured JSON explanation back out —
summary, key terms, red flags, action items, and a few suggested
questions. Works the same way no matter what kind of document was
uploaded — the prompt (see prompts.py), not this code, is what decides
what the document is.

answer_question(): a follow-up chat turn scoped to one document — the
model only sees that document's text and summary, plus prior turns in
the conversation, so it can't wander into unrelated small talk.
"""

import json
import os

from groq import Groq

from prompts import (
    CHAT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_chat_context,
    build_user_prompt,
)

DEFAULT_MODEL = "openai/gpt-oss-120b"

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Add it to backend/.env "
                "(see backend/.env.example) — get a free key at "
                "https://console.groq.com/keys"
            )
        _client = Groq(api_key=api_key)
    return _client


def _model() -> str:
    return os.environ.get("GROQ_MODEL", DEFAULT_MODEL)


def explain_document(document_text: str) -> dict:
    """Returns a dict with document_type, summary, key_terms, red_flags,
    action_items, suggested_questions — always this shape, even on
    empty input or a model response that fails to parse as JSON."""

    if not document_text.strip():
        return {
            "document_type": "unknown",
            "summary": "No readable text was found in this document.",
            "key_terms": [],
            "red_flags": [],
            "action_items": ["Try re-uploading a clearer scan or a text-based file."],
            "suggested_questions": [],
        }

    client = _get_client()

    response = client.chat.completions.create(
        model=_model(),
        max_tokens=1500,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(document_text)},
        ],
    )

    model_text = response.choices[0].message.content or ""
    return _safe_parse_explanation(model_text)


def answer_question(
    document_text: str,
    summary: str,
    history: list[dict],
    question: str,
) -> str:
    """Answers one chat turn about a specific document.

    `history` is a list of {"role": "user"|"assistant", "content": str}
    dicts from earlier turns in this document's conversation, oldest
    first. Returns the assistant's plain-text reply.
    """
    client = _get_client()

    messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": build_chat_context(document_text, summary)},
        {"role": "assistant", "content": "Understood — I'll answer based on this document."},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=_model(),
        max_tokens=600,
        temperature=0.3,
        messages=messages,
    )

    return (response.choices[0].message.content or "").strip()


def _safe_parse_explanation(text: str) -> dict:
    """The model is instructed to return raw JSON, but strip code fences
    defensively in case it wraps the response anyway, and fill in any
    missing keys so callers always get the full shape."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed = {
            "document_type": "document",
            "summary": text[:800],
            "key_terms": [],
            "red_flags": [],
            "action_items": [],
        }

    parsed.setdefault("document_type", "document")
    parsed.setdefault("summary", "")
    parsed.setdefault("key_terms", [])
    parsed.setdefault("red_flags", [])
    parsed.setdefault("action_items", [])
    parsed.setdefault("suggested_questions", [])
    return parsed
