import pytest
from unittest.mock import patch, MagicMock, call
from youtubetranscript import pipeline


URL = "https://youtube.com/watch?v=dQw4w9WgXcQ"
SEGMENTS = [{"text": "Hello", "start": 0.0}]
METADATA = {"title": "Rick Roll", "video_id": "dQw4w9WgXcQ"}


def _patch_all(meta=METADATA, caps=SEGMENTS, download_path="/tmp/a.m4a",
               transcribe_segs=SEGMENTS, formatted="Hello", written="/out/Rick Roll.txt"):
    return [
        patch("youtubetranscript.pipeline.metadata.fetch", return_value=meta),
        patch("youtubetranscript.pipeline.captions.fetch", return_value=caps),
        patch("youtubetranscript.pipeline.downloader.download", return_value=download_path),
        patch("youtubetranscript.pipeline.transcriber.transcribe", return_value=transcribe_segs),
        patch("youtubetranscript.pipeline.formatter.format", return_value=formatted),
        patch("youtubetranscript.pipeline.writer.write", return_value=written),
        patch("youtubetranscript.pipeline.tempfile.mkdtemp", return_value="/tmp/ytdl_test"),
        patch("youtubetranscript.pipeline.shutil.rmtree"),
        patch("youtubetranscript.pipeline.os.path.exists", return_value=True),
    ]


def test_pipeline_uses_captions_when_available():
    patches = _patch_all(caps=SEGMENTS)
    with patches[0], patches[1] as mock_caps, patches[2] as mock_dl, patches[3], \
         patches[4], patches[5], patches[6], patches[7], patches[8]:
        pipeline.run(URL)
        mock_caps.assert_called_once_with("dQw4w9WgXcQ", None)
        mock_dl.assert_not_called()


def test_pipeline_falls_back_to_download_when_no_captions():
    patches = _patch_all(caps=None)
    with patches[0], patches[1], patches[2] as mock_dl, patches[3] as mock_tr, \
         patches[4], patches[5], patches[6], patches[7], patches[8]:
        pipeline.run(URL)
        mock_dl.assert_called_once()
        mock_tr.assert_called_once()


def test_pipeline_passes_timestamps_to_formatter():
    patches = _patch_all()
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4] as mock_fmt, patches[5], patches[6], patches[7], patches[8]:
        pipeline.run(URL, timestamps=True)
        mock_fmt.assert_called_once_with(SEGMENTS, True)


def test_pipeline_uses_output_arg_for_writer():
    patches = _patch_all()
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4], patches[5] as mock_wr, patches[6], patches[7], patches[8]:
        pipeline.run(URL, output="my_file.txt")
        mock_wr.assert_called_once_with("Hello", "my_file.txt")


def test_pipeline_uses_title_when_no_output():
    patches = _patch_all()
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4], patches[5] as mock_wr, patches[6], patches[7], patches[8]:
        pipeline.run(URL, output=None)
        mock_wr.assert_called_once_with("Hello", "Rick Roll")


def test_pipeline_cleans_up_temp_dir_on_success():
    patches = _patch_all(caps=None)
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4], patches[5], patches[6] as mock_mkdtemp, \
         patches[7] as mock_rmtree, patches[8]:
        pipeline.run(URL)
        mock_rmtree.assert_called_once_with("/tmp/ytdl_test", ignore_errors=True)


def test_pipeline_cleans_up_temp_dir_on_failure():
    patches = _patch_all(caps=None)
    with patches[0], patches[1], patches[2], patches[3] as mock_tr, \
         patches[4], patches[5], patches[6] as mock_mkdtemp, \
         patches[7] as mock_rmtree, patches[8]:
        mock_tr.side_effect = RuntimeError("transcription failed")
        with pytest.raises(RuntimeError):
            pipeline.run(URL)
        mock_rmtree.assert_called_once_with("/tmp/ytdl_test", ignore_errors=True)


# --- backend selection -----------------------------------------------------

GEMINI_SEGS = [{"text": "From Gemini", "start": 0.0}]
CANONICAL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def _gemini_patches():
    return [
        patch("youtubetranscript.pipeline.gemini.transcribe", return_value=GEMINI_SEGS),
        patch("youtubetranscript.pipeline.metadata.fetch_oembed_title", return_value="OEmbed Title"),
    ]


def test_backend_gemini_skips_local_path():
    patches = _patch_all()
    g_tr, g_title = _gemini_patches()
    with patches[0] as mock_meta, patches[1] as mock_caps, patches[2], patches[3], \
         patches[4] as mock_fmt, patches[5] as mock_wr, patches[6], patches[7], patches[8], \
         g_tr as mock_gem, g_title:
        pipeline.run(URL, backend="gemini", lang="en", gemini_model="m1")
        mock_meta.assert_not_called()
        mock_caps.assert_not_called()
        mock_gem.assert_called_once_with(CANONICAL, lang="en", model="m1")
        mock_fmt.assert_called_once_with(GEMINI_SEGS, False)
        mock_wr.assert_called_once_with("Hello", "OEmbed Title")


def test_backend_auto_falls_back_to_gemini_when_local_blocked(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    patches = _patch_all()
    g_tr, g_title = _gemini_patches()
    with patches[0] as mock_meta, patches[1], patches[2], patches[3], \
         patches[4] as mock_fmt, patches[5], patches[6], patches[7], patches[8], \
         g_tr as mock_gem, g_title:
        mock_meta.side_effect = Exception("Sign in to confirm you're not a bot")
        pipeline.run(URL)
        mock_gem.assert_called_once()
        mock_fmt.assert_called_once_with(GEMINI_SEGS, False)


def test_backend_auto_reraises_local_error_without_gemini_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    patches = _patch_all()
    g_tr, g_title = _gemini_patches()
    with patches[0] as mock_meta, patches[1], patches[2], patches[3], \
         patches[4], patches[5], patches[6], patches[7], patches[8], \
         g_tr as mock_gem, g_title:
        mock_meta.side_effect = Exception("Sign in to confirm you're not a bot")
        with pytest.raises(Exception, match="not a bot"):
            pipeline.run(URL)
        mock_gem.assert_not_called()


def test_backend_auto_prefers_local_captions(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    patches = _patch_all(caps=SEGMENTS)
    g_tr, g_title = _gemini_patches()
    with patches[0], patches[1], patches[2], patches[3], \
         patches[4] as mock_fmt, patches[5], patches[6], patches[7], patches[8], \
         g_tr as mock_gem, g_title:
        pipeline.run(URL)
        mock_gem.assert_not_called()
        mock_fmt.assert_called_once_with(SEGMENTS, False)


def test_backend_local_never_uses_gemini(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    patches = _patch_all()
    g_tr, g_title = _gemini_patches()
    with patches[0] as mock_meta, patches[1], patches[2], patches[3], \
         patches[4], patches[5], patches[6], patches[7], patches[8], \
         g_tr as mock_gem, g_title:
        mock_meta.side_effect = Exception("blocked")
        with pytest.raises(Exception, match="blocked"):
            pipeline.run(URL, backend="local")
        mock_gem.assert_not_called()
