"""Lote 1 (v0.8): bienvenida, roles y notificaciones. Recorrido completo de un miembro, SIN webhook real.

Perfil de prueba: EU 44,5 · ASICS y New Balance · envío a España (config/miembros.toml).
Datos: CAPTURA REAL de Footdistrict (20-nov-2026 12:39) con el stock tal cual + cambios CONTROLADOS
(vuelve la 44,5 de las New Balance; vuelve la 44 de las ASICS). Discord SIMULADO.
Uso: python tools/lote1.py   → docs/v08/LOTE1_REGISTRO.md
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import piloto  # noqa: E402  (servidores locales de tienda y Discord)
from cookgroup.config import MonitorConfig  # noqa: E402
from cookgroup.discord import WebhookSender, build_embed  # noqa: E402
from cookgroup.market import FileMarketProvider  # noqa: E402
from cookgroup.members import Profile, decide, load_profiles, personalize  # noqa: E402
from cookgroup.models import Event, EventType  # noqa: E402
from cookgroup.pipeline import run_cycle  # noqa: E402
from cookgroup.sources.shopify import ShopifySource, parse_products  # noqa: E402
from cookgroup.store import Store  # noqa: E402

FIX = ROOT / "tests/fixtures/footdistrict_nb_asics_REAL_2026-11-20.json"
NB, AS = "new-balance-u990v7-gr7-made-in-usa-u990gr7", "asics-gel-kayano-14-carrier-grey-1203a537-026"


def run(log=print) -> dict:
    state = piloto.State()
    state.catalog = json.loads(FIX.read_text(encoding="utf-8"))
    shop, disc = piloto._servers(state)
    url = f"http://127.0.0.1:{shop.server_port}"
    hook = f"http://127.0.0.1:{disc.server_port}/api/webhooks/0/lote1"
    tmp = Path(tempfile.mkdtemp())
    store = Store(tmp / "lote1.db")
    profiles = load_profiles(ROOT / "config/miembros.toml")
    me = profiles[0]
    cfg = MonitorConfig("footdistrict", "shopify", "FOOTDISTRICT", url, channel="sneakers", country="ES", region="eu",
                        ships_es="sí")
    market = FileMarketProvider(tmp / "none.json")
    send = WebhookSender(hook, max_retries=1).send
    src = ShopifySource("FOOTDISTRICT", url)
    steps, ok = [], True

    def check(name, cond, detail, kind="silencio" if False else ""):
        nonlocal ok
        ok &= bool(cond)
        steps.append((name, "OK" if cond else "FALLA", detail))
        log(f"[{'OK' if cond else 'FALLA'}] {name}: {detail}")

    def setsize(handle, size, val=True):
        p = next(x for x in state.catalog["products"] if x["handle"] == handle)
        next(v for v in p["variants"] if v["title"] == size)["available"] = val

    # 0. el miembro elige en la bienvenida
    design = __import__("tomllib").loads((ROOT / "config/servidor.toml").read_text(encoding="utf-8"))
    from_roles = Profile.from_roles(me.member_id, "Javi", ["Sneakers", "Rebajas", "Lanzamientos", "Raffles", "ASICS",
                                                         "New Balance", "Envío a España", "EU 44,5"], design)
    check("0. Bienvenida → perfil", from_roles.sizes == {"44.5"} and from_roles.brands == {"ASICS", "New Balance"}
          and "Envío a España" in from_roles.regions,
          "roles elegidos: Sneakers, Rebajas, Lanzamientos, Raffles · ASICS, New Balance · Envío a España · EU 44,5")

    r = run_cycle(cfg, {}, src, store, market, send, profiles=profiles)
    check("1. Base (estado real de la tienda)", r["ok"] and r["sent"] == 0,
          f"{r['products']} productos reales; NB 990v7: 44,5 agotada; ASICS Kayano 14: solo 42,5 y 43,5")

    setsize(NB, "44.5")
    r = run_cycle(cfg, {}, src, store, market, send, profiles=profiles)
    last = state.received[-1] if state.received else {}
    good = last.get("allowed_mentions", {}).get("users") == [me.member_id] and f"<@{me.member_id}>" in last.get("content", "")
    check("2. ✅ Vuelve la EU 44,5 de New Balance → te menciona", r["sent"] == 1 and good,
          f"aviso en #sneakers-eu con «<@tu-id> · EU 44,5»; solo se notifica a tu usuario (allowed_mentions)")
    received_payload = last

    setsize(AS, "44")
    n0 = len(state.received)
    r = run_cycle(cfg, {}, src, store, market, send, profiles=profiles)
    last = state.received[-1] if len(state.received) > n0 else {}
    silent = r["sent"] == 1 and not last.get("allowed_mentions", {}).get("users") and "<@" not in last.get("content", "")
    ev_as = Event(EventType.RESTOCK, next(p for p in parse_products(state.catalog, store="FOOTDISTRICT", base_url=url,
                                                                    currency="EUR") if p.product_id.endswith("57978")),
                  ())
    reason = decide(me, Event(EventType.RESTOCK, ev_as.product, tuple(v for v in ev_as.product.variants if v.title == "44")),
                    channel="sneakers", family="Sneakers", ships_es="sí").reason
    check("3. 🔕 Vuelve la EU 44 de ASICS (no es tu talla) → se publica, pero sin mencionarte", silent,
          f"motivo registrado: {reason}")
    discarded_payload = last

    # 4. misma señal en el canal agregado → no hay segunda mención
    prod_nb = next(p for p in parse_products(state.catalog, store="FOOTDISTRICT", base_url=url, currency="EUR")
                   if p.product_id.endswith("899706"))
    ev_nb = Event(EventType.RESTOCK, prod_nb, tuple(v for v in prod_nb.variants if v.title == "44.5"))
    _, dec = personalize(build_embed(ev_nb), ev_nb, profiles, store, channel="restocks", family="Sneakers", ships_es="sí")
    check("4. 🔕 La misma señal en el canal agregado (#restocks) → sin segunda mención", not dec[0][1].notify,
          dec[0][1].reason)

    # 5–8. casos de silencio por reglas
    ev_ad = Event(EventType.RESTOCK, prod_nb.__class__(**{**prod_nb.__dict__, "vendor": "adidas",
                                                          "title": "adidas Originals Oregon Ultra Tech"}), ev_nb.variants)
    cases = [
        ("5. 🔕 Otra marca (adidas) en tu talla", decide(me, ev_ad, channel="sneakers", family="Sneakers", ships_es="sí")),
        ("6. 🔕 Tienda que solo da stock general: no puede decir «vuelve la 44,5»",
         decide(me, ev_nb, channel="sneakers", family="Sneakers", ships_es="sí", size_stock=False)),
        ("7. 🔕 Tienda sin envío a España confirmado", decide(me, ev_nb, channel="sneakers", family="Sneakers",
                                                            ships_es="por confirmar")),
        ("8. 🔕 Avisos en pausa", decide(Profile(**{**me.__dict__, "paused": True}), ev_nb, channel="sneakers",
                                         family="Sneakers", ships_es="sí")),
    ]
    for name, d in cases:
        check(name, not d.notify, d.reason)
    ev_new = Event(EventType.NEW_PRODUCT, prod_nb, ())
    d = decide(me, ev_new, channel="sneakers", family="Sneakers", ships_es="sí", size_stock=False)
    check("9. Producto nuevo de tu marca en tienda sin tallas → aviso de producto, avisando de que la talla no está confirmada",
          d.notify and "sin confirmar" in d.reason, d.reason)
    shop.shutdown(); disc.shutdown()
    return {"ok": ok, "steps": steps, "received": received_payload, "discarded": discarded_payload, "all": state.received}


def write_log(res: dict, path: Path = ROOT / "docs/v08/LOTE1_REGISTRO.md") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
    L = [f"# Lote 1 — bienvenida, roles y notificaciones (ejecutado {now}, Madrid)", "",
         "**Datos:** CAPTURA REAL de Footdistrict (20-nov 12:39) + cambios CONTROLADOS + Discord SIMULADO. "
         "Perfil de prueba: EU 44,5 · ASICS y New Balance · envío a España.", "",
         f"Resultado: **{'TODO OK' if res['ok'] else 'HAY FALLOS'}**", "", "| Paso | Resultado | Detalle |", "|---|---|---|"]
    L += [f"| {a} | {b} | {c} |" for a, b, c in res["steps"]]
    L += ["", "Repetir: `python tools/lote1.py`"]
    path.write_text("\n".join(L), encoding="utf-8")
    return path


if __name__ == "__main__":
    r = run()
    print(write_log(r))
    sys.exit(0 if r["ok"] else 1)
