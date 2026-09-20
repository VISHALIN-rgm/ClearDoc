"""Text-to-speech for the explain step.

After Groq explains a document, its plain-language summary is spoken
aloud: this renders it to an MP3 with gTTS (Google's free
text-to-speech endpoint — no API key needed, just outbound internet
access) and saves it under data/audio/. The result's `audioUrl` points
the frontend at the file so it can play it back.

TTS is treated as best-effort: if it fails (no internet access, gTTS
hiccup, etc.) the pipeline still returns the written explanation —
speech is a bonus, not a requirement.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from gtts import gTTS

AUDIO_DIR = Path(__file__).parent / "data" / "audio"

logger = logging.getLogger(__name__)


def synthesize_speech(text: str, document_id: str) -> Optional[str]:
    """Speaks `text` to an MP3 file named after the document.

    Returns the *absolute* URL the frontend should use to play it
    (built from PUBLIC_BASE_URL, since the frontend and backend run on
    different ports/origins in local dev), or None if speech
    generation wasn't possible.
    """
    if not text or not text.strip():
        return None

    try:
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        file_path = AUDIO_DIR / f"{document_id}.mp3"
        gTTS(text=text, lang="en").save(str(file_path))
    except Exception:
        logger.warning("Speech synthesis failed for %s", document_id, exc_info=True)
        return None

    base_url = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    return f"{base_url}/audio/{document_id}.mp3"
