# YoutubeTranscript

CLI tool that takes a YouTube URL and saves a transcript to a `.txt` file.
Works even when the video has no captions — falls back to local Whisper transcription,
or to Gemini (which fetches the video server-side) when YouTube blocks the host IP.

## Quick start

```bash
# requires: Python 3.12+, uv
uv sync                            # installs dependencies + package (editable)
uv run python main.py <youtube-url>
```

**Options:**

```
uv run python main.py <url> [--timestamps] [--output FILE] [--lang CODE] [--model MODEL]
                             [--backend auto|local|gemini] [--gemini-model NAME]

  --timestamps         prefix each line with [MM:SS]
  --output FILE        override output filename  (default: video title)
  --lang CODE          e.g. en, es, zh-TW        (default: first available captions / auto-detect)
  --model MODEL        Whisper size: tiny | base | small | medium | large  (default: base)
  --backend            auto (default): local captions → Whisper; on any local failure,
                         fall back to Gemini if GEMINI_API_KEY is set
                       local:  never call Gemini
                       gemini: skip yt-dlp / captions entirely (fastest on cloud servers)
  --gemini-model NAME  default: gemini-2.5-flash
```

**Example:**

```bash
uv run python main.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --timestamps --model medium
# saves: Rick Astley - Never Gonna Give You Up.txt
```

## Backends

| Path | Needs | Text source | When it works |
|---|---|---|---|
| captions (`youtube-transcript-api`) | nothing | YouTube's own captions, exact | home/residential IP |
| Whisper (`yt-dlp` audio + `faster-whisper`) | CPU, model download | local ASR | home IP, or cloud IP with `YT_COOKIES` |
| Gemini (`--backend gemini`) | `GEMINI_API_KEY` | Gemini ASR of the video, public videos only | anywhere, including blocked cloud IPs |

Gemini cost scales with video length (~100 input tokens per second at low media resolution, ≈360k per hour). Long outputs that hit the model's token limit are resumed automatically from the last timestamp via clip offsets.

## YouTube authentication

YouTube may block downloads with a bot-detection challenge. To fix this, set the `YT_COOKIES` environment variable pointing to a Netscape-format cookies file:

```bash
export YT_COOKIES=~/cookies.txt          # add to .bashrc / .zshrc for persistence
uv run python main.py <url>
```

To export cookies from your browser, use a browser extension like [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) or the `yt-dlp --cookies-from-browser` command.

> **JS runtime:** yt-dlp works best with [deno](https://deno.land) installed (`curl -fsSL https://deno.land/install.sh | sh`).

> **Cloud servers:** YouTube blocks datacenter IPs (OVH, DigitalOcean, AWS, …) for both captions and downloads. Use `--backend gemini` there, or run locally. See [docs/cloud-ip-troubleshooting.md](docs/cloud-ip-troubleshooting.md).

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
  pipeline.py     # orchestrates all steps + backend selection; stable public API
  metadata.py     # title + video_id via yt-dlp; URL parsing + oEmbed title (no yt-dlp)
  captions.py     # fetch existing captions (youtube-transcript-api)
  gemini.py       # transcribe a YouTube URL via Gemini REST (stdlib only)
  downloader.py   # download audio via yt-dlp  (used only when no captions)
  transcriber.py  # local transcription via faster-whisper
  formatter.py    # render segments as plain text or [MM:SS] timestamped
  writer.py       # save formatted string to .txt file
  cli.py          # argparse entry point
main.py           # calls cli.main()
tests/            # unit tests, all modules mocked
```

**Pipeline flow:**

```
pipeline.run(url, timestamps, output, lang, model, backend, gemini_model)
  local path (backend auto|local):
    1. metadata.fetch(url)              → title, video_id
    2. captions.fetch(video_id, lang)   → segments  (or None)
    3. if None:
         downloader.download(url)       → audio file  (temp, always cleaned up)
         transcriber.transcribe(audio)  → segments
  gemini path (backend gemini, or auto after a local failure with GEMINI_API_KEY set):
    1. metadata.parse_video_id(url) + metadata.fetch_oembed_title(id)
    2. gemini.transcribe(canonical_url) → segments
  then:
    formatter.format(segments)          → string
    writer.write(string, output)        → filepath
```

## Dependencies

| Package | Role |
|---|---|
| `yt-dlp` | metadata + audio download |
| `youtube-transcript-api` | fast caption fetch |
| `faster-whisper` | local CPU transcription |

Gemini and oEmbed calls use the standard library (`urllib`); no extra package.

## Tests

```bash
uv run pytest          # run all tests
uv run pytest -v       # verbose
```

## Future web layer

`pipeline.run()` is the stable interface. A Flask/FastAPI app would call it directly — no changes to pipeline or below required.
