import pytest
from unittest.mock import patch, MagicMock
from youtubetranscript.captions import fetch


def _make_snippet(text: str, start: float):
    s = MagicMock()
    s.text = text
    s.start = start
    return s


def _make_transcript(code: str, generated: bool, snippets):
    t = MagicMock()
    t.language_code = code
    t.is_generated = generated
    t.fetch.return_value = snippets
    return t


_SNIPPETS = [_make_snippet("Hello", 0.0), _make_snippet("World", 2.5)]
_EXPECTED = [{"text": "Hello", "start": 0.0}, {"text": "World", "start": 2.5}]


def _transcript_list(transcripts):
    """Mimic TranscriptList: iterates manual transcripts before generated ones."""
    tl = MagicMock()
    tl.__iter__ = MagicMock(side_effect=lambda: iter(transcripts))
    return tl


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_without_lang_takes_first_available_transcript(mock_cls):
    """A zh-Hant-only video must not fall through to Whisper when lang is unset."""
    zh = _make_transcript("zh-Hant", False, _SNIPPETS)
    mock_cls.return_value.list.return_value = _transcript_list([zh])
    assert fetch("vid", lang=None) == _EXPECTED
    mock_cls.return_value.list.assert_called_once_with("vid")


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_with_lang_uses_find_transcript(mock_cls):
    es = _make_transcript("es", False, _SNIPPETS)
    tl = _transcript_list([es])
    tl.find_transcript.return_value = es
    mock_cls.return_value.list.return_value = tl
    assert fetch("vid", lang="es") == _EXPECTED
    tl.find_transcript.assert_called_once_with(["es"])


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_returns_none_when_lang_not_found(mock_cls):
    from youtube_transcript_api._errors import NoTranscriptFound
    tl = _transcript_list([])
    tl.find_transcript.side_effect = NoTranscriptFound("vid", ["es"], MagicMock())
    mock_cls.return_value.list.return_value = tl
    assert fetch("vid", lang="es") is None


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_returns_none_when_no_transcripts(mock_cls):
    mock_cls.return_value.list.return_value = _transcript_list([])
    assert fetch("vid", lang=None) is None


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_returns_none_on_transcripts_disabled(mock_cls):
    from youtube_transcript_api._errors import TranscriptsDisabled
    mock_cls.return_value.list.side_effect = TranscriptsDisabled("vid")
    assert fetch("vid", lang=None) is None


@patch("youtubetranscript.captions.YouTubeTranscriptApi")
def test_fetch_propagates_ip_block(mock_cls):
    """IP blocks must surface so the pipeline can switch backends."""
    from youtube_transcript_api._errors import RequestBlocked
    mock_cls.return_value.list.side_effect = RequestBlocked("vid")
    with pytest.raises(RequestBlocked):
        fetch("vid", lang=None)
