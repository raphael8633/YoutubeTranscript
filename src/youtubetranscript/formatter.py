"""Format transcript segments as plain text or timestamped text."""


def format(segments: list[dict], timestamps: bool = False) -> str:
    """Convert a list of segments to a formatted string.

    Args:
        segments: List of dicts with 'text' (str) and 'start' (float, seconds).
        timestamps: If True, prefix each line with [MM:SS].

    Returns:
        Formatted transcript string.
    """
    if not segments:
        return ""

    lines = []
    for seg in segments:
        text = seg["text"]
        if timestamps:
            total_seconds = int(seg["start"])
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            lines.append(f"[{minutes:02d}:{seconds:02d}] {text}")
        else:
            lines.append(text)

    return "\n".join(lines)
