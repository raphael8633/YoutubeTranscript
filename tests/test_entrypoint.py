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
