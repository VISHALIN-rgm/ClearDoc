"""Shared data shapes used across Doculyze's backend.

Kept dependency-free (stdlib only) so it's easy to reason about and
easy to test.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import time
import uuid


@dataclass
class RedFlag:
    issue: str
    why_it_matters: str
    severity: str  # "low" | "medium" | "high"


@dataclass
class AnalysisResult:
    document_id: str
    status: str  # "processing" | "complete" | "failed"
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    summary: Optional[str] = None
    key_terms: List[str] = field(default_factory=list)
    red_flags: List[dict] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    audio_url: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=lambda: time.time())

    def to_api_dict(self) -> dict:
        """Camel-cased shape the frontend expects."""
        return {
            "documentId": self.document_id,
            "status": self.status,
            "documentName": self.document_name,
            "documentType": self.document_type,
            "summary": self.summary,
            "keyTerms": self.key_terms,
            "redFlags": self.red_flags,
            "actionItems": self.action_items,
            "audioUrl": self.audio_url,
            "error": self.error,
            "createdAt": self.created_at,
        }


def new_document_id() -> str:
    return uuid.uuid4().hex
