"""Download audio from a YouTube URL via yt-dlp."""

import os
import yt_dlp


def download(url: str, tmp_dir: str) -> str:
    """Download the best-available audio from *url* into *tmp_dir*.

    Args:
        url: YouTube video URL.
        tmp_dir: Directory in which to save the audio file.

    Returns:
        Full path of the downloaded audio file.

    Raises:
        Exception: propagated from yt-dlp on network / format errors.
    """
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    filepath = info["requested_downloads"][0]["filepath"]
    return filepath
