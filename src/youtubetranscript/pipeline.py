"""Orchestrate the full transcript pipeline."""

import os
import shutil
import sys
import tempfile

from youtubetranscript import metadata, captions, downloader, transcriber, formatter, writer, gemini

BACKENDS = ("auto", "local", "gemini")


def _local_segments(url: str, lang: str | None, model: str) -> tuple[str, list[dict]]:
    """Return ``(title, segments)`` from captions, or local Whisper transcription."""
    meta = metadata.fetch(url)
    video_id = meta["video_id"]
    title = meta["title"]

    segments = captions.fetch(video_id, lang)

    tmp_dir: str | None = None
    try:
        if segments is None:
            tmp_dir = tempfile.mkdtemp()
            audio_file = downloader.download(url, tmp_dir=tmp_dir)
            segments = transcriber.transcribe(audio_file, lang=lang, model=model)
    finally:
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    return title, segments


def _gemini_segments(url: str, lang: str | None, gemini_model: str) -> tuple[str, list[dict]]:
    """Return ``(title, segments)`` via oEmbed and Gemini, without yt-dlp."""
    video_id = metadata.parse_video_id(url)
    canonical = f"https://www.youtube.com/watch?v={video_id}"
    title = metadata.fetch_oembed_title(video_id)
    segments = gemini.transcribe(canonical, lang=lang, model=gemini_model)
    return title, segments


def run(
    url: str,
    timestamps: bool = False,
    output: str | None = None,
    lang: str | None = None,
    model: str = "base",
    backend: str = "auto",
    gemini_model: str = gemini.DEFAULT_MODEL,
) -> str:
    """Fetch or transcribe a YouTube video and save the transcript.

    Steps:
      1. Acquire segments with the selected backend:
         - ``local``: fetch metadata via yt-dlp, try existing captions, else
           download audio and transcribe with Whisper.
         - ``gemini``: resolve the title via oEmbed and transcribe with Gemini.
         - ``auto``: try ``local``; if it raises and ``GEMINI_API_KEY`` is
           set, fall back to ``gemini``, otherwise re-raise.
      2. Format the segments.
      3. Write the result to a file.

    Args:
        url: YouTube video URL.
        timestamps: Whether to include [MM:SS] timestamps in the output.
        output: Override output file path/name.  Defaults to the video title.
        lang: BCP-47 language code for captions / transcription.
        model: Whisper model size to use when transcribing locally.
        backend: One of ``"auto"``, ``"local"`` or ``"gemini"``.
        gemini_model: Gemini model name for the ``gemini`` backend.

    Returns:
        Path of the written transcript file.

    Raises:
        ValueError: for an unknown *backend*.
    """
    if backend not in BACKENDS:
        raise ValueError(f"Unknown backend {backend!r}; expected one of {', '.join(BACKENDS)}")

    if backend == "gemini":
        title, segments = _gemini_segments(url, lang, gemini_model)
    elif backend == "local":
        title, segments = _local_segments(url, lang, model)
    else:
        try:
            title, segments = _local_segments(url, lang, model)
        except Exception as exc:
            if not os.environ.get("GEMINI_API_KEY"):
                raise
            print(
                f"local path failed ({type(exc).__name__}: {str(exc)[:120]}); "
                "falling back to Gemini",
                file=sys.stderr,
            )
            title, segments = _gemini_segments(url, lang, gemini_model)

    text = formatter.format(segments, timestamps)
    filepath = writer.write(text, output or title)
    return filepath
