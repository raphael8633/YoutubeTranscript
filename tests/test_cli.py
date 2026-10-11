from unittest.mock import patch
from youtubetranscript import cli, gemini


@patch("youtubetranscript.cli.pipeline.run", return_value="/out/x.txt")
def test_cli_defaults_to_auto_backend(mock_run):
    cli.main(["https://youtu.be/abc"])
    kwargs = mock_run.call_args.kwargs
    assert kwargs["backend"] == "auto"
    assert kwargs["gemini_model"] == gemini.DEFAULT_MODEL


@patch("youtubetranscript.cli.pipeline.run", return_value="/out/x.txt")
def test_cli_passes_backend_and_gemini_model(mock_run):
    cli.main(["https://youtu.be/abc", "--backend", "gemini", "--gemini-model", "gemini-3-flash-preview"])
    kwargs = mock_run.call_args.kwargs
    assert kwargs["backend"] == "gemini"
    assert kwargs["gemini_model"] == "gemini-3-flash-preview"
