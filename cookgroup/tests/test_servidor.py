"""Instalador de la estructura del servidor: se puede repetir sin duplicar y nunca toca lo que ya existe."""
import json
from pathlib import Path

from cookgroup.server_setup import DiscordAPI, apply, load_design, make_plan

ROOT = Path(__file__).resolve().parents[1]


class Resp:
    def __init__(self, code, data):
        self.status_code, self._d = code, data
        self.content = json.dumps(data).encode()
        self.text = json.dumps(data)

    def json(self):
        return self._d


class FakeDiscord:
    """Servidor falso con lo que tiene hoy «Mi servidor privado»: general, juegos, música y 2 de voz."""
    def __init__(self, community=False):
        self.n = 100
        self.roles = [{"id": "1", "name": "@everyone"}]
        self.chans = [{"id": "10", "name": "Canales de texto", "type": 4}, {"id": "11", "name": "general", "type": 0, "parent_id": "10"},
                      {"id": "12", "name": "juegos", "type": 0, "parent_id": "10"}, {"id": "13", "name": "música", "type": 0, "parent_id": "10"},
                      {"id": "14", "name": "Canales de voz", "type": 4}, {"id": "15", "name": "Lounge", "type": 2, "parent_id": "14"}]
        self.community, self.calls = community, []

    def _id(self):
        self.n += 1
        return str(self.n)

    def get(self, url, headers=None):
        return Resp(200, self.roles if url.endswith("/roles") else self.chans)

    def post(self, url, headers=None, json=None):
        self.calls.append(("POST", url.split("/v10")[1], json.get("name")))
        if url.endswith("/roles"):
            r = {"id": self._id(), "name": json["name"]}; self.roles.append(r); return Resp(200, r)
        if url.endswith("/webhooks"):
            return Resp(200, {"id": self._id(), "token": "SECRETO"})
        if url.endswith("/messages"):
            self.pinned_cards = getattr(self, "pinned_cards", 0) + 1
            return Resp(200, {"id": self._id()})
        if json.get("type") in (5, 15) and not self.community:
            return Resp(400, {"message": "requiere Comunidad"})
        c = {"id": self._id(), **json}; self.chans.append(c); return Resp(200, c)

    def put(self, url, headers=None, json=None):
        if "/pins/" in url:
            return Resp(204, {})
        return Resp(200, {}) if self.community else Resp(400, {"message": "requiere Comunidad"})


def test_install_is_idempotent_and_keeps_existing(tmp_path):
    d = load_design(ROOT / "config/servidor.toml")
    fake, env = FakeDiscord(), tmp_path / ".env"
    r1 = apply(d, DiscordAPI("t", "1", fake), env, log=lambda *_: None)
    assert len(r1["plan"].channels) == 38 + 207 and {"general", "juegos", "música"} <= set(r1["plan"].kept)
    assert r1["webhooks_added"] >= 15 and "SECRETO" in env.read_text()
    assert any("Comunidad" in n for n in r1["notes"])            # foros → texto + aviso
    before = len(fake.calls)
    r2 = apply(d, DiscordAPI("t", "1", fake), env, log=lambda *_: None)
    assert r2["plan"].empty and len(fake.calls) == before          # segunda vez: nada que crear
    assert r1["cards_pinned"] == _lote_cards() and r2["cards_pinned"] == 0    # tarjeta fijada una sola vez por tienda del lote
    assert (tmp_path / "data/canales_ids.json").exists()
    assert not any(c[0] != "POST" for c in fake.calls)             # nunca borra ni edita
    names = [c["name"] for c in fake.chans]
    assert len(names) == len(set(names))                           # sin duplicados


def test_plan_counts():
    d = load_design(ROOT / "config/servidor.toml")
    p = make_plan(d, [], [], set())
    assert len(p.roles) == 4 + 10 + 14 + 5 + 29 and len(p.categories) == 18


def _lote_cards():
    """Una tarjeta fijada por tienda de los lotes (config/lote*_tiendas.toml): crece al integrar tiendas."""
    import pathlib
    import tomllib
    cfg = pathlib.Path(__file__).parents[1] / "config"
    return sum(len(tomllib.loads(f.read_text(encoding="utf-8")).get("tienda", [])) for f in cfg.glob("lote*_tiendas.toml"))
