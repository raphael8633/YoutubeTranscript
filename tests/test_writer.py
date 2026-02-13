import os
import pytest
from youtubetranscript.writer import write


def test_write_creates_file(tmp_path):
    out = tmp_path / "transcript.txt"
    result = write("Hello world", str(out))
    assert result == str(out)
    assert out.read_text(encoding="utf-8") == "Hello world"


def test_write_overwrites_existing_file(tmp_path):
    out = tmp_path / "transcript.txt"
    out.write_text("old content", encoding="utf-8")
    write("new content", str(out))
    assert out.read_text(encoding="utf-8") == "new content"


def test_write_sanitizes_title_as_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = write("text", "My Video: Part 1/2?")
    assert os.path.exists(result)
    assert "/" not in os.path.basename(result)
    assert ":" not in os.path.basename(result)
    assert "?" not in os.path.basename(result)


def test_write_appends_txt_extension_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = write("text", "mytranscript")
    assert result.endswith(".txt")
