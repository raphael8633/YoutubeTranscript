import os
import pytest
from unittest.mock import patch, MagicMock
from youtubetranscript.downloader import download


@patch("youtubetranscript.downloader.yt_dlp.YoutubeDL")
def test_download_returns_filepath(mock_ydl_cls, tmp_path):
    """download() should return the path of the audio file written by yt-dlp."""
    expected = str(tmp_path / "audio.m4a")

    ydl = MagicMock()
    ydl.__enter__ = MagicMock(return_value=ydl)
    ydl.__exit__ = MagicMock(return_value=False)
    # Simulate yt-dlp writing the file and returning info
    ydl.download = MagicMock(return_value=0)
    ydl.prepare_filename = MagicMock(return_value=expected)
    ydl.extract_info = MagicMock(return_value={"requested_downloads": [{"filepath": expected}]})
    mock_ydl_cls.return_value = ydl

    result = download("https://youtube.com/watch?v=dQw4w9WgXcQ", tmp_dir=str(tmp_path))
    assert result == expected


@patch("youtubetranscript.downloader.yt_dlp.YoutubeDL")
def test_download_passes_output_template(mock_ydl_cls, tmp_path):
    """Output template should be set to tmp_dir."""
    ydl = MagicMock()
    ydl.__enter__ = MagicMock(return_value=ydl)
    ydl.__exit__ = MagicMock(return_value=False)
    ydl.extract_info = MagicMock(return_value={"requested_downloads": [{"filepath": str(tmp_path / "a.m4a")}]})
    mock_ydl_cls.return_value = ydl

    download("https://youtube.com/watch?v=dQw4w9WgXcQ", tmp_dir=str(tmp_path))

    call_opts = mock_ydl_cls.call_args[0][0]
    assert str(tmp_path) in call_opts["outtmpl"]


@patch("youtubetranscript.downloader.yt_dlp.YoutubeDL")
def test_download_raises_on_failure(mock_ydl_cls, tmp_path):
    ydl = MagicMock()
    ydl.__enter__ = MagicMock(return_value=ydl)
    ydl.__exit__ = MagicMock(return_value=False)
    ydl.extract_info = MagicMock(side_effect=Exception("download error"))
    mock_ydl_cls.return_value = ydl

    with pytest.raises(Exception, match="download error"):
        download("https://youtube.com/watch?v=bad", tmp_dir=str(tmp_path))


@patch("youtubetranscript.downloader.yt_dlp.YoutubeDL")
def test_download_uses_cookiefile_from_env(mock_ydl_cls, tmp_path, monkeypatch):
    """When YT_COOKIES is set, yt-dlp opts should include cookiefile."""
    cookie_path = str(tmp_path / "cookies.txt")
    monkeypatch.setenv("YT_COOKIES", cookie_path)

    ydl = MagicMock()
    ydl.__enter__ = MagicMock(return_value=ydl)
    ydl.__exit__ = MagicMock(return_value=False)
    ydl.extract_info = MagicMock(return_value={"requested_downloads": [{"filepath": str(tmp_path / "a.m4a")}]})
    mock_ydl_cls.return_value = ydl

    download("https://youtube.com/watch?v=dQw4w9WgXcQ", tmp_dir=str(tmp_path))

    call_opts = mock_ydl_cls.call_args[0][0]
    assert call_opts["cookiefile"] == cookie_path


@patch("youtubetranscript.downloader.yt_dlp.YoutubeDL")
def test_download_no_cookiefile_without_env(mock_ydl_cls, tmp_path, monkeypatch):
    """When YT_COOKIES is not set, cookiefile should not appear in opts."""
    monkeypatch.delenv("YT_COOKIES", raising=False)

    ydl = MagicMock()
    ydl.__enter__ = MagicMock(return_value=ydl)
    ydl.__exit__ = MagicMock(return_value=False)
    ydl.extract_info = MagicMock(return_value={"requested_downloads": [{"filepath": str(tmp_path / "a.m4a")}]})
    mock_ydl_cls.return_value = ydl

    download("https://youtube.com/watch?v=dQw4w9WgXcQ", tmp_dir=str(tmp_path))

    call_opts = mock_ydl_cls.call_args[0][0]
    assert "cookiefile" not in call_opts
