import pytest
from youtubetranscript.formatter import format


SEGMENTS = [
    {"text": "Hello world", "start": 0.0},
    {"text": "This is a test", "start": 75.5},
    {"text": "Goodbye", "start": 3661.0},
]


def test_plain_text_joins_with_newlines():
    result = format(SEGMENTS, timestamps=False)
    assert result == "Hello world\nThis is a test\nGoodbye"


def test_timestamps_prefix_each_line():
    result = format(SEGMENTS, timestamps=True)
    lines = result.splitlines()
    assert lines[0] == "[00:00] Hello world"
    assert lines[1] == "[01:15] This is a test"
    assert lines[2] == "[61:01] Goodbye"


def test_empty_segments_returns_empty_string():
    assert format([], timestamps=False) == ""
    assert format([], timestamps=True) == ""


def test_single_segment_no_trailing_newline():
    result = format([{"text": "Only one", "start": 5.0}], timestamps=False)
    assert result == "Only one"
    assert not result.endswith("\n")
