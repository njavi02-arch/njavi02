import pytest

from cookgroup import ratelimit


@pytest.fixture(autouse=True)
def _no_domain_wait(monkeypatch):
    monkeypatch.setattr(ratelimit, "DEFAULT_MIN_INTERVAL", 0.0)
