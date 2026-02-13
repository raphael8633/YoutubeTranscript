"""Orchestrate the full transcript pipeline."""

import os
import shutil
import tempfile

from youtubetranscript import metadata, captions, downloader, transcriber, formatter, writer


def run(
    url: str,
    timestamps: bool = False,
    output: str | None = None,
    lang: str | None = None,
    model: str = "base",
) -> str:
    """Fetch or transcribe a YouTube video and save the transcript.

    Steps:
      1. Fetch video metadata (title, video_id).
      2. Try to fetch existing captions.
      3. If no captions: download audio and transcribe locally.
      4. Format the segments.
      5. Write the result to a file.

    Args:
        url: YouTube video URL.
        timestamps: Whether to include [MM:SS] timestamps in the output.
        output: Override output file path/name.  Defaults to the video title.
        lang: BCP-47 language code for captions / transcription.
        model: Whisper model size to use when transcribing locally.

    Returns:
        Path of the written transcript file.
    """
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

    text = formatter.format(segments, timestamps)
    filepath = writer.write(text, output or title)
    return filepath
