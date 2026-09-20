from extraction import extract_text


def test_extract_txt_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello, this is a plain text document.", encoding="utf-8")

    text = extract_text(str(file_path), "sample.txt")

    assert text == "Hello, this is a plain text document."


def test_extract_unreadable_image_returns_empty_not_raises(tmp_path):
    # Not a real image — should degrade to "" rather than raising.
    file_path = tmp_path / "broken.png"
    file_path.write_bytes(b"not actually a png")

    text = extract_text(str(file_path), "broken.png")

    assert text == ""


def test_extract_truncates_long_text(tmp_path):
    file_path = tmp_path / "long.txt"
    file_path.write_text("a" * 20000, encoding="utf-8")

    text = extract_text(str(file_path), "long.txt")

    assert len(text) == 15000
