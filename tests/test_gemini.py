import pytest
from unittest.mock import patch
from youtubetranscript import gemini
from youtubetranscript.gemini import GeminiError, parse_lines, transcribe


URL = "https://www.youtube.com/watch?v=abc123"


def _response(text: str, finish: str = "STOP") -> dict:
    return {"candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": finish}]}


# --- parse_lines -----------------------------------------------------------

def test_parse_lines_hh_mm_ss_with_padding_space():
    text = "[ 00:00:00] Hello there.\n[00:01:05] Second line."
    assert parse_lines(text, offset=0) == [
        {"text": "Hello there.", "start": 0.0},
        {"text": "Second line.", "start": 65.0},
    ]


def test_parse_lines_mm_ss():
    assert parse_lines("[02:03] Hi", offset=0) == [{"text": "Hi", "start": 123.0}]


def test_parse_lines_adds_clip_offset():
    # Gemini timestamps are relative to the clip start, not the full video.
    assert parse_lines("[00:00:07] Hi", offset=600) == [{"text": "Hi", "start": 607.0}]


def test_parse_lines_joins_untimestamped_continuation_lines():
    text = "[00:00:01] First part\nsecond part\n\n[00:00:09] Next"
    assert parse_lines(text, offset=0) == [
        {"text": "First part second part", "start": 1.0},
        {"text": "Next", "start": 9.0},
    ]


def test_parse_lines_leading_untimestamped_text_starts_at_offset():
    assert parse_lines("Intro words\n[00:00:04] Then", offset=30) == [
        {"text": "Intro words", "start": 30.0},
        {"text": "Then", "start": 34.0},
    ]


def test_parse_lines_strips_code_fences():
    text = "```\n[00:00:01] Hi\n```"
    assert parse_lines(text, offset=0) == [{"text": "Hi", "start": 1.0}]


# --- transcribe ------------------------------------------------------------

def test_transcribe_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(GeminiError, match="GEMINI_API_KEY"):
        transcribe(URL, lang=None)


@patch("youtubetranscript.gemini._post")
def test_transcribe_single_request(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    mock_post.return_value = _response("[00:00:00] Hello\n[00:00:03] World")
    assert transcribe(URL, lang=None) == [
        {"text": "Hello", "start": 0.0},
        {"text": "World", "start": 3.0},
    ]
    model, body, key = mock_post.call_args[0]
    assert model == gemini.DEFAULT_MODEL
    assert key == "k"
    part = body["contents"][0]["parts"][0]
    assert part["file_data"]["file_uri"] == URL
    assert "video_metadata" not in part  # first request covers the whole video


@patch("youtubetranscript.gemini._post")
def test_transcribe_mentions_lang_in_prompt(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    mock_post.return_value = _response("[00:00:00] 你好")
    transcribe(URL, lang="zh-TW")
    _model, body, _key = mock_post.call_args[0]
    prompt = body["contents"][0]["parts"][1]["text"]
    assert "zh-TW" in prompt


@patch("youtubetranscript.gemini._post")
def test_transcribe_uses_given_model(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    mock_post.return_value = _response("[00:00:00] Hi")
    transcribe(URL, lang=None, model="gemini-3-flash-preview")
    assert mock_post.call_args[0][0] == "gemini-3-flash-preview"


@patch("youtubetranscript.gemini._post")
def test_transcribe_continues_after_max_tokens(mock_post, monkeypatch):
    """A truncated response resumes from the last (possibly cut) segment."""
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    mock_post.side_effect = [
        _response("[00:00:00] A\n[00:10:00] B\n[00:20:00] C cut mid-sen", "MAX_TOKENS"),
        # second request is clipped at 1200 s; timestamps relative to that
        _response("[00:00:00] C complete.\n[00:05:00] D"),
    ]
    assert transcribe(URL, lang=None) == [
        {"text": "A", "start": 0.0},
        {"text": "B", "start": 600.0},
        {"text": "C complete.", "start": 1200.0},
        {"text": "D", "start": 1500.0},
    ]
    second_part = mock_post.call_args_list[1][0][1]["contents"][0]["parts"][0]
    assert second_part["video_metadata"] == {"start_offset": "1200s"}


@patch("youtubetranscript.gemini._post")
def test_transcribe_raises_when_truncation_makes_no_progress(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    mock_post.return_value = _response("[00:00:00] only one cut seg", "MAX_TOKENS")
    with pytest.raises(GeminiError, match="truncated"):
        transcribe(URL, lang=None)


@patch("youtubetranscript.gemini._post")
def test_transcribe_raises_on_empty_candidates(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    mock_post.return_value = {"promptFeedback": {"blockReason": "OTHER"}}
    with pytest.raises(GeminiError):
        transcribe(URL, lang=None)
