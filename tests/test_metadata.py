import pytest
from unittest.mock import patch, MagicMock
from youtubetranscript.metadata import fetch


def _make_ydl(info: dict):
    """Return a mock yt_dlp.YoutubeDL context manager yielding *info*."""
    ydl = MagicMock()
    ydl.__enter__ = MagicMock(return_value=ydl)
    ydl.__exit__ = MagicMock(return_value=False)
    ydl.extract_info = MagicMock(return_value=info)
    return ydl


@patch("youtubetranscript.metadata.yt_dlp.YoutubeDL")
def test_fetch_returns_title_and_id(mock_ydl_cls):
    mock_ydl_cls.return_value = _make_ydl(
        {"title": "Rick Roll", "id": "dQw4w9WgXcQ"}
    )
    result = fetch("https://youtube.com/watch?v=dQw4w9WgXcQ")
    assert result == {"title": "Rick Roll", "video_id": "dQw4w9WgXcQ"}


@patch("youtubetranscript.metadata.yt_dlp.YoutubeDL")
def test_fetch_raises_on_extraction_failure(mock_ydl_cls):
    ydl = _make_ydl({})
    ydl.extract_info.side_effect = Exception("network error")
    mock_ydl_cls.return_value = ydl
    with pytest.raises(Exception, match="network error"):
        fetch("https://youtube.com/watch?v=bad")
