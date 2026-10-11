"""Keep the test suite hermetic: tests never see the host's GEMINI_API_KEY.

Without this, the auto backend would fall back to the real Gemini API in any
test where the local path raises and Gemini is not patched.
"""

import pytest


@pytest.fixture(autouse=True)
def _no_host_gemini_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
