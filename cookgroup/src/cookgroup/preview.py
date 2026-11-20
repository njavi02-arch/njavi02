"""Vista previa HTML de los mensajes (estilo Discord) y alerta de prueba para el webhook.

Los ejemplos salen de muestras REALES capturadas el 19-nov-2026 (tests/fixtures/*_REAL_*) y, para los
eventos que no se pueden capturar a demanda (restock, bajada, price error), de transformaciones de esas
muestras claramente marcadas como SIMULADAS.
"""
from __future__ import annotations

import html
import json
import re
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .discord import build_embed
from .models import Event, EventType, Opportunity
from .releases import Calendar, Release, StoreLink, build_digest, build_reminder
from .rules import PingRule, build_ping
from .sources.rss import parse_feed
from .sources.shopify import parse_products
from .normalize import clean_variants

FIX = Path(__file__).resolve().parent / "samples"
TS = "2026-11-19T12:45:00+00:00"


def _mind001():
    d = json.loads((FIX / "shopify_family30_REAL_2026-11-19.json").read_text())
    return clean_variants(parse_products(d, store="Family 3.0", base_url="https://www.family3-0.com", currency="EUR")[0])


def _bstn_samples() -> list[tuple[str, str, dict]]:
    from .launches import LaunchEvent, LaunchEventType, apply_product, build_launch_digest, build_launch_embed, diff_launches
    from .sources.bstn import parse_listing, parse_product
    now = datetime(2026, 11, 19, 13, 20, tzinfo=timezone.utc)
    items = parse_listing(json.loads((FIX / "bstn_upcoming_eu_es_REAL_2026-11-19.json").read_text()), region="eu_es", now=now)
    by = {i.key: i for i in items}
    _, st = diff_launches({}, items, now)
    out = [("lanzamientos", "RESUMEN INICIAL · datos reales de BSTN (19-nov-2026)",
            build_launch_digest(st, now, title="Resumen inicial — BSTN: raffles abiertos y próximos lanzamientos"))]
    out.append(("raffles", "RAFFLE ABIERTO · datos reales de BSTN",
                build_launch_embed(LaunchEvent(LaunchEventType.RAFFLE_OPEN, by["JJ7604-001"], "k"), now)))
    near = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
    out.append(("raffles", "RECORDATORIO DE CIERRE · real, mostrado como se vería el 20-nov a las 13:00",
                build_launch_embed(LaunchEvent(LaunchEventType.RAFFLE_CLOSING, by["JJ7604-001"], "k"), near)))
    out.append(("lanzamientos", "ANUNCIO · datos reales (aparece como nuevo en «Coming Soon»)",
                build_launch_embed(LaunchEvent(LaunchEventType.ANNOUNCED, by["IF4396-001"], "k"), now)))
    car = by["IW6306-001"]
    out.append(("lanzamientos", "FECHA CAMBIADA (SIMULADA a partir de datos reales)",
                build_launch_embed(LaunchEvent(LaunchEventType.DATE_CHANGED, car, "k", old_ts=car.release_ts - 86400, simulated=True), now)))
    page = parse_product(json.loads((FIX / "bstn_product_iw6306-001_REAL_2026-11-19.json").read_text()))
    at = datetime.fromtimestamp(car.release_ts + 52, timezone.utc)
    ev = apply_product(car.uid, st[car.uid], page, at, live_check=True)[0]
    ev.simulated = True
    out.append(("lanzamientos", "A LA VENTA (SIMULADO: tallas reales de la ficha previa al lanzamiento)", build_launch_embed(ev, at)))
    from .sources.bstn import SizeStock
    rs = LaunchEvent(LaunchEventType.SIZE_RESTOCK, car, "k", sizes=[next(x for x in page.sizes if x.eu == "43")], simulated=True)
    out.append(("restocks", "VUELVE UNA TALLA (SIMULADO)", build_launch_embed(rs, at + timedelta(hours=3))))
    return out


def sample_payloads() -> list[tuple[str, str, dict]]:
    """(canal, etiqueta, payload) para la vista previa."""
    p = _mind001()
    out: list[tuple[str, str, dict]] = _bstn_samples()
    out.append(("sneakers", "RESTOCK · datos reales de Family 3.0 (estado de stock simulado)",
                build_embed(Event(EventType.RESTOCK, p, p.available_variants, detected_at=TS))))
    sz = p.available_variants[0].title          # la talla de las ventas ES una talla disponible (corrección v0.8)
    opp = Opportunity(Event(EventType.NEW_PRODUCT, p, p.available_variants), p.available_variants[0].price_cents, 15500,
                      3440, 38.2, 71, margin_pct=22.2, verified=True, buy_size=sz,
                      basis=f"SIMULACIÓN: 5 ventas cerradas de EJEMPLO en stockx, talla {sz}, nuevo, la más reciente hace "
                            f"3 días y la más antigua hace 26; costes: comisión 9 % + envío de venta 5,00 € + envío de compra 0 €")
    out.append(("sneakers", "NUEVO PRODUCTO con beneficio VERIFICADO (ventas de EJEMPLO: simulación)",
                build_embed(Event(EventType.NEW_PRODUCT, p, p.available_variants, detected_at=TS), opp)))
    opp2 = Opportunity(Event(EventType.NEW_PRODUCT, p, p.available_variants), 9000, None, None, None, 0,
                       notes=["solo 1 ventas en los últimos 30 días (mínimo 3)", "envío a España sin confirmar"])
    out.append(("sneakers", "NUEVO PRODUCTO con «beneficio sin verificar» (lo normal hoy: market_data vacío)",
                build_embed(Event(EventType.NEW_PRODUCT, p, p.available_variants, detected_at=TS), opp2)))
    cheap = replace(p, variants=tuple(replace(v, price_cents=5400, compare_at_cents=9000) for v in p.variants))
    out.append(("rebajas_30", "BAJADA DE PRECIO (SIMULADA) · copiada también al canal del tramo 30 %",
                build_embed(Event(EventType.PRICE_DROP, cheap, cheap.available_variants, 9000, 5400, TS))))
    err = replace(p, variants=tuple(replace(v, price_cents=1800) for v in p.variants))
    pe_opp = Opportunity(Event(EventType.PRICE_ERROR, err), 1800, None, None, None, 55,
                         notes=["Referencia: mediana de 12 precios observados por este sistema",
                                "Posible error de precio: la tienda puede cancelar el pedido"])
    out.append(("sneakers", "POSIBLE PRICE ERROR (SIMULADO)",
                build_embed(Event(EventType.PRICE_ERROR, err, err.available_variants, 9000, 1800, TS), pe_opp)))
    deals = parse_feed((FIX / "chollometro_REAL_2026-11-19.xml").read_text(), store="Chollometro")
    for d in deals:
        out.append(("chollos", "CHOLLO · entrada real del feed de Chollometro",
                    build_embed(Event(EventType.NEW_PRODUCT, d, d.variants, detected_at=TS))))
    rule = PingRule.from_dict({"name": "mind", "keywords": ["mind 001"], "max_price": 100, "channel": "pings",
                               "role_id": "111111111111111111"})
    ev = Event(EventType.RESTOCK, p, p.available_variants, detected_at=TS)
    out.append(("pings", "PING por regla \"mind 001 ≤ 100\" (rol de ejemplo)", build_ping(rule, ev, build_embed(ev))))
    rel = Release("nike-mind-001-hq4307-001", "Nike Mind 001 Pre-Game Mules (Black/Hyper Crimson)",
                  datetime(2026, 11, 20, 9, 0, tzinfo=timezone(timedelta(hours=1))), "LEO", "unknown", "HQ4307-001",
                  89.99, [StoreLink("Nike", "https://www.nike.com/es/launch")], notes="SIMULACIÓN: en producción solo se avisa si status=confirmado.", status="confirmado",
                  official_source="https://www.nike.com/es/launch")
    out.append(("releases", "RECORDATORIO de lanzamiento (calendario del staff)", build_reminder(rel, 60)))
    cal = Calendar("releases", "Europe/Madrid", [60], "08:00", [rel])
    out.append(("releases", "RESUMEN \"Drops del día\"", build_digest(cal, rel.release_at.date())))
    return out


# ----------------------------------------------------------------------------- render
def _md(text: str) -> str:
    t = html.escape(str(text))
    t = re.sub(r"&lt;t:(\d+):([A-Za-z])&gt;", lambda m: _ts(int(m.group(1)), m.group(2)), t)
    t = re.sub(r"&lt;@&amp;(\d+)&gt;", r'<span class="mention">@rol</span>', t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"~~(.+?)~~", r"<s>\1</s>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t.replace("\n", "<br>")


def _ts(ts: int, style: str) -> str:
    d = datetime.fromtimestamp(ts, timezone(timedelta(hours=1)))
    if style == "R":
        return '<span class="ts">(relativo)</span>'
    if style == "D":
        return f'<span class="ts">{d:%d/%m/%Y}</span>'
    return f'<span class="ts">{d:%d/%m/%Y %H:%M}</span>'


def _embed_html(e: dict) -> str:
    color = f"#{e.get('color', 0x5865F2):06x}"
    title = _md(e.get("title", ""))
    if e.get("url"):
        title = f'<a href="{html.escape(e["url"])}" target="_blank" rel="noopener">{title}</a>'
    thumb = f'<img class="thumb" src="{html.escape(e["thumbnail"]["url"])}" alt="" onerror="this.remove()">' if e.get("thumbnail") else ""
    fields, row = [], []
    for f in e.get("fields", []):
        cell = f'<div class="field{" inline" if f.get("inline") else ""}"><div class="fn">{_md(f["name"])}</div><div class="fv">{_md(f["value"])}</div></div>'
        fields.append(cell)
    foot = _md(e.get("footer", {}).get("text", ""))
    desc = f'<div class="desc">{_md(e["description"])}</div>' if e.get("description") else ""
    return (f'<div class="embed" style="border-left-color:{color}"><div class="eb">{thumb}<div class="et">{title}</div>{desc}'
            f'<div class="fields">{"".join(fields)}</div><div class="foot">{foot}</div></div></div>')


def render_html(items: list[tuple[str, str, dict]], title: str = "Cookgroup — vista previa de alertas") -> str:
    msgs = []
    for ch, label, payload in items:
        content = f'<div class="content">{_md(payload["content"])}</div>' if payload.get("content") else ""
        embeds = "".join(_embed_html(e) for e in payload.get("embeds", []))
        msgs.append(f'<section><div class="chan"># {html.escape(ch)}</div><div class="label">{html.escape(label)}</div>'
                    f'<div class="msg"><div class="avatar">CG</div><div class="body"><div class="author">Cookgroup '
                    f'<span class="app">APP</span></div>{content}{embeds}</div></div></section>')
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>
:root{{--bg:#313338;--panel:#2b2d31;--text:#dbdee1;--muted:#949ba4;--link:#00a8fc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.4 "gg sans","Noto Sans",Helvetica,Arial,sans-serif}}
header{{padding:24px 24px 8px;max-width:820px;margin:auto}}h1{{font-size:20px;margin:0 0 6px;color:#f2f3f5}}
header p{{margin:4px 0;color:var(--muted);font-size:13px}}main{{max-width:820px;margin:auto;padding:0 24px 40px}}
section{{margin:22px 0}}.chan{{color:var(--muted);font-weight:600;font-size:13px}}.label{{color:#f0b232;font-size:12px;margin:2px 0 8px}}
.msg{{display:flex;gap:14px}}.avatar{{flex:none;width:40px;height:40px;border-radius:50%;background:#5865f2;color:#fff;display:grid;place-items:center;font-weight:700;font-size:13px}}
.author{{font-weight:600;color:#f2f3f5}}.app{{background:#5865f2;color:#fff;font-size:10px;padding:1px 4px;border-radius:3px;vertical-align:middle}}
.content{{margin:2px 0 4px}}.mention{{background:rgba(88,101,242,.3);color:#c9cdfb;padding:0 2px;border-radius:3px}}
.embed{{background:var(--panel);border-left:4px solid;border-radius:4px;max-width:520px;margin-top:4px}}.eb{{padding:10px 14px 12px;position:relative}}
.thumb{{float:right;width:80px;height:80px;object-fit:cover;border-radius:4px;margin:0 0 8px 12px;background:#fff}}
.et{{font-weight:700;color:#f2f3f5;margin-bottom:6px}}.et a{{color:var(--link);text-decoration:none}}.desc{{margin-bottom:6px}}
.fields{{display:flex;flex-wrap:wrap;gap:6px 16px;clear:none}}.field{{flex:1 1 100%;min-width:0}}.field.inline{{flex:1 1 140px}}
.fn{{font-weight:700;font-size:13px;color:#f2f3f5}}.fv{{font-size:14px;word-break:break-word}}a{{color:var(--link)}}
code{{background:#1e1f22;padding:1px 4px;border-radius:3px;font-size:13px}}.foot{{clear:both;color:var(--muted);font-size:12px;margin-top:8px}}
.ts{{background:#3f4147;border-radius:3px;padding:0 3px}}
</style></head><body><header><h1>{html.escape(title)}</h1>
<p>Generado con el código real del bot a partir de muestras capturadas el 19-nov-2026 (BSTN, Family 3.0, Chollometro).
Los eventos marcados como SIMULADOS transforman esas muestras para enseñar el formato.</p>
<p>Así se verán en Discord; los colores y el orden de campos son los mismos que enviará el webhook.</p></header>
<main>{"".join(msgs)}</main></body></html>"""


def write_preview(path: str | Path) -> Path:
    path = Path(path)
    path.write_text(render_html(sample_payloads()), encoding="utf-8")
    return path


def test_payload() -> dict:
    p = _mind001()
    payload = build_embed(Event(EventType.RESTOCK, p, p.available_variants,
                                detected_at=datetime.now(timezone.utc).isoformat(timespec="seconds")))
    payload["content"] = "🧪 **Mensaje de PRUEBA del cookgroup** — si ves esto, el webhook funciona."
    payload["embeds"][0]["footer"]["text"] = "PRUEBA · datos de muestra del 19-nov-2026, no es un restock real"
    payload["allowed_mentions"] = {"parse": []}
    return payload
