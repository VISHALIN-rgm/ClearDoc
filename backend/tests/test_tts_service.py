import tts_service


def test_synthesize_speech_returns_none_for_empty_text():
    assert tts_service.synthesize_speech("", "doc-1") is None
    assert tts_service.synthesize_speech("   ", "doc-1") is None


def test_synthesize_speech_returns_none_when_gtts_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(tts_service, "AUDIO_DIR", tmp_path)

    class BoomTTS:
        def __init__(self, *args, **kwargs):
            pass

        def save(self, *args, **kwargs):
            raise RuntimeError("no network access")

    monkeypatch.setattr(tts_service, "gTTS", BoomTTS)

    result = tts_service.synthesize_speech("Hello there", "doc-2")

    assert result is None


def test_synthesize_speech_builds_absolute_url(monkeypatch, tmp_path):
    monkeypatch.setattr(tts_service, "AUDIO_DIR", tmp_path)
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://localhost:8000")

    class FakeTTS:
        def __init__(self, *args, **kwargs):
            pass

        def save(self, path):
            with open(path, "wb") as f:
                f.write(b"fake-mp3-bytes")

    monkeypatch.setattr(tts_service, "gTTS", FakeTTS)

    url = tts_service.synthesize_speech("Hello there", "doc-3")

    assert url == "http://localhost:8000/audio/doc-3.mp3"
    assert (tmp_path / "doc-3.mp3").exists()
