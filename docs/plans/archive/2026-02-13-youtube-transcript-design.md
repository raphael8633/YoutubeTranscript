# YouTube Transcript — Design

## Goal

CLI tool that takes a YouTube URL and saves a transcript to a file. Works even when the video has no captions, by downloading audio and transcribing locally.

---

## Architecture

```
src/
  youtubetranscript/
    cli.py          # argparse entry point
    pipeline.py     # orchestrates all steps; callable by future web layer
    metadata.py     # fetch video title (and other info) via yt-dlp
    captions.py     # try fetching existing captions (youtube-transcript-api)
    downloader.py   # download audio via yt-dlp
    transcriber.py  # transcribe audio via faster-whisper
    formatter.py    # format segments as plain text or [MM:SS] timestamped
    writer.py       # save formatted string to file
tests/
  test_captions.py
  test_downloader.py
  test_transcriber.py
  test_formatter.py
  test_writer.py
  test_pipeline.py
```

`pipeline.py` is the public core — the CLI calls it, and a future web layer can too.

---

## Pipeline Flow

```
pipeline.run(url, timestamps=False, output=None, lang=None, model="base")
  │
  ├─ 1. metadata.fetch(url) → title, video_id
  │
  ├─ 2. captions.fetch(url, lang)
  │      └─ success → segments (list of {text, start})
  │      └─ fail / no captions → None
  │
  ├─ 3. if None:
  │      downloader.download(url) → audio_file (temp file)
  │      transcriber.transcribe(audio_file, lang, model) → segments
  │      [temp audio file deleted in finally block]
  │
  ├─ 4. formatter.format(segments, timestamps) → string
  │
  └─ 5. writer.write(string, output or title) → filepath
```

---

## CLI Interface

```
python main.py <url> [options]

Arguments:
  url                 YouTube URL (required)

Options:
  --timestamps        Include [MM:SS] timestamps in output (default: off)
  --output FILE       Override output filename (default: video title)
  --lang CODE         Language code e.g. en, es, fr (default: auto-detect)
  --model MODEL       Whisper model: tiny, base, small, medium, large
                      (default: base)
```

Example:
```
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ --timestamps --model medium
# saves: Rick Astley - Never Gonna Give You Up.txt
```

---

## Dependencies

```toml
dependencies = [
  "yt-dlp",                  # audio download + metadata + caption availability
  "youtube-transcript-api",  # fast caption fetch when captions exist
  "faster-whisper",          # local audio transcription (same models as Whisper, faster)
]
```

---

## Error Handling

| Failure | Behaviour |
|---|---|
| Invalid / private URL | `yt-dlp` metadata fails → print clear error, exit |
| No audio stream | `yt-dlp` download fails → print error, exit |
| Transcription error | `faster-whisper` fails → print error, clean temp file, exit |
| Output file exists | Overwrite silently |
| No captions + offline | Falls through to local transcription (works once audio downloaded) |

Temp audio files are always cleaned up via `try/finally`, even on failure.

---

## Future Web Layer

`pipeline.run()` is the stable interface. A web app (Flask/FastAPI) would:
1. Accept a URL via HTTP POST
2. Call `pipeline.run(url, ...)` directly
3. Return the transcript text or a download link

No changes to `pipeline.py` or below required.
