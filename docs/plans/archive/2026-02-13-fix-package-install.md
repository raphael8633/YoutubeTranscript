# Fix Package Installation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `uv run python main.py <url>` work by properly installing the `youtubetranscript` package in editable mode, and update README so new users succeed on first try.

**Architecture:** Add a `[build-system]` table (hatchling) to `pyproject.toml` so `uv sync` installs the package from `src/` as an editable install. pytest already works via `pythonpath = ["src"]`; the gap is that `uv run python …` doesn't get that path injection. README currently omits the required `uv sync` step in Quick Start.

**Tech Stack:** uv, hatchling, Python 3.12, pytest

---

## Background / Root Cause

`pyproject.toml` has no `[build-system]` table. Without it, `uv sync` treats the project as a *dependency-only* workspace and never installs the local package — so `from youtubetranscript.cli import main` works in pytest (because pytest injects `src/`) but fails for every other `uv run python` call.

Fix: add `[build-system]` + `[tool.hatch.build.targets.wheel]` → `uv sync` will editable-install the package into `.venv`. Then verify README Quick Start matches the actual working commands.

---

### Task 1: Write a failing smoke test for `main.py` entry point

**Files:**
- Create: `tests/test_entrypoint.py`

**Step 1: Write the failing test**

```python
# tests/test_entrypoint.py
import subprocess, sys, pathlib

PROJECT_ROOT = str(pathlib.Path(__file__).parent.parent)

def test_main_help_exits_zero():
    """Verify `uv run python main.py --help` exits 0 and prints usage."""
    result = subprocess.run(
        ["uv", "run", "python", "main.py", "--help"],
        capture_output=True, text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0, result.stderr
    assert "usage" in result.stdout.lower(), result.stdout
```

**Step 2: Run test to verify it fails**

```bash
cd /d/dev/YoutubeTranscript && unset VIRTUAL_ENV && uv run pytest tests/test_entrypoint.py -v
```

Expected: **FAIL** — `ModuleNotFoundError: No module named 'youtubetranscript'` visible in stderr.

**Step 3: Commit the failing test**

```bash
git add tests/test_entrypoint.py
git commit -m "test: add failing smoke test for main.py entry point"
```

---

### Task 2: Add build-system to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1: Edit `pyproject.toml`**

Replace the entire file with:

```toml
[project]
name = "youtubetranscript"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "faster-whisper>=1.2.1",
    "youtube-transcript-api>=1.2.4",
    "yt-dlp>=2026.2.4",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/youtubetranscript"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[dependency-groups]
dev = [
    "hatchling>=1.25.0",
    "pytest>=9.0.2",
]
```

**Step 2: Re-sync the environment**

```bash
cd /d/dev/YoutubeTranscript && unset VIRTUAL_ENV && uv sync
```

Expected: output includes installing `youtubetranscript` (editable). No errors.

**Step 3: Verify the package is now installed**

```bash
unset VIRTUAL_ENV && uv run python -c "import youtubetranscript; print('ok')"
```

Expected: prints `ok`.

---

### Task 3: Verify tests pass

**Step 1: Run the new smoke test**

```bash
cd /d/dev/YoutubeTranscript && unset VIRTUAL_ENV && uv run pytest tests/test_entrypoint.py -v
```

Expected: **PASS**.

**Step 2: Run the full test suite**

```bash
unset VIRTUAL_ENV && uv run pytest -v
```

Expected: all 28 tests pass (27 original + 1 new smoke test).

**Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "fix: add build-system so uv sync installs package in editable mode"
```

---

### Task 4: Update README.md Quick Start and New Device Setup

**Files:**
- Modify: `README.md`

The README currently shows:

```bash
uv sync
python main.py <youtube-url>
```

Problems:
1. `python main.py` should be `uv run python main.py` — without `uv run`, the system Python is used and the package isn't found.
2. The New Device Setup section says `uv run pytest` to verify — that's fine, but it doesn't say `uv sync` installs the package itself as an editable install (confusing for new users).

**Step 1: Update Quick Start block in README.md**

Replace:
```markdown
## Quick start

```bash
# requires: Python 3.12+, uv
uv sync
python main.py <youtube-url>
```
```

With:
```markdown
## Quick start

```bash
# requires: Python 3.12+, uv
uv sync                            # installs dependencies + package (editable)
uv run python main.py <youtube-url>
```
```

**Step 2: Update Options block command**

Replace:
```
python main.py <url> [--timestamps] [--output FILE] [--lang CODE] [--model MODEL]
```

With:
```
uv run python main.py <url> [--timestamps] [--output FILE] [--lang CODE] [--model MODEL]
```

**Step 3: Update Example block**

Replace:
```bash
python main.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --timestamps --model medium
```

With:
```bash
uv run python main.py "https://youtube.com/watch?v=dQw4w9WgXcQ" --timestamps --model medium
```

**Step 4: Verify README end-to-end as a new user would**

Run exactly the commands shown in Quick Start:
```bash
cd /d/dev/YoutubeTranscript && unset VIRTUAL_ENV && uv sync && uv run python main.py --help
```

Expected: exit 0, usage printed.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: fix README commands to use 'uv run python' consistently"
```

---

### Task 5: Manual end-to-end smoke run

**Step 1: Run `--help`**

```bash
cd /d/dev/YoutubeTranscript && unset VIRTUAL_ENV && uv run python main.py --help
```

Expected: prints usage with `--timestamps`, `--output`, `--lang`, `--model` options. Exit code 0.

---

## Done

After Task 5:
- `uv run python main.py <youtube-url>` works
- All 28 tests pass
- README Quick Start works verbatim for a new user
