"""Write transcript text to a file."""

import re


_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _sanitize(name: str) -> str:
    """Replace characters that are invalid in file names."""
    return _INVALID_CHARS.sub("_", name).strip()


def write(text: str, output: str) -> str:
    """Write *text* to *output* and return the resolved file path.

    Args:
        text: The transcript content.
        output: Desired output path or video title.  If the value looks like an
                existing directory or an absolute path its directory is kept
                intact; otherwise it is treated as a bare file name and
                characters invalid on Windows/Linux are replaced with
                underscores.  A ``.txt`` extension is added when missing.

    Returns:
        Absolute path of the file that was written.
    """
    import os

    if os.path.isabs(output):
        # Explicit absolute path — trust the caller entirely.
        name = output
    else:
        # Treat as a video title or relative name; sanitize all invalid chars.
        name = _sanitize(output)

    if not os.path.splitext(name)[1]:
        name += ".txt"

    filepath = os.path.abspath(name)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(text)
    return filepath
