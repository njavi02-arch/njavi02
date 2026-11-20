"""v0.9: foro de lanzamientos, raffles, restocks por talla y rebajas (positivos y silencios)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def test_channels_batch():
    import lote2
    r = lote2.run(log=lambda *_: None)
    assert r["ok"], [s for s in r["steps"] if s[2] != "OK"]


def test_store_filter_in_profile():
    from cookgroup.members import Profile, decide
    from cookgroup.models import Event, EventType, Product, Variant
    p = Product("SNIPES", "1", "Nike Dunk", "https://t", "EUR", (Variant("v", "44.5", 10000, True),), vendor="Nike")
    prof = Profile("1", "x", sizes={"44.5"}, excluded_stores={"SNIPES"})
    assert "por tienda" in decide(prof, Event(EventType.RESTOCK, p, p.variants), channel="sneakers", family="Sneakers", ships_es="sí").reason


def test_sample_feed_delay_cap_and_no_mentions():
    from cookgroup.sample_feed import SampleFeed
    f = SampleFeed()
    pl = {"content": "🔔 <@1>", "allowed_mentions": {"users": ["1"]}, "embeds": [{"title": "x"}]}
    assert all(f.offer(pl, 1000 + i) for i in range(3)) and not f.offer(pl, 1100)   # cupo de 3 al día
    assert f.due(1000 + 3599) == []                                                 # aún con retraso
    out = f.due(1000 + 3603)
    assert len(out) == 3 and "content" not in out[0] and out[0]["allowed_mentions"] == {"parse": []}
