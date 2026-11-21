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


def test_member_counter_renames_hourly(tmp_path):
    from cookgroup.billing import Billing, load_plans
    from cookgroup.store import Store
    from cookgroup.web import App, update_counter

    class R:
        names = []
        def rename_counter(self, cid, n): self.names.append((cid, n))
    b = Billing(Store(str(tmp_path / "x.db")), load_plans())
    app = App(b, R(), env={"SESSION_SECRET": "x", "DISCORD_CONTADOR_CHANNEL_ID": "55"})
    assert update_counter(app) == 0 and R.names == [("55", 0)]
    assert update_counter(app) is None                 # no más de una vez por hora
