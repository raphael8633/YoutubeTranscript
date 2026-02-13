"""Fetch existing YouTube captions via youtube-transcript-api."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled


def fetch(video_id: str, lang: str | None) -> list[dict] | None:
    """Try to retrieve captions for *video_id*.

    Args:
        video_id: YouTube video ID (not the full URL).
        lang: BCP-47 language code (e.g. ``"en"``, ``"es"``).  Defaults to
              ``"en"`` when ``None``.

    Returns:
        List of ``{"text": str, "start": float}`` dicts, or ``None`` if no
        captions are available.
    """
    language = lang or "en"
    api = YouTubeTranscriptApi()
    try:
        transcript = api.fetch(video_id, languages=[language])
    except (NoTranscriptFound, TranscriptsDisabled):
        return None

    return [{"text": snip.text, "start": snip.start} for snip in transcript]
