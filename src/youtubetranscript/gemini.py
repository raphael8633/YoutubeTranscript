"""Transcribe a YouTube video server-side via the Gemini API.

Gemini accepts a YouTube URL as ``file_data.file_uri`` and fetches the video
itself, so this backend works from cloud IPs where YouTube blocks yt-dlp and
youtube-transcript-api.
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MODEL = "gemini-2.5-flash"

_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_TIMEOUT = 600  # seconds; long videos take minutes to process
_RETRY_STATUSES = {429, 500, 503}
_MAX_ATTEMPTS = 3
_BACKOFF = 5  # seconds, doubled after each failed attempt

_TIMESTAMP = re.compile(
    r"^\[\s*(?:(\d+):)?(\d{1,2}):(\d{1,2}(?:\.\d+)?)\s*\]\s*(.*)$"
)


class GeminiError(RuntimeError):
    """Raised when the Gemini API fails or returns an unusable response."""


def parse_lines(text: str, offset: float) -> list[dict]:
    """Parse ``[HH:MM:SS] text`` lines into transcript segments.

    Args:
        text: Raw model output, one utterance per line.
        offset: Start of the transcribed clip in seconds.  Gemini timestamps
                are relative to the clip, so this is added to each one.

    Returns:
        List of ``{"text": str, "start": float}`` dicts.  Untimestamped lines
        are joined onto the previous segment (or start one at *offset*).
    """
    segments: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("```"):
            continue
        match = _TIMESTAMP.match(line)
        if match:
            hours, minutes, seconds, body = match.groups()
            start = int(hours or 0) * 3600 + int(minutes) * 60 + float(seconds)
            segments.append({"text": body.strip(), "start": float(offset) + start})
        elif segments:
            prev = segments[-1]
            prev["text"] = f"{prev['text']} {line}" if prev["text"] else line
        else:
            segments.append({"text": line, "start": float(offset)})
    return segments


def _api_message(err: urllib.error.HTTPError) -> str:
    """Extract the API error message from an HTTP error body."""
    try:
        payload = json.loads(err.read().decode("utf-8"))
        return payload["error"]["message"]
    except Exception:  # noqa: BLE001
        return err.reason or ""


def _post(model: str, body: dict, key: str) -> dict:
    """POST *body* to ``generateContent`` for *model* and return the JSON reply.

    Retries on HTTP 429/500/503 with exponential backoff.

    Raises:
        GeminiError: on any other HTTP error, or when retries are exhausted.
    """
    url = _ENDPOINT.format(model=urllib.parse.quote(model)) + "?" + urllib.parse.urlencode({"key": key})
    data = json.dumps(body).encode("utf-8")
    delay = _BACKOFF
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        request = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            message = _api_message(err)
            if err.code in _RETRY_STATUSES and attempt < _MAX_ATTEMPTS:
                time.sleep(delay)
                delay *= 2
                continue
            raise GeminiError(f"Gemini API HTTP {err.code} ({model}): {message}") from None
        except urllib.error.URLError as err:
            raise GeminiError(f"Gemini API request failed ({model}): {err.reason}") from None
    raise GeminiError(f"Gemini API request failed ({model})")  # pragma: no cover


def _prompt(lang: str | None) -> str:
    """Build the transcription instruction."""
    prompt = (
        "Transcribe the speech in this video verbatim, in the original spoken "
        "language. Do not translate or summarise. Write one line per sentence "
        "or utterance, each prefixed with its timestamp as [HH:MM:SS]. Output "
        "only the transcript lines."
    )
    if lang:
        prompt += f" The speech language is {lang}."
    return prompt


def _request_body(url: str, prompt: str, start: float | None) -> dict:
    """Build a ``generateContent`` request body, optionally clipped at *start*."""
    video_part: dict = {"file_data": {"file_uri": url}}
    if start is not None:
        video_part["video_metadata"] = {"start_offset": f"{int(start)}s"}
    return {
        "contents": [{"parts": [video_part, {"text": prompt}]}],
        "generationConfig": {"mediaResolution": "MEDIA_RESOLUTION_LOW"},
    }


def _extract(response: dict) -> tuple[str, str | None]:
    """Return ``(text, finishReason)`` from a ``generateContent`` reply."""
    try:
        candidate = response["candidates"][0]
        text = candidate["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        reason = (response.get("promptFeedback") or {}).get("blockReason")
        detail = f" (blockReason: {reason})" if reason else ""
        raise GeminiError(f"Gemini returned no transcript text{detail}") from None
    return text, candidate.get("finishReason")


def transcribe(
    url: str,
    lang: str | None,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
) -> list[dict]:
    """Transcribe the YouTube video at *url* with Gemini.

    When a response hits the output token limit, the last (possibly cut)
    segment is discarded and a follow-up request resumes from its timestamp.

    Args:
        url: Canonical YouTube watch URL.
        lang: Language code of the speech, or ``None`` to let Gemini detect it.
        model: Gemini model name.
        api_key: API key; defaults to the ``GEMINI_API_KEY`` environment variable.

    Returns:
        List of ``{"text": str, "start": float}`` dicts.

    Raises:
        GeminiError: when no key is configured, the API fails, or truncated
            output cannot make progress.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise GeminiError("Gemini backend requires GEMINI_API_KEY to be set")

    prompt = _prompt(lang)
    segments: list[dict] = []
    offset = 0.0
    start: float | None = None
    while True:
        text, finish = _extract(_post(model, _request_body(url, prompt, start), key))
        parsed = parse_lines(text, offset)
        if finish != "MAX_TOKENS":
            segments.extend(parsed)
            return segments

        if len(parsed) < 2:
            raise GeminiError("Gemini output was truncated before any complete segment")
        dropped = parsed.pop()
        # The clip starts at whole seconds, so align the offset with it.
        next_offset = float(int(dropped["start"]))
        if next_offset <= offset:
            raise GeminiError("Gemini output was truncated without advancing the timestamp")
        segments.extend(parsed)
        offset = start = next_offset
