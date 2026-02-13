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
