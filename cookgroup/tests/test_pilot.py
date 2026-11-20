"""Piloto e2e por HTTP local: captura real de Footdistrict + cambios controlados + Discord simulado que cae y vuelve."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def test_pilot_end_to_end():
    import piloto
    res = piloto.run(log=lambda *_: None)
    assert res["ok"], [s for s in res["steps"] if s[1] != "OK"]
    assert len(res["received"]) == 3
