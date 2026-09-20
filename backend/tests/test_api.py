import base64

from fastapi.testclient import TestClient

import app as app_module
import cancellation
import storage


def _client(monkeypatch):
    # Don't actually run extraction/Groq/gTTS during API tests — just
    # prove the endpoint wires a background task and returns the
    # right shape. The pipeline itself is covered by its own tests.
    calls = []
    monkeypatch.setattr(
        app_module, "process_document", lambda *args: calls.append(args)
    )
    return TestClient(app_module.app), calls


def test_health():
    client = TestClient(app_module.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root():
    client = TestClient(app_module.app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Doculyze API"


def test_upload_returns_processing_and_schedules_pipeline(monkeypatch, tmp_path):
    monkeypatch.setattr(app_module, "UPLOADS_DIR", tmp_path)
    client, calls = _client(monkeypatch)

    file_bytes = b"hello world"
    payload = {
        "file": base64.b64encode(file_bytes).decode(),
        "file_name": "note.txt",
    }

    response = client.post("/upload", json=payload)

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "processing"
    assert "documentId" in body
    assert len(calls) == 1


def test_upload_accepts_data_url_prefix(monkeypatch, tmp_path):
    monkeypatch.setattr(app_module, "UPLOADS_DIR", tmp_path)
    client, calls = _client(monkeypatch)

    file_bytes = b"hello again"
    b64 = base64.b64encode(file_bytes).decode()
    payload = {"file": f"data:text/plain;base64,{b64}", "file_name": "note.txt"}

    response = client.post("/upload", json=payload)

    assert response.status_code == 202
    assert len(calls) == 1


def test_upload_rejects_invalid_base64(monkeypatch, tmp_path):
    monkeypatch.setattr(app_module, "UPLOADS_DIR", tmp_path)
    client, _ = _client(monkeypatch)

    response = client.post("/upload", json={"file": "!!!not base64!!!", "file_name": "x.txt"})

    assert response.status_code == 400


def test_result_returns_processing_when_unknown(monkeypatch):
    monkeypatch.setattr(storage, "get_result", lambda doc_id: None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.get("/result/does-not-exist")

    assert response.status_code == 200
    assert response.json() == {"documentId": "does-not-exist", "status": "processing"}


def test_result_returns_stored_item_without_internal_fields(monkeypatch):
    item = {
        "documentId": "abc",
        "status": "complete",
        "summary": "hi",
        "documentText": "the full raw text, kept internal",
        "chatHistory": [{"role": "user", "content": "hey"}],
    }
    monkeypatch.setattr(storage, "get_result", lambda doc_id: item if doc_id == "abc" else None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.get("/result/abc")
    body = response.json()

    assert body["documentId"] == "abc"
    assert body["summary"] == "hi"
    assert "documentText" not in body
    assert "chatHistory" not in body


def test_results_lists_recent_without_internal_fields(monkeypatch):
    items = [
        {"documentId": "b", "documentText": "secret internal text"},
        {"documentId": "a"},
    ]
    monkeypatch.setattr(storage, "list_results", lambda limit=20: items)
    monkeypatch.setattr(app_module, "list_results", storage.list_results)
    client = TestClient(app_module.app)

    response = client.get("/results")
    body = response.json()

    assert [item["documentId"] for item in body] == ["b", "a"]
    assert "documentText" not in body[0]


def test_cancel_flags_a_processing_job(monkeypatch):
    monkeypatch.setattr(storage, "get_result", lambda doc_id: {"documentId": doc_id, "status": "processing"})
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.post("/cancel/doc-123")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelling"
    assert cancellation.is_cancelled("doc-123") is True
    cancellation.clear("doc-123")


def test_cancel_on_unknown_job_still_flags_it(monkeypatch):
    monkeypatch.setattr(storage, "get_result", lambda doc_id: None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.post("/cancel/doc-unknown")

    assert response.status_code == 200
    assert cancellation.is_cancelled("doc-unknown") is True
    cancellation.clear("doc-unknown")


def test_cancel_on_already_complete_job_is_a_noop(monkeypatch):
    finished = {"documentId": "doc-done", "status": "complete", "summary": "done"}
    monkeypatch.setattr(storage, "get_result", lambda doc_id: finished)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.post("/cancel/doc-done")

    assert response.status_code == 200
    assert response.json()["status"] == "complete"
    assert cancellation.is_cancelled("doc-done") is False


def test_get_chat_returns_history(monkeypatch):
    item = {"documentId": "doc-1", "chatHistory": [{"role": "user", "content": "hi"}]}
    monkeypatch.setattr(storage, "get_result", lambda doc_id: item if doc_id == "doc-1" else None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.get("/chat/doc-1")

    assert response.status_code == 200
    assert response.json()["history"] == [{"role": "user", "content": "hi"}]


def test_get_chat_404_for_unknown_document(monkeypatch):
    monkeypatch.setattr(storage, "get_result", lambda doc_id: None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.get("/chat/does-not-exist")

    assert response.status_code == 404


def test_post_chat_answers_and_saves_history(monkeypatch):
    item = {
        "documentId": "doc-1",
        "status": "complete",
        "documentText": "Electricity bill. Due 5th.",
        "summary": "A bill due on the 5th.",
        "chatHistory": [],
    }
    saved = {}

    monkeypatch.setattr(storage, "get_result", lambda doc_id: item if doc_id == "doc-1" else None)
    monkeypatch.setattr(storage, "save_result", lambda saved_item: saved.update(saved_item))
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    monkeypatch.setattr(app_module, "save_result", storage.save_result)
    monkeypatch.setattr(
        app_module, "answer_question", lambda **kwargs: "You must pay by the 5th."
    )

    client = TestClient(app_module.app)
    response = client.post("/chat/doc-1", json={"message": "When is it due?"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "You must pay by the 5th."
    assert body["history"] == [
        {"role": "user", "content": "When is it due?"},
        {"role": "assistant", "content": "You must pay by the 5th."},
    ]
    assert saved["chatHistory"] == body["history"]


def test_post_chat_rejects_unready_document(monkeypatch):
    item = {"documentId": "doc-1", "status": "processing"}
    monkeypatch.setattr(storage, "get_result", lambda doc_id: item)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.post("/chat/doc-1", json={"message": "hi"})

    assert response.status_code == 409


def test_post_chat_rejects_empty_message(monkeypatch):
    item = {"documentId": "doc-1", "status": "complete"}
    monkeypatch.setattr(storage, "get_result", lambda doc_id: item)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.post("/chat/doc-1", json={"message": "   "})

    assert response.status_code == 400


def test_post_chat_404_for_unknown_document(monkeypatch):
    monkeypatch.setattr(storage, "get_result", lambda doc_id: None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.post("/chat/does-not-exist", json={"message": "hi"})

    assert response.status_code == 404


def test_delete_removes_result_and_files(monkeypatch, tmp_path):
    upload_path = tmp_path / "doc-1_bill.txt"
    upload_path.write_text("hello")
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    audio_path = audio_dir / "doc-1.mp3"
    audio_path.write_bytes(b"fake-mp3")

    item = {"documentId": "doc-1", "status": "complete", "filePath": str(upload_path)}
    deleted_ids = []

    monkeypatch.setattr(storage, "get_result", lambda doc_id: item if doc_id == "doc-1" else None)
    monkeypatch.setattr(storage, "delete_result", lambda doc_id: deleted_ids.append(doc_id) or True)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    monkeypatch.setattr(app_module, "delete_result", storage.delete_result)
    monkeypatch.setattr(app_module, "AUDIO_DIR", audio_dir)

    client = TestClient(app_module.app)
    response = client.delete("/result/doc-1")

    assert response.status_code == 200
    assert response.json() == {"documentId": "doc-1", "deleted": True}
    assert deleted_ids == ["doc-1"]
    assert not upload_path.exists()
    assert not audio_path.exists()


def test_delete_404_for_unknown_document(monkeypatch):
    monkeypatch.setattr(storage, "get_result", lambda doc_id: None)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    client = TestClient(app_module.app)

    response = client.delete("/result/does-not-exist")

    assert response.status_code == 404


def test_delete_tolerates_missing_files_on_disk(monkeypatch, tmp_path):
    # filePath points at a file that's already gone — delete should
    # still succeed rather than raising.
    item = {"documentId": "doc-2", "status": "complete", "filePath": str(tmp_path / "gone.txt")}

    monkeypatch.setattr(storage, "get_result", lambda doc_id: item if doc_id == "doc-2" else None)
    monkeypatch.setattr(storage, "delete_result", lambda doc_id: True)
    monkeypatch.setattr(app_module, "get_result", storage.get_result)
    monkeypatch.setattr(app_module, "delete_result", storage.delete_result)
    monkeypatch.setattr(app_module, "AUDIO_DIR", tmp_path)

    client = TestClient(app_module.app)
    response = client.delete("/result/doc-2")

    assert response.status_code == 200
