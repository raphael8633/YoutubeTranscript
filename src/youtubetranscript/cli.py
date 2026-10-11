"""Command-line interface for youtubetranscript."""

import argparse
import sys

from youtubetranscript import gemini, pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="youtubetranscript",
        description="Save a transcript for a YouTube video.",
    )
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "--timestamps",
        action="store_true",
        default=False,
        help="Include [MM:SS] timestamps in output (default: off)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Override output filename (default: video title)",
    )
    parser.add_argument(
        "--lang",
        metavar="CODE",
        default=None,
        help="Language code e.g. en, es, fr (default: auto-detect)",
    )
    parser.add_argument(
        "--model",
        metavar="MODEL",
        default="base",
        help="Whisper model: tiny, base, small, medium, large (default: base)",
    )
    parser.add_argument(
        "--backend",
        choices=pipeline.BACKENDS,
        default="auto",
        help=(
            "Transcript source: auto = local captions/Whisper first, Gemini "
            "fallback when blocked and GEMINI_API_KEY is set; local = "
            "captions/Whisper only; gemini = Gemini only (default: auto)"
        ),
    )
    parser.add_argument(
        "--gemini-model",
        metavar="MODEL",
        default=gemini.DEFAULT_MODEL,
        help=f"Gemini model for the gemini backend (default: {gemini.DEFAULT_MODEL})",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        filepath = pipeline.run(
            url=args.url,
            timestamps=args.timestamps,
            output=args.output,
            lang=args.lang,
            model=args.model,
            backend=args.backend,
            gemini_model=args.gemini_model,
        )
        print(f"Saved: {filepath}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
