# YoutubeTranscript

CLI tool that takes a YouTube URL and saves a transcript to a `.txt` file.
Works even when the video has no captions — falls back to local Whisper transcription.

## Quick start

```bash
# requires: Python 3.12+, uv
uv sync                            # installs dependencies + package (editable)
uv run python main.py <youtube-url>
```

**Options:**

```
uv run python main.py <url> [--timestamps] [--output FILE] [--lang CODE] [--model MODEL]

  --timestamps     prefix each line with [MM:SS]
  --output FILE    override output filename  (default: video title)
  --lang CODE      e.g. en, es, fr           (default: auto-detect)
  --model MODEL    tiny | base | small | medium | large  (default: base)
```

**Example:**

```bash
uv run python main.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --timestamps --model medium
# saves: Rick Astley - Never Gonna Give You Up.txt
```

## New device setup

```bash
git clone <repo-url>
cd YoutubeTranscript

# install uv (if not already)
# Windows:  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

uv sync          # installs Python 3.12 + all dependencies
uv run pytest    # verify everything works
```

> `faster-whisper` downloads Whisper model weights on first use (~150 MB for `base`).
> No GPU required — runs on CPU with `int8` quantisation.

## Architecture

```
src/youtubetranscript/
  pipeline.py     # orchestrates all steps; stable public API
  metadata.py     # fetch title + video_id via yt-dlp
  captions.py     # fetch existing captions (youtube-transcript-api)
  downloader.py   # download audio via yt-dlp  (used only when no captions)
  transcriber.py  # local transcription via faster-whisper
  formatter.py    # render segments as plain text or [MM:SS] timestamped
  writer.py       # save formatted string to .txt file
  cli.py          # argparse entry point
main.py           # calls cli.main()
tests/            # 27 unit tests, all modules mocked
```

**Pipeline flow:**

```
pipeline.run(url, timestamps, output, lang, model)
  1. metadata.fetch(url)              → title, video_id
  2. captions.fetch(video_id, lang)   → segments  (or None)
  3. if None:
       downloader.download(url)       → audio file  (temp, always cleaned up)
       transcriber.transcribe(audio)  → segments
  4. formatter.format(segments)       → string
  5. writer.write(string, output)     → filepath
```

## Dependencies

| Package | Role |
|---|---|
| `yt-dlp` | metadata + audio download |
| `youtube-transcript-api` | fast caption fetch |
| `faster-whisper` | local CPU transcription |

## Tests

```bash
uv run pytest          # run all 27 tests
uv run pytest -v       # verbose
```

## Future web layer

`pipeline.run()` is the stable interface. A Flask/FastAPI app would call it directly — no changes to pipeline or below required.
