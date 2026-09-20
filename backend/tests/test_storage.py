import storage


def test_save_and_get_result(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "RESULTS_FILE", tmp_path / "results.json")

    item = {"documentId": "abc123", "status": "complete", "createdAt": 100}
    storage.save_result(item)

    assert storage.get_result("abc123") == item
    assert storage.get_result("does-not-exist") is None


def test_list_results_sorted_newest_first(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "RESULTS_FILE", tmp_path / "results.json")

    storage.save_result({"documentId": "a", "status": "complete", "createdAt": 1})
    storage.save_result({"documentId": "b", "status": "complete", "createdAt": 3})
    storage.save_result({"documentId": "c", "status": "complete", "createdAt": 2})

    ids = [item["documentId"] for item in storage.list_results()]

    assert ids == ["b", "c", "a"]


def test_delete_result_removes_entry(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "RESULTS_FILE", tmp_path / "results.json")

    storage.save_result({"documentId": "a", "status": "complete", "createdAt": 1})
    storage.save_result({"documentId": "b", "status": "complete", "createdAt": 2})

    deleted = storage.delete_result("a")

    assert deleted is True
    assert storage.get_result("a") is None
    assert storage.get_result("b") is not None


def test_delete_result_on_unknown_id_returns_false(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "DATA_DIR", tmp_path)
    monkeypatch.setattr(storage, "RESULTS_FILE", tmp_path / "results.json")

    assert storage.delete_result("does-not-exist") is False
