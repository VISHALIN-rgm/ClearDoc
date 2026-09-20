import json
from types import SimpleNamespace

import pytest

import groq_service


def _fake_client(fake_response):
    class FakeCompletions:
        def create(self, **kwargs):
            self.last_kwargs = kwargs
            return fake_response

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    return FakeClient()


def test_explain_document_empty_text_skips_api_call(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("Groq should not be called for empty input")

    monkeypatch.setattr(groq_service, "_get_client", fail_if_called)

    result = groq_service.explain_document("   ")

    assert result["document_type"] == "unknown"
    assert result["red_flags"] == []
    assert result["suggested_questions"] == []
    assert "re-uploading" in result["action_items"][0]


def test_explain_document_parses_model_json(monkeypatch):
    expected = {
        "document_type": "electricity bill",
        "summary": "This is a monthly electricity bill for 450 units.",
        "key_terms": ["Due date: 5th", "Amount: 1200"],
        "red_flags": [{"issue": "Late fee", "why_it_matters": "Adds 5%", "severity": "medium"}],
        "action_items": ["Pay before the due date"],
        "suggested_questions": ["What happens if I pay late?"],
    }

    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(expected)))]
    )

    def create(**kwargs):
        assert kwargs["messages"][1]["content"].startswith("Here is the extracted text")
        return fake_response

    fake_client = _fake_client(fake_response)
    fake_client.chat.completions.create = create
    monkeypatch.setattr(groq_service, "_get_client", lambda: fake_client)

    result = groq_service.explain_document("Your electricity bill for March is 1200 rupees.")

    assert result == expected


def test_explain_document_falls_back_on_bad_json(monkeypatch):
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="not json at all"))]
    )
    monkeypatch.setattr(groq_service, "_get_client", lambda: _fake_client(fake_response))

    result = groq_service.explain_document("some document text")

    assert result["document_type"] == "document"
    assert result["summary"] == "not json at all"
    assert result["suggested_questions"] == []


def test_explain_document_fills_missing_keys(monkeypatch):
    # Model returned valid JSON but forgot a couple of fields — the
    # caller should still get the full shape.
    partial = {"document_type": "lease", "summary": "A one-year lease."}
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(partial)))]
    )
    monkeypatch.setattr(groq_service, "_get_client", lambda: _fake_client(fake_response))

    result = groq_service.explain_document("lease text")

    assert result["key_terms"] == []
    assert result["red_flags"] == []
    assert result["action_items"] == []
    assert result["suggested_questions"] == []


def test_get_client_raises_without_api_key(monkeypatch):
    groq_service._client = None
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    try:
        with pytest.raises(RuntimeError):
            groq_service._get_client()
    finally:
        monkeypatch.setenv("GROQ_API_KEY", "test-key")
        groq_service._client = None


def test_answer_question_includes_document_context_and_history(monkeypatch):
    captured = {}

    def create(**kwargs):
        captured["messages"] = kwargs["messages"]
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Yes, a 5% late fee applies."))]
        )

    fake_client = _fake_client(None)
    fake_client.chat.completions.create = create
    monkeypatch.setattr(groq_service, "_get_client", lambda: fake_client)

    history = [
        {"role": "user", "content": "What's the due date?"},
        {"role": "assistant", "content": "The 5th of the month."},
    ]

    reply = groq_service.answer_question(
        document_text="Electricity bill. Due 5th. Late fee 5%.",
        summary="A monthly electricity bill.",
        history=history,
        question="Is there a late fee?",
    )

    assert reply == "Yes, a 5% late fee applies."
    messages = captured["messages"]
    # system prompt, document context, ack, then history, then the new question
    assert messages[0]["role"] == "system"
    assert "Electricity bill" in messages[1]["content"]
    assert messages[-1] == {"role": "user", "content": "Is there a late fee?"}
    assert history[0] in messages
    assert history[1] in messages
