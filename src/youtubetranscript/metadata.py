"""Fetch video metadata (title, id) via yt-dlp."""

import yt_dlp


def fetch(url: str) -> dict:
    """Return basic metadata for *url*.

    Returns:
        dict with keys ``title`` (str) and ``video_id`` (str).

    Raises:
        Exception: propagated from yt-dlp on network / URL errors.
    """
    opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {"title": info["title"], "video_id": info["id"]}
