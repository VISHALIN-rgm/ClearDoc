"""Cancellation flags for in-flight pipeline jobs.

The pipeline (extract -> explain -> speak -> save) runs as a single
background task per document. There's no external job queue to pull a
task off of, so cancellation works by a flag the pipeline checks
between steps: `POST /cancel/{id}` sets the flag, and
`pipeline.process_document` looks at it after each step, stopping
early (and saving a "cancelled" result) if it's set.

This is best-effort, not a hard kill: a step already in flight (e.g. a
Groq request that's already been sent) still completes — cancellation
takes effect at the next checkpoint, not mid-network-call. In practice
this means cancelling during extraction is near-instant, and
cancelling during explain/speak stops the pipeline right after that
step returns.
"""

import threading

_cancelled: set[str] = set()
_lock = threading.Lock()


def request_cancel(document_id: str) -> None:
    with _lock:
        _cancelled.add(document_id)


def is_cancelled(document_id: str) -> bool:
    with _lock:
        return document_id in _cancelled


def clear(document_id: str) -> None:
    """Drop the flag once a job reaches a terminal state, so the set
    doesn't grow unbounded over a long-running server."""
    with _lock:
        _cancelled.discard(document_id)
