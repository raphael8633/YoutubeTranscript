---
id: M-002
title: Tests inherit host GEMINI_API_KEY and hit the real Gemini API
severity: hard
triggers:
  keywords:
  - GEMINI_API_KEY exported in the host shell
  - auto backend falls back to Gemini in a test
  - test patches local path but not gemini.transcribe
  - DID NOT RAISE in pipeline failure test
guard:
  command: Keep tests/conftest.py autouse fixture that delenv GEMINI_API_KEY; tests needing a key set a fake one via monkeypatch and patch gemini._post / gemini.transcribe.
status: active
---

## Symptom
A pipeline test that makes the local path raise (without patching Gemini) silently fell back to the real Gemini API because the host shell exports GEMINI_API_KEY; the request was billed and the test failed with "DID NOT RAISE".

## Resolution
`tests/conftest.py` strips GEMINI_API_KEY for every test. Any new network seam (`_post`, `_get_json`) must be patched in tests, never reached.
