"""Panel del dueño (v0.9): responder en un minuto cómo va el negocio. Lo usan la web local (/admin) y el panel estático."""
from __future__ import annotations

import csv
import html
import time
import tomllib
from pathlib import Path

from .web_util import madrid

E = html.escape


def eur(c):
    return f"{(c or 0) / 100:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def render_owner(b, roles_api=None, *, now=None, tasks_file="config/tareas_editoriales.toml", live=False, pin="",
                 deliveries_csv="docs/v09/ENTREGAS_REALES.csv", store_health=None, intervals=None,
                 channels_expected: list | None = None, support=None) -> str:
    now = now or time.time()
    s = b.summary(now=now)
    an = b.anomalies(roles_api, now=now)
    plan = next(iter(b.plans.values()), None)
    est = (s["real"]["miembros_de_pago"] + s["prueba"]["miembros_de_pago"]) * (plan.price_cents if plan else 0)

    def k(label, val, sub=""):
        return f"<div><span class=muted>{E(label)}</span><b>{E(str(val))}</b><span class=muted>{E(sub)}</span></div>"

    def block(lbl, d):
        return (f"<h3>{lbl}</h3><div class=k>" + k("Miembros de pago", d["miembros_de_pago"]) + k("Altas (30 días)", d["altas"])
                + k("Renovaciones", d["renovaciones"]) + k("Bajas", d["bajas"], f" · {d['cancelaciones_programadas']} cancelan al vencer")
                + k("Cobrado (30 días)", eur(d["cobrado_cents"])) + k("Ingreso mensual recurrente", eur(d["mrr_cents"]))
                + k("Cobros fallidos", d["cobros_fallidos"]) + "</div>")

    out = ["<h1>Panel del dueño</h1>", f"<p class=muted>Actualizado {madrid(now)} (Madrid)</p>",
           "<h2>1 · Miembros e ingresos</h2>", block("Cifras REALES (cobros de verdad)", s["real"]),
           block("Cifras DE PRUEBA (Stripe en modo prueba o simulador)", s["prueba"]),
           f"<p class=muted>ESTIMADO: si todos los miembros con acceso pagaran el plan actual, {eur(est)}/mes. No es dinero cobrado.</p>"]
    bad = an["pagado_sin_acceso"] + an["acceso_sin_derecho"]
    out.append("<h2>2 · Accesos que no cuadran</h2>")
    if not bad:
        out.append("<p><span class='tag ok'>todo cuadra</span> nadie ha pagado sin acceso y nadie tiene acceso vencido.</p>")
    for did, why in an["pagado_sin_acceso"]:
        out.append(f"<div class=card><span class='tag bad'>PAGADO SIN ACCESO</span> {E(did)} — {E(why)} {_retry(did, live, pin)}</div>")
    for did, why in an["acceso_sin_derecho"]:
        out.append(f"<div class=card><span class='tag bad'>ACCESO SIN DERECHO</span> {E(did)} — {E(why)} {_retry(did, live, pin)}</div>")
    out.append("<h2>3 · Alertas y fuentes</h2>")
    rows = []
    if Path(deliveries_csv).exists():
        rows = list(csv.DictReader(open(deliveries_csv, encoding="utf-8")))
    conf = [r for r in rows if r["estado"] == "entrega real confirmada"]
    out.append(f"<p>Entregas reales confirmadas en tu Discord: <b>{len(conf)}</b>"
               + (f" · última {E(conf[-1]['fecha_utc'])} en #{E(conf[-1]['canal'])} (mensaje {E(conf[-1]['message_id'])})" if conf else
                  " · <span class='tag'>ninguna todavía</span>") + "</p>")
    if store_health is not None:
        from .diagnostics import lag_label
        late = [(src, lag_label(last_ok, (intervals or {}).get(src, 600))) for src, last_ok, *_ in store_health]
        late = [x for x in late if x[1] != "AL DÍA"]
        out.append(f"<p>Fuentes con retraso o sin lectura: <b>{len(late)}</b></p>" + "".join(
            f"<div class=muted>{E(a)} · {E(b_)}</div>" for a, b_ in late[:15]))
    act = b.s.channel_activity() if hasattr(b.s, "channel_activity") else []
    if channels_expected:
        seen = {c for c, *_ in act}
        out.append("<table><tr><th>Canal</th><th>Último aviso</th><th>Avisos 7 días</th><th>Estado</th></tr>" + "".join(
            f"<tr><td>#{E(c)}</td><td>{madrid(t)}</td><td>{n}</td><td>{'✅' if n else '<span class=\'tag bad\'>SIN DATOS 7 DÍAS</span>'}</td></tr>"
            for c, t, n in act) + "".join(f"<tr><td>#{E(c)}</td><td>—</td><td>0</td><td><span class='tag bad'>NUNCA HA RECIBIDO</span></td></tr>"
                                         for c in channels_expected if c not in seen) + "</table>")
    last = b._q("SELECT store, MAX(sent_at), message_id FROM alerts WHERE message_id IS NOT NULL GROUP BY store ORDER BY 2 DESC LIMIT 10")
    if last:
        out.append("<table><tr><th>Tienda/canal</th><th>Último aviso entregado</th><th>Mensaje</th></tr>" + "".join(
            f"<tr><td>{E(a)}</td><td>{madrid(t)}</td><td>{E(str(m))}</td></tr>" for a, t, m in last) + "</table>")
    out.append("<h2>4 · Requiere atención</h2>")
    tickets = b._q("SELECT id, discord_id, subject, opened_at FROM tickets WHERE status='abierto' ORDER BY opened_at")
    if support is not None:                              # hilos privados de #soporte leídos con el bot
        try:
            tickets = [(t["id"], t["owner"], t["name"], t["last_at"]) for t in support() if t["needs_reply"]]
        except Exception as e:   # noqa: BLE001
            out.append(f"<p class=muted>No se pudieron leer los tickets de Discord: {E(str(e))}</p>")
    fails = b._q("SELECT discord_id, amount_cents, at FROM payments WHERE status='fallido' ORDER BY at DESC LIMIT 10")
    pend = b._q("SELECT discord_id, attempts, last_error FROM role_sync WHERE status='pendiente'")
    tasks = []
    if Path(tasks_file).exists():
        tasks = [t for t in tomllib.loads(Path(tasks_file).read_text(encoding="utf-8")).get("tarea", []) if t.get("estado") != "hecha"]
    out.append(f"<p>Tickets que necesitan respuesta: <b>{len(tickets)}</b> · cobros fallidos: <b>{len(fails)}</b> · sincronizaciones pendientes: "
               f"<b>{len(pend)}</b> · tareas editoriales: <b>{len(tasks)}</b></p>")
    for t in tickets:
        out.append(f"<div class=card>🎫 #{t[0]} · {E(t[1])} · {E(t[2])} · abierto {madrid(t[3])}</div>")
    for d, a, at in fails:
        out.append(f"<div class=card>💳 Cobro fallido · {E(str(d))} · {eur(a)} · {madrid(at)}</div>")
    for t in tasks:
        out.append(f"<div class=card>📝 {E(t['titulo'])} · responsable: {E(t.get('responsable', '—'))} · para {E(t.get('fecha', '—'))}</div>")
    out.append("<h2>5 · Fichas de miembro</h2><table><tr><th>Miembro</th><th>Plan</th><th>Modo</th><th>Vigencia</th><th>Derecho</th>"
               "<th>Rol</th><th>Sincronización</th><th></th></tr>")
    for (did,) in b._q("SELECT discord_id FROM members ORDER BY linked_at"):
        c = b.member_card(did, now=now)
        sync = f"{c['sincronizacion']} · {madrid(c['ultima_sincronizacion'])}" + (f" · {c['intentos']} intentos · {c['ultimo_error']}" if c["ultimo_error"] else "")
        out.append(f"<tr><td>{E(c['usuario'] or '')}<br><span class=muted>{E(did)}</span></td><td>{E(c['plan'] or '—')}</td><td>{E(c['modo'] or '—')}</td>"
                   f"<td>{madrid(c['vigente_hasta'])}{' · cancela' if c['cancela_al_vencer'] else ''}</td>"
                   f"<td>{'✅' if c['derecho'] else '—'} {E(c['motivo'])}</td><td>{'✅' if c['rol_en_discord'] else '—'}</td>"
                   f"<td>{E(sync)}</td><td>{_retry(did, live, pin)}</td></tr>")
    out.append("</table><h2>6 · Registro de acciones</h2><table><tr><th>Cuándo</th><th>Quién</th><th>Acción</th><th>Miembro</th><th>Detalle</th></tr>")
    for at, actor, action, target, detail in b._q("SELECT * FROM audit ORDER BY at DESC LIMIT 25"):
        out.append(f"<tr><td>{madrid(at)}</td><td>{E(actor)}</td><td>{E(action)}</td><td>{E(target)}</td><td>{E(detail or '')}</td></tr>")
    out.append("</table>")
    return "\n".join(out)


def _retry(did, live, pin):
    if live:
        return (f"<form method=post action='/admin/reintentar?pin={E(pin)}' style=display:inline><input type=hidden name=d value='{E(did)}'>"
                f"<button class='btn g'>Reintentar sincronización</button></form>")
    return f"<code>cookgroup cuenta --reintentar {E(did)}</code>"
