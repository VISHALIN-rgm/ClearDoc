import cancellation
import pipeline
import storage


def _patch_storage(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "RESULTS_FILE", tmp_path / "results.json")
    monkeypatch.setattr(pipeline, "save_result", storage.save_result)


def test_process_document_completes_normally(monkeypatch, tmp_path):
    _patch_storage(monkeypatch, tmp_path)
    monkeypatch.setattr(pipeline, "extract_text", lambda path, name: "some text")
    monkeypatch.setattr(
        pipeline,
        "explain_document",
        lambda text: {
            "document_type": "note",
            "summary": "A short note.",
            "key_terms": [],
            "red_flags": [],
            "action_items": [],
            "suggested_questions": ["What is this about?"],
        },
    )
    monkeypatch.setattr(pipeline, "synthesize_speech", lambda text, doc_id: "http://x/a.mp3")

    pipeline.process_document("doc-ok", "/tmp/fake", "note.txt")

    item = storage.get_result("doc-ok")
    assert item["status"] == "complete"
    assert item["summary"] == "A short note."
    assert item["documentText"] == "some text"
    assert item["chatHistory"] == []
    assert item["suggestedQuestions"] == ["What is this about?"]
    assert item["filePath"] == "/tmp/fake"
    assert cancellation.is_cancelled("doc-ok") is False


def test_process_document_stops_before_explain_if_cancelled(monkeypatch, tmp_path):
    _patch_storage(monkeypatch, tmp_path)
    monkeypatch.setattr(pipeline, "extract_text", lambda path, name: "some text")

    def fail_if_called(text):
        raise AssertionError("explain_document should not run once cancelled")

    monkeypatch.setattr(pipeline, "explain_document", fail_if_called)

    cancellation.request_cancel("doc-cancel")
    pipeline.process_document("doc-cancel", "/tmp/fake", "note.txt")

    item = storage.get_result("doc-cancel")
    assert item["status"] == "cancelled"
    assert cancellation.is_cancelled("doc-cancel") is False


def test_process_document_stops_before_speech_if_cancelled_mid_run(monkeypatch, tmp_path):
    _patch_storage(monkeypatch, tmp_path)
    monkeypatch.setattr(pipeline, "extract_text", lambda path, name: "some text")

    def explain_then_cancel(text):
        cancellation.request_cancel("doc-late-cancel")
        return {"summary": "won't be used", "document_type": "x"}

    monkeypatch.setattr(pipeline, "explain_document", explain_then_cancel)

    def fail_if_called(text, doc_id):
        raise AssertionError("synthesize_speech should not run once cancelled")

    monkeypatch.setattr(pipeline, "synthesize_speech", fail_if_called)

    pipeline.process_document("doc-late-cancel", "/tmp/fake", "note.txt")

    item = storage.get_result("doc-late-cancel")
    assert item["status"] == "cancelled"


def test_process_document_handles_exception_as_failed(monkeypatch, tmp_path):
    _patch_storage(monkeypatch, tmp_path)

    def boom(path, name):
        raise RuntimeError("disk exploded")

    monkeypatch.setattr(pipeline, "extract_text", boom)

    pipeline.process_document("doc-fail", "/tmp/fake", "note.txt")

    item = storage.get_result("doc-fail")
    assert item["status"] == "failed"
    assert "disk exploded" in item["error"]
