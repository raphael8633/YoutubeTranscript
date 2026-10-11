"""Fetch existing YouTube captions via youtube-transcript-api."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled


def fetch(video_id: str, lang: str | None) -> list[dict] | None:
    """Try to retrieve captions for *video_id*.

    Args:
        video_id: YouTube video ID (not the full URL).
        lang: BCP-47 language code (e.g. ``"en"``, ``"es"``).  When ``None``,
              the first available transcript is used (manual before
              auto-generated), whatever its language.

    Returns:
        List of ``{"text": str, "start": float}`` dicts, or ``None`` if no
        matching captions are available.

    Raises:
        Exception: request errors such as ``RequestBlocked`` / ``IpBlocked``
            propagate so the caller can switch backends.
    """
    api = YouTubeTranscriptApi()
    try:
        transcripts = api.list(video_id)
    except TranscriptsDisabled:
        return None

    if lang:
        try:
            transcript = transcripts.find_transcript([lang])
        except NoTranscriptFound:
            return None
    else:
        transcript = next(iter(transcripts), None)
        if transcript is None:
            return None

    return [{"text": snip.text, "start": snip.start} for snip in transcript.fetch()]
