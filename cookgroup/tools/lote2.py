"""Lotes 2–5 (v0.9): foro de lanzamientos, raffles, restocks por talla y rebajas, con su prueba positiva y de silencio.

Datos: CAPTURA REAL de BSTN (19-nov-2026, 17 lanzamientos) + cambios CONTROLADOS (otra tienda, cambio de fecha,
cambio de plazo) + Footdistrict real (20-nov) para restocks y rebajas. Discord SIMULADO.
Uso: python tools/lote2.py → docs/v09/CANALES_REGISTRO.md
"""
from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cookgroup.discord import build_embed  # noqa: E402
from cookgroup.forum import FakeForum, Forum  # noqa: E402
from cookgroup.models import Event, EventType  # noqa: E402
from cookgroup.raffles import RaffleBoard, from_bstn  # noqa: E402
from cookgroup.sources.bstn import parse_listing  # noqa: E402
from cookgroup.sources.shopify import parse_products  # noqa: E402
from cookgroup.store import Store  # noqa: E402

NOW = int(datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc).timestamp())


def run(log=print) -> dict:
    tmp = Path(tempfile.mkdtemp())
    st = Store(str(tmp / "lote2.db"))
    steps, ok_all, examples = [], True, {}

    def check(canal, name, cond, detail):
        nonlocal ok_all
        ok_all &= bool(cond)
        steps.append((canal, name, "OK" if cond else "FALLA", detail))
        log(f"[{'OK' if cond else 'FALLA'}] {canal} · {name}: {detail}")

    items = parse_listing(json.loads((ROOT / "tests/fixtures/bstn_upcoming_eu_es_REAL_2026-11-19.json").read_text()),
                          region="eu_es", now=datetime.fromtimestamp(NOW, timezone.utc))
    # ---------------- FORO
    fake = FakeForum()
    forum = Forum(st, fake)
    for l in items:
        forum.ingest(l)
    check("#lanzamientos", "1. Un hilo por lanzamiento (captura real BSTN)", len(fake.threads) == len({l.key for l in items}),
          f"{len(items)} lanzamientos reales → {len(fake.threads)} hilos")
    again = sum(len(forum.ingest(l)) for l in items)
    check("#lanzamientos", "2. 🔕 Releer lo mismo: silencio", again == 0, "0 publicaciones nuevas")
    gta = next(l for l in items if l.key == "JJ7604-001")
    other = replace(gta, store="FOOTDISTRICT", region="es", url="https://footdistrict.com/", raffle=True, raffle_active=True,
                    raffle_url="https://footdistrict.com/", release_ts=None)
    done = forum.ingest(other)
    t = forum.get("JJ7604-001")
    check("#lanzamientos", "3. Aparece otra tienda → se actualiza el MISMO hilo (SIMULACIÓN)", done == ["nueva tienda en el hilo: FOOTDISTRICT"]
          and len(fake.threads) == len({l.key for l in items}) and len(t.stores) == 2, "respuesta «Nueva tienda» + mensaje inicial editado")
    nn = next(l for l in items if l.key == "IF4396-001")
    done = forum.ingest(replace(nn, release_ts=nn.release_ts + 86400))
    check("#lanzamientos", "4. Cambia la fecha → aviso en el hilo (CAMBIO CONTROLADO)", done == ["cambio de fecha en BSTN"],
          fake.threads[forum.get("IF4396-001").thread_id]["replies"][-1]["content"])
    wk = forum.next_7_days(NOW, "1572928642999255120")
    check("#próximos-7-días", "5. Vista de los próximos 7 días", wk and "Próximos 7 días" in wk["embeds"][0]["title"],
          f"{wk['embeds'][0]['description'].count(chr(10)) + 1} lanzamientos con enlace a su hilo")
    examples["lanzamientos"] = fake.threads[t.thread_id]["starter"]
    examples["próximos-7-días"] = wk
    # ---------------- RAFFLES
    sent, pinned = [], {}
    board = RaffleBoard(st, sent.append, lambda p: pinned.update(p=p))
    r = from_bstn(gta, NOW)
    done = board.ingest(r, NOW)
    f = {x["name"]: x["value"] for x in sent[0]["embeds"][0]["fields"]}
    check("#raffles", "6. Apertura con ficha completa (captura real BSTN)", done == ["apertura"] and all(
        k in f for k in ("Qué se sortea", "Inscripción", "Requisitos", "Desde España", "Cierre", "Última verificación", "Entrega")),
          f"cierre {f['Cierre']} · España: {f['Desde España']}")
    examples["raffles"] = sent[0]
    check("#raffles", "7. 🔕 La misma ficha otra vez: silencio", board.ingest(from_bstn(gta, NOW + 60), NOW + 60) == [], "sin publicación")
    r2 = replace(from_bstn(gta, NOW + 120), closes_ts=r.closes_ts + 7200)
    check("#raffles", "8. Cambio de plazo (CAMBIO CONTROLADO +2 h)", board.ingest(r2, NOW + 120) == ["cambio de plazo"], sent[-1]["content"])
    t_rem = r2.closes_ts - 2 * 3600
    check("#raffles", "9. Recordatorio 3 h antes", board.tick(t_rem) == ["recordatorio"], "«CIERRA EN MENOS DE 3 H»")
    check("#raffles", "10. 🔕 Sin recordatorio repetido", board.tick(t_rem + 600) == [], "silencio")
    closed = board.tick(r2.closes_ts + 1)
    check("#raffles", "11. Cierre al vencer y fuera de la lista de abiertos", closed == ["cierre por plazo"]
          and "JJ7604" not in json.dumps(board.list_payload(r2.closes_ts + 1)), pinned["p"]["embeds"][0]["title"])
    check("#raffles", "12. 🔕 Raffle cerrado: no vuelve a avisar", board.ingest(from_bstn(gta, r2.closes_ts + 99), r2.closes_ts + 99) == [],
          "silencio")
    # ---------------- RESTOCKS POR TALLA y REBAJAS (Footdistrict real)
    fd = json.loads((ROOT / "tests/fixtures/footdistrict_REAL_2026-11-20.json").read_text())
    prods = parse_products(fd, store="FOOTDISTRICT", base_url="https://footdistrict.com", currency="EUR")
    ore = next(p for p in prods if "Oregon" in p.title)
    v44 = next(v for v in ore.variants if v.title == "44")
    e = build_embed(Event(EventType.RESTOCK, ore, (replace(v44, available=True),)))
    check("#restocks", "13. Vuelve una talla con stock confirmado de ESA talla", e["embeds"][0]["title"].startswith("🔄 VUELVE LA EU 44"),
          e["embeds"][0]["title"])
    examples["restocks"] = e
    nosize = replace(ore, variants=(replace(v44, title="Única", available=True),))
    e2 = build_embed(Event(EventType.RESTOCK, nosize, nosize.variants))
    check("#restocks", "14. 🔕 Tienda sin tallas: no anuncia «vuelve la 44»", "VUELVE LA" not in e2["embeds"][0]["title"], e2["embeds"][0]["title"])
    drm = next(p for p in prods if "Martens" in p.title)
    cheap = replace(drm, variants=tuple(replace(v, price_cents=22400) for v in drm.variants))
    e3 = build_embed(Event(EventType.PRICE_DROP, cheap, cheap.available_variants, 28000, 22400))
    fx = {x["name"]: x["value"] for x in e3["embeds"][0]["fields"]}
    check("#rebajas-30", "15. Bajada con precio anterior, actual y origen de ambos (CAMBIO CONTROLADO 280→224)",
          "origen" in fx.get("Antes", "") and "origen" in fx.get("Ahora", ""), f"Antes: {fx['Antes'].splitlines()[0]} · Ahora: {fx['Ahora'].splitlines()[0]}")
    examples["rebajas-30"] = e3
    return {"ok": ok_all, "steps": steps, "examples": examples, "forum": fake}


def write_log(res, path=ROOT / "docs/v09/CANALES_REGISTRO.md"):
    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
    L = [f"# Canales prioritarios — pruebas (ejecutado {now}, Madrid)", "",
         "Datos: CAPTURA REAL de BSTN (19-nov) y Footdistrict (20-nov) + CAMBIOS CONTROLADOS + Discord SIMULADO.", "",
         f"Resultado: **{'TODO OK' if res['ok'] else 'HAY FALLOS'}**", "", "| Canal | Prueba | Resultado | Detalle |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in res["steps"]]
    path.write_text("\n".join(L), encoding="utf-8")
    return path


if __name__ == "__main__":
    r = run()
    print(write_log(r))
    sys.exit(0 if r["ok"] else 1)
