"""Panel de tiendas en directo (v1.1): ¿el bot funciona?, ¿cada tienda se lee?, ¿qué se ha publicado y dónde?

Se regenera solo cada 30 s mientras el bot está en marcha (docs/v11/PANEL_TIENDAS.html) y la página se recarga sola.
Distingue tres situaciones que antes se confundían:
  · BOT PARADO        → el proceso no late: nada se está leyendo.
  · FUENTE CAÍDA      → el bot va, pero esa tienda no se lee bien (errores seguidos o sin lectura buena a tiempo).
  · SIN NOVEDADES     → la tienda se lee bien y simplemente no ha publicado nada nuevo.
"""
from __future__ import annotations

import html
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from .store_directory import EU_ORDER, FLAGS, SIGNALS, channel_ids, load_lote, reconcile

E = html.escape
MAD = ZoneInfo("Europe/Madrid")
OUT = Path("docs/v11/PANEL_TIENDAS.html")


def _mad(ts) -> str:
    if ts in (None, ""):
        return "—"
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    return datetime.fromtimestamp(ts, MAD).strftime("%d/%m %H:%M:%S")


def _ago(ts, now) -> str:
    if ts in (None, ""):
        return "nunca"
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    s = int(now - ts)
    return f"hace {s} s" if s < 120 else f"hace {s // 60} min" if s < 7200 else f"hace {s // 3600} h"


def state_of(bot_up: bool, health: tuple | None, interval: int, now: float, recent_events: int) -> tuple[str, str]:
    if not bot_up:
        return "BOT PARADO", "bad"
    if not health or not health[1]:
        return "SIN LECTURA TODAVÍA", "warn"
    last_ok = datetime.fromisoformat(health[1]).timestamp()
    if (health[2] or 0) >= 3 or now - last_ok > interval * 2 + 150:
        return "FUENTE CAÍDA", "bad"
    return ("AL DÍA · con avisos" if recent_events else "AL DÍA · sin novedades"), "ok"


def collect(store, cfg, *, now: float | None = None, env=None, heartbeat=None) -> dict:
    import os
    from .diagnostics import process_state
    from .raffle_router import latest
    now = now or time.time()
    env = env if env is not None else os.environ
    pst, pdet = process_state(heartbeat) if heartbeat else process_state()
    bot_up = pst == "EN MARCHA"
    health = {h[0]: h for h in store.health()}
    sched = store.schedules()
    deliveries = latest(store, limit=500)
    guild, ids = channel_ids()
    lote = load_lote()
    rows = reconcile(monitors=cfg.monitors, lote=lote)
    mons = {m.name: m for m in cfg.monitors}
    alerts = store.db.execute("SELECT store, channel, MAX(sent_at), message_id, COUNT(*) FROM alerts WHERE message_id IS NOT NULL "
                              "AND message_id NOT IN ('', 'None', 'hilo') AND COALESCE(channel, '') != 'pruebas' "
                              "AND dedupe_key NOT LIKE 'real|%' GROUP BY store, channel").fetchall()
    stores = []
    for t in lote:
        ms = [mons[n] for n in t["monitores"] if n in mons]
        m0 = ms[0] if ms else None
        h = health.get(m0.name) if m0 else None
        sc = sched.get(m0.name, {}) if m0 else {}
        interval = sc.get("interval_s") or (m0.interval_seconds if m0 else 0)
        ch_key = "tienda_" + t["canal"].replace("-", "_")
        mine = [d for d in deliveries if d["store"] == t["nombre"] and not d["prueba"]]
        ap = [d for d in mine if d["kind"] == "apertura"]          # se enlaza el de #raffles-<tienda> si existe
        raffle = next((d for d in ap if d["channel"].startswith("raffles_")), ap[0] if ap else None)
        last = [a for a in alerts if a[0] == t["nombre"] or a[1] == ch_key]
        last = max(last, key=lambda a: a[2]) if last else None
        recent = sum(1 for a in alerts if (a[0] == t["nombre"]) and a[2] and
                     now - datetime.fromisoformat(a[2]).timestamp() < 86400)
        st, cls = state_of(bot_up, h, interval or 600, now, recent)
        cid = ids.get(t["canal"])
        stores.append({"nombre": t["nombre"], "pais": t["pais"], "canal": t["canal"],
                       "canal_url": f"https://discord.com/channels/{guild}/{cid}" if guild and cid else None,
                       "instalado": bool(cid) or bool(env.get(f"DISCORD_WEBHOOK_{ch_key.upper()}")),
                       "intervalo_s": interval, "ultima_ok": h[1] if h else None, "errores": h[2] if h else None,
                       "ultimo_error": h[3] if h else None, "proximo": sc.get("next_at"), "motivo_espera": sc.get("reason"),
                       "senales": {s: t.get(s, "sin-fuente") for s in SIGNALS},
                       "ultimo_raffle": raffle, "ultimo_aviso": last, "estado": st, "clase": cls, "envio_es": t.get("envio_es")})
    verified_channels = {a[1] for a in alerts if a[1] and not str(a[1]).startswith("pruebas")}
    counts = {"descubiertas": len(rows),
              "fuente_validada": sum(1 for r in rows if r["nivel"] == "piloto" or any(
                  (health.get(n) or (None, None))[1] for n in r["monitores"])),
              "instaladas": sum(1 for s in stores if s["instalado"]),
              "entrega_verificada": sum(1 for s in stores if ("tienda_" + s["canal"].replace("-", "_")) in verified_channels
                                        or s["nombre"] in {d["store"] for d in deliveries if not d["prueba"] and d["message_id"]})}
    tests = [d for d in deliveries if d["prueba"]][:5]
    return {"now": now, "bot": (pst, pdet), "demo": not health and not ids, "stores": stores, "directory": rows,
            "counts": counts, "pruebas": tests, "guild": guild, "ids": ids}


CSS = """body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1115;color:#e7e9ee}
main{max-width:1200px;margin:auto;padding:16px}h1{font-size:22px;margin:4px 0}h2{font-size:17px;margin:22px 0 8px}
.muted{color:#9aa3b2;font-size:13px}.banner{padding:12px 14px;border-radius:10px;margin:10px 0;font-weight:600}
.ok{background:#12351f;color:#7ee2a0}.bad{background:#3a1416;color:#ff9b9b}.warn{background:#3a2e12;color:#ffd479}
.demo{background:#2b2140;color:#d6c2ff}.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}
.k div{background:#181b22;border-radius:10px;padding:12px}.k b{display:block;font-size:26px;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:7px 6px;border-bottom:1px solid #262a33;text-align:left;vertical-align:top}
th{color:#9aa3b2;font-weight:600}.tag{display:inline-block;padding:2px 7px;border-radius:6px;font-size:12px;font-weight:600}
a{color:#8ab4ff}.f{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}select,input{background:#181b22;color:#e7e9ee;border:1px solid #333;border-radius:8px;padding:6px}
.s-probado{color:#7ee2a0}.s-por-probar{color:#ffd479}.s-sin-fuente{color:#6b7280}
@media(max-width:700px){td:nth-child(n+6),th:nth-child(n+6){display:none}}"""

JS = """function flt(){const p=document.getElementById('fp').value,s=document.getElementById('fs').value,q=document.getElementById('fq').value.toLowerCase();
document.querySelectorAll('[data-pais]').forEach(r=>{const ok=(!p||r.dataset.pais===p)&&(!s||(' '+r.dataset.senales+' ').includes(' '+s+' '))&&(!q||r.textContent.toLowerCase().includes(q));r.style.display=ok?'':'none'})}"""


def render(d: dict, *, refresh: int = 30) -> str:
    now = d["now"]
    pst, pdet = d["bot"]
    c = d["counts"]
    o = [f"<!doctype html><html lang=es><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
         f"<meta http-equiv=refresh content={refresh}><title>Panel de tiendas · cookgroup</title><style>{CSS}</style><main>",
         "<h1>Panel de tiendas</h1>", "<p><a href='FIDELIDAD.html'>→ Fidelidad con la referencia, por categoría (339 canales)</a></p>", f"<p class=muted>Actualizado {_mad(now)} (Madrid) · se recarga solo cada {refresh} s</p>"]
    if d["demo"]:
        o.append("<div class='banner demo'>DEMO · el bot aún no ha leído ninguna tienda desde esta carpeta y el servidor no está "
                 "instalado. Lo que ves sale de las pruebas locales con datos reales capturados; los estados en directo aparecen al "
                 "arrancar ARRANCAR.bat.</div>")
    o.append(f"<div id=stale class='banner bad' style=display:none></div>"
             f"<div class='banner {'ok' if pst == 'EN MARCHA' else 'bad'}'>BOT {E(pst)} — {E(pdet)}</div>")
    o.append(f"<script>const GEN={int(now * 1000)};setInterval(chk,5000);function chk(){{const m=Math.round((Date.now()-GEN)/60000);"
             f"if(Date.now()-GEN>120000){{const e=document.getElementById('stale');e.style.display='';e.textContent='Este panel no se "
             f"actualiza desde hace '+m+' min: el bot está PARADO o el ordenador apagado. Los estados de abajo son de la última vez que funcionó.'}}}}"
             f"window.addEventListener('load',chk)</script>")
    o.append("<div class=k>" + "".join(f"<div><span class=muted>{a}</span><b>{b}</b><span class=muted>{s}</span></div>" for a, b, s in (
        ("Tiendas descubiertas", c["descubiertas"], "comercios únicos del inventario"),
        ("Con fuente validada", c["fuente_validada"], "lectura buena o señal probada"),
        ("Instaladas en Discord", c["instaladas"], "canal propio creado"),
        ("Con entrega verificada", c["entrega_verificada"], "mensaje real confirmado"))) + "</div>")
    countries = sorted({s["pais"] for s in d["stores"]} | {r["pais"] for r in d["directory"] if r["pais"]},
                       key=lambda x: (EU_ORDER.index(x) if x in EU_ORDER else 99, x))
    o.append("<div class=f><select id=fp onchange=flt()><option value=''>Todos los países</option>" +
             "".join(f"<option>{E(x)}</option>" for x in countries) + "</select><select id=fs onchange=flt()><option value=''>Todas las señales</option>" +
             "".join(f"<option value={s}>{s.upper()}</option>" for s in SIGNALS) +
             "</select><input id=fq placeholder='Buscar tienda' oninput=flt()></div>")
    o.append("<h2>Tiendas con canal propio (lote 1)</h2><table><tr><th>Tienda</th><th>Estado</th><th>Ritmo</th>"
             "<th>Última lectura buena</th><th>Próximo intento</th><th>Último raffle / aviso</th><th>Señales</th><th>Canal</th></tr>")
    for s in d["stores"]:
        sig = " ".join(k for k, v in s["senales"].items() if v == "probado")
        rf = s["ultimo_raffle"]
        av = s["ultimo_aviso"]
        last = (f"🎟️ {_mad(rf['detected_ts'])} · <a href='{E(rf['jump_url'])}'>Ver mensaje</a> · {rf['detect_to_send_ms']} ms" if rf and rf.get("jump_url")
                else f"🎟️ {_mad(rf['detected_ts'])}" if rf else
                f"{_mad(av[2])}" + (f" · <a href='https://discord.com/channels/{d['guild']}/{d['ids'].get(s['canal'])}/{av[3]}'>Ver mensaje</a>"
                                    if d["guild"] and d["ids"].get(s["canal"]) else "") if av else "—")
        nxt = f"{_mad(s['proximo'])}<br><span class=muted>{E(s['motivo_espera'] or '')}</span>" if s["proximo"] else "—"
        err = f"<br><span class=muted>{E(str(s['ultimo_error'] or '')[:90])}</span>" if s["errores"] else ""
        chan = (f"<a href='{E(s['canal_url'])}'>#{E(s['canal'])}</a>" if s["canal_url"] else
                f"#{E(s['canal'])} <span class=muted>({'webhook listo' if s['instalado'] else 'sin instalar'})</span>")
        o.append(f"<tr data-pais='{E(s['pais'])}' data-senales='{sig}'><td><b>{FLAGS.get(s['pais'], '')} {E(s['nombre'])}</b><br>"
                 f"<span class=muted>envío ES: {E(s['envio_es'] or '—')}</span></td><td><span class='tag {s['clase']}'>{E(s['estado'])}</span>{err}</td>"
                 f"<td>cada {s['intervalo_s']} s</td><td>{_mad(s['ultima_ok'])}<br><span class=muted>{_ago(s['ultima_ok'], now)}</span></td>"
                 f"<td>{nxt}</td><td>{last}</td><td>" + " ".join(f"<span class=s-{v}>{k[:4].upper()}</span>" for k, v in s["senales"].items())
                 + f"</td><td>{chan}</td></tr>")
    o.append("</table><p class=muted>Señales: verde = activa (probada con datos reales) · amarillo = en prueba, no se publica · gris = la tienda "
             "no lo ofrece por una vía pública. El ritmo real puede variar ±10 % y se alarga si la tienda pide esperar.</p>")
    if d["pruebas"]:
        o.append("<h2>Pruebas en #pruebas-bot</h2><table><tr><th>Cuándo</th><th>Detección → envío</th><th>Detección → Discord</th><th>Mensaje</th></tr>")
        for t in d["pruebas"]:
            link = f"<a href='{E(t['jump_url'])}'>Ver mensaje</a>" if t["jump_url"] else E(str(t["message_id"]))
            o.append(f"<tr><td>{_mad(t['detected_ts'])}</td><td>{t['detect_to_send_ms']} ms</td><td>{t['detect_to_discord_ms']} ms</td>"
                     f"<td>{link}</td></tr>")
        o.append("</table>")
    o.append(f"<h2>Directorio de tiendas ({len(d['directory'])} comercios únicos)</h2><table><tr><th>Tienda</th><th>País</th><th>Nivel</th>"
             "<th>Envío a España</th><th>Monitores</th><th>Filas en inventario</th></tr>")
    for r in d["directory"]:
        cid = d["ids"].get(r["canal"]) if r["canal"] else None
        name = (f"<a href='https://discord.com/channels/{d['guild']}/{cid}'>{E(r['nombre'])}</a>" if cid and d["guild"] else E(r["nombre"]))
        lvl = "operativa" if cid and r["nivel"] == "piloto" and c["entrega_verificada"] else r["nivel"]
        o.append(f"<tr data-pais='{E(r['pais'])}' data-senales='{' '.join(r['senales'])}'><td>{name}<br><span class=muted>{E(', '.join(r['dominios'][:3]))}</span></td>"
                 f"<td>{FLAGS.get(r['pais'], '')} {E(r['pais'] or '—')}</td><td><span class='tag {'ok' if lvl != 'descubierta' else 'warn'}'>{lvl}</span></td>"
                 f"<td>{E(r['envio_es'])}</td><td>{len(r['monitores'])}</td><td>{r['filas_inventario']}"
                 + (f" <span class=muted>({r['duplicadas']} duplicada{'s' if r['duplicadas'] != 1 else ''})</span>" if r["duplicadas"] else "") + "</td></tr>")
    o.append(f"</table></main><script>{JS}</script></html>")
    return "\n".join(o)


def write_store_panel(store, cfg, path=OUT, **kw) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = collect(store, cfg, **kw)
    p.write_text(render(data), encoding="utf-8")
    (p.parent / "panel_tiendas.json").write_text(json.dumps({k: v for k, v in data.items() if k != "directory"}, default=str,
                                                            ensure_ascii=False, indent=1), encoding="utf-8")
    return p
