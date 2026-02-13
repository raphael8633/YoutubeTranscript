import pytest
from unittest.mock import patch, MagicMock
from youtubetranscript.captions import fetch


def _make_snippet(text: str, start: float):
    s = MagicMock()
    s.text = text
    s.start = start
    return s


_SNIPPETS = [_make_snippet("Hello", 0.0), _make_snippet("World", 2.5)]
_EXPECTED = [{"text": "Hello", "start": 0.0}, {"text": "World", "start": 2.5}]


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_returns_segments(mock_cls):
    instance = mock_cls.return_value
    instance.fetch.return_value = _SNIPPETS
    result = fetch("dQw4w9WgXcQ", lang=None)
    assert result == _EXPECTED
    instance.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["en"])


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_uses_specified_lang(mock_cls):
    instance = mock_cls.return_value
    instance.fetch.return_value = _SNIPPETS
    fetch("dQw4w9WgXcQ", lang="es")
    instance.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["es"])


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_returns_none_on_no_transcript(mock_cls):
    from youtube_transcript_api._errors import NoTranscriptFound
    instance = mock_cls.return_value
    instance.fetch.side_effect = NoTranscriptFound("dQw4w9WgXcQ", ["en"], MagicMock())
    result = fetch("dQw4w9WgXcQ", lang=None)
    assert result is None


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_returns_none_on_transcripts_disabled(mock_cls):
    from youtube_transcript_api._errors import TranscriptsDisabled
    instance = mock_cls.return_value
    instance.fetch.side_effect = TranscriptsDisabled("dQw4w9WgXcQ")
    result = fetch("dQw4w9WgXcQ", lang=None)
    assert result is None
