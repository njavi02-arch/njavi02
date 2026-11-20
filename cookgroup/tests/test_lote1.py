"""Lote 1 (v0.8): del perfil del miembro a la mención, con captura real + cambios controlados + Discord simulado."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def test_lote1_member_journey():
    import lote1
    r = lote1.run(log=lambda *_: None)
    assert r["ok"], [s for s in r["steps"] if s[1] != "OK"]
    assert r["received"]["allowed_mentions"]["users"] == ["100000000000000001"]
    assert "<@" not in r["discarded"].get("content", "")


def test_eu_size_parsing():
    from cookgroup.members import eu_size
    assert eu_size("44,5") == eu_size("EU 44.5") == eu_size("44½") == "44.5"
    assert eu_size("US 10") is None and eu_size("M") is None and eu_size("44 2/3") == "44 2/3"
