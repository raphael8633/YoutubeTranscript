"""Fetch video metadata (title, id) via yt-dlp, or without it.

``parse_video_id`` and ``fetch_oembed_title`` avoid yt-dlp so they keep
working from cloud IPs that YouTube blocks.
"""

import json
import os
import re
import urllib.parse
import urllib.request

import yt_dlp

_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
_YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
_PATH_PREFIXES = ("shorts", "embed", "live", "v")
_OEMBED = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
_TIMEOUT = 15  # seconds


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
    cookie_path = os.environ.get("YT_COOKIES")
    if cookie_path:
        opts["cookiefile"] = cookie_path
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {"title": info["title"], "video_id": info["id"]}


def parse_video_id(url_or_id: str) -> str:
    """Extract the 11-character video ID from a YouTube URL or bare ID.

    Supports ``watch?v=``, ``youtu.be/``, ``shorts/``, ``embed/`` and
    ``live/`` URLs on the www, mobile and bare domains.

    Raises:
        ValueError: when no video ID can be found.
    """
    value = url_or_id.strip()
    if _ID.match(value):
        return value

    parsed = urllib.parse.urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.hostname or "").lower()
    parts = [p for p in parsed.path.split("/") if p]
    candidate = None
    if host == "youtu.be" and parts:
        candidate = parts[0]
    elif host in _YOUTUBE_HOSTS:
        if parsed.path == "/watch":
            candidate = urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in _PATH_PREFIXES:
            candidate = parts[1]

    if candidate and _ID.match(candidate):
        return candidate
    raise ValueError(f"Not a YouTube video URL or ID: {url_or_id}")


def _get_json(url: str) -> dict:
    """GET *url* and decode the JSON response."""
    with urllib.request.urlopen(url, timeout=_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_oembed_title(video_id: str) -> str:
    """Return the video title from YouTube's oEmbed endpoint.

    Falls back to *video_id* on any error, since the title only names the
    output file.
    """
    try:
        return _get_json(_OEMBED.format(video_id=video_id))["title"]
    except Exception:  # noqa: BLE001
        return video_id
