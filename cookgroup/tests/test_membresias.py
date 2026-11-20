"""v0.9: alta, baja, renovación, pago fallido, duplicado, firma falsa y Discord caído (web local + simulador de Stripe)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def test_membership_journey():
    import membresias_demo
    r = membresias_demo.run(log=lambda *_: None)
    assert r["ok"], [s for s in r["steps"] if s[1] != "OK"]


def test_signature_scheme():
    import pytest
    from cookgroup.billing import BadSignature, sign, verify
    body = b'{"id":"evt_1","type":"x","data":{"object":{}}}'
    h = sign(body, "whsec_x", 1000)
    assert verify(body, h, "whsec_x", now=1100)["id"] == "evt_1"
    with pytest.raises(BadSignature):
        verify(body, h, "whsec_otro", now=1100)
    with pytest.raises(BadSignature):
        verify(body, h, "whsec_x", now=5000)          # repetición tardía
