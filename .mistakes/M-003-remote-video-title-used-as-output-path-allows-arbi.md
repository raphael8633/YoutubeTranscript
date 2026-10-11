---
id: M-003
title: Remote video title used as output path allows arbitrary file write
severity: hard
triggers:
  keywords:
  - writer.write(text, output or title)
  - os.path.isabs trusted for video title
  - oEmbed / yt-dlp title chooses output filename
  - new title source added to pipeline
guard:
  command: Pass remote titles through writer.sanitize_filename before writer.write; only a user-supplied --output may be an absolute path.
status: active
---

## Symptom
`writer.write` trusts absolute paths. The pipeline passed the remote video title straight through, so a title such as `/home/ubuntu/.bashrc` would overwrite that file.

## Resolution
`pipeline.run` calls `writer.write(text, output or writer.sanitize_filename(title))`; covered by `test_pipeline_sanitizes_remote_title_into_plain_filename` for both backends.
