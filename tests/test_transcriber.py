import pytest
from unittest.mock import patch, MagicMock
from youtubetranscript.transcriber import transcribe


def _make_segment(text: str, start: float):
    seg = MagicMock()
    seg.text = text
    seg.start = start
    return seg


@patch("youtubetranscript.transcriber.WhisperModel")
def test_transcribe_returns_segments(mock_cls):
    model_instance = mock_cls.return_value
    segs = [_make_segment(" Hello", 0.0), _make_segment(" World", 2.5)]
    model_instance.transcribe.return_value = (iter(segs), MagicMock())

    result = transcribe("/tmp/audio.m4a", lang=None, model="base")
    assert result == [{"text": "Hello", "start": 0.0}, {"text": "World", "start": 2.5}]


@patch("youtubetranscript.transcriber.WhisperModel")
def test_transcribe_passes_language(mock_cls):
    model_instance = mock_cls.return_value
    model_instance.transcribe.return_value = (iter([]), MagicMock())

    transcribe("/tmp/audio.m4a", lang="es", model="base")
    call_kwargs = model_instance.transcribe.call_args[1]
    assert call_kwargs.get("language") == "es"


@patch("youtubetranscript.transcriber.WhisperModel")
def test_transcribe_strips_whitespace_from_text(mock_cls):
    model_instance = mock_cls.return_value
    segs = [_make_segment("  leading and trailing  ", 1.0)]
    model_instance.transcribe.return_value = (iter(segs), MagicMock())

    result = transcribe("/tmp/audio.m4a", lang=None, model="base")
    assert result[0]["text"] == "leading and trailing"
