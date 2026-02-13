"""Transcribe an audio file locally using faster-whisper."""

from faster_whisper import WhisperModel


def transcribe(audio_file: str, lang: str | None, model: str = "base") -> list[dict]:
    """Transcribe *audio_file* and return segments.

    Args:
        audio_file: Path to the audio file to transcribe.
        lang: BCP-47 language code, or ``None`` for auto-detection.
        model: Whisper model size (``"tiny"``, ``"base"``, ``"small"``, etc.).

    Returns:
        List of ``{"text": str, "start": float}`` dicts.
    """
    whisper = WhisperModel(model, device="cpu", compute_type="int8")
    kwargs = {}
    if lang:
        kwargs["language"] = lang
    segments, _info = whisper.transcribe(audio_file, **kwargs)
    return [{"text": seg.text.strip(), "start": seg.start} for seg in segments]
