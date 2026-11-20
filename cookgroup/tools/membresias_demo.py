"""Recorrido completo de la venta de membresías en PRUEBA LOCAL (sin claves, sin red, sin cobros).

Por la web local real (HTTP): página de venta → vincular Discord (identidad de prueba) → pago (simulador con firma de
Stripe) → rol «Suscriptor activo» → bienvenida → acceso a canales → cuenta → cancelación → retirada al vencer.
Casos: visitante que no paga, pago fallido, renovación, evento duplicado, firma falsa y «ha pagado pero Discord estaba
caído» (recuperado desde el panel del dueño, con registro de la acción).
Uso: python tools/membresias_demo.py → docs/v09/MEMBRESIAS_REGISTRO.md y docs/v09/PANEL_DUENO_demo.html
"""
from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ["NO_PROXY"] = os.environ["no_proxy"] = "127.0.0.1,localhost"
os.chdir(ROOT)

import requests  # noqa: E402

from cookgroup.access import SUB, VIEW, can, channel_overwrites, effective  # noqa: E402
from cookgroup.billing import Billing, load_plans  # noqa: E402
from cookgroup.store import Store  # noqa: E402
from cookgroup.web import App, serve  # noqa: E402

DAY = 86400


class FakeDiscordRoles:
    """Servidor de Discord simulado: rol «Suscriptor activo», mensajes de bienvenida y posibilidad de caída."""
    def __init__(self):
        self.members: dict[str, set] = {}
        self.down, self.welcomed = False, []

    def _chk(self):
        if self.down:
            raise RuntimeError("Discord no responde (503, simulado)")

    def add_role(self, uid):
        self._chk(); self.members.setdefault(uid, set()).add(SUB)

    def remove_role(self, uid):
        self._chk(); self.members.setdefault(uid, set()).discard(SUB)

    def has_role(self, uid):
        return SUB in self.members.get(uid, set())

    def holders(self):
        return [u for u, r in self.members.items() if SUB in r]

    def welcome(self, uid):
        self._chk(); self.welcomed.append(uid)

    def sees(self, uid, audiencia="suscriptores"):
        return can(effective(self.members.get(uid, set()) | {"Nike", "EU 44,5"}, channel_overwrites(audiencia, "lectura")), VIEW)


def snapshot(b, dc, now, name, note):
    from cookgroup.owner_panel import render_owner
    from cookgroup.web import CSS
    html = (f"<!DOCTYPE html><html lang=es><head><meta charset=utf-8><title>Panel del dueño (demo)</title><style>{CSS}</style></head>"
            f"<body><div class=w><div class=muted>{note} · PRUEBA LOCAL: no son clientes reales</div>"
            + render_owner(b, dc, now=now, deliveries_csv=str(ROOT / "docs/v09/ENTREGAS_REALES.csv")) + "</div></body></html>")
    (ROOT / "docs/v09").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/v09" / name).write_text(html, encoding="utf-8")


def run(log=print) -> dict:
    tmp = Path(tempfile.mkdtemp())
    clock = {"t": time.time()}
    b = Billing(Store(str(tmp / "membresias.db")), load_plans(ROOT / "config/planes.toml"))
    dc = FakeDiscordRoles()
    app = App(b, dc, env={"SESSION_SECRET": "demo"}, clock=lambda: clock["t"])
    pin = "1234"
    srv = serve(app, pin, port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}"
    steps, ok_all = [], True

    def check(name, cond, detail):
        nonlocal ok_all
        ok_all &= bool(cond)
        steps.append((name, "OK" if cond else "FALLA", detail))
        log(f"[{'OK' if cond else 'FALLA'}] {name}: {detail}")

    def client():
        return requests.Session()

    def signup(s, did, name):
        s.get(base + "/")
        s.post(base + "/alta", data={"discord_id": did, "username": name})
        s.get(base + "/pagar")
        return s.post(base + "/simular", data={"r": "ok"})

    # --- usuario 1: VISITANTE
    v = client()
    r = v.get(base + "/")
    check("1. Visitante abre la página de venta", r.status_code == 200 and "19,99" in r.text.replace(".", ","),
          "ve el plan, el precio (19,99 €/mes), qué incluye y las condiciones")
    v.post(base + "/alta", data={"discord_id": "200000000000000001", "username": "Visitante de prueba"})
    check("2. Visitante sin pagar: solo zona pública", not dc.sees("200000000000000001") and dc.sees("200000000000000001", "todos"),
          "ve bienvenida, planes, muestra y soporte; no ve los canales de pago")

    # --- usuario 2: SUSCRIPTOR (recorrido completo)
    s = client()
    r = signup(s, "200000000000000002", "Javi (prueba)")
    card = b.member_card("200000000000000002", now=clock["t"])
    check("3. Alta: vincula Discord → pago de prueba → rol", card["derecho"] and dc.has_role("200000000000000002"),
          f"pago simulado con firma de Stripe; rol «Suscriptor activo» concedido; vigente hasta {card['vigente_hasta']}")
    check("4. Bienvenida enviada una sola vez", dc.welcomed.count("200000000000000002") == 1, "mensaje privado de bienvenida")
    check("5. Acceso a los canales contratados", dc.sees("200000000000000002"), "ahora ve #sneakers-eu, #lanzamientos, #raffles…")
    r = s.get(base + "/cuenta")
    check("6. El cliente ve su suscripción", "rol «Suscriptor activo» concedido" in r.text, "página /cuenta: estado, vigencia y botón de cancelar")
    s.post(base + "/cancelar")
    check("7. Cancela: mantiene el acceso hasta el fin del periodo", b.entitled("200000000000000002", clock["t"])[0]
          and dc.has_role("200000000000000002"), b.entitled("200000000000000002", clock["t"])[1])
    cus, sub = app.subs_by_member["200000000000000002"]
    clock["t"] += 31 * DAY
    body, sig = app.sim.event("customer.subscription.deleted", app.sim.sub_obj(sub, cus, "200000000000000002", "canceled",
                                                                                clock["t"] - DAY, True), clock["t"])
    app.process(body, sig, simulated=True)
    check("8. Al vencer se retira el acceso", not dc.has_role("200000000000000002") and not dc.sees("200000000000000002"),
          "rol retirado; conserva preferencias (Nike, EU 44,5) pero ya no ve los canales de pago")

    # --- usuario 3: pagó con Discord caído → recuperación desde el panel
    dc.down = True
    signup(client(), "200000000000000003", "Pago con Discord caído")
    an = b.anomalies(dc, now=clock["t"])
    check("9. Ha pagado pero Discord estaba caído → aparece en el panel", any(d == "200000000000000003" for d, _ in an["pagado_sin_acceso"]),
          "«PAGADO SIN ACCESO» con el error; sincronización pendiente")
    snapshot(b, dc, clock["t"], "PANEL_DUENO_demo.html",
             "DEMO · INCIDENCIA ABIERTA: un cliente ha pagado mientras Discord estaba caído (fecha simulada del recorrido)")
    dc.down = False
    requests.post(base + f"/admin/reintentar?pin={pin}", data={"d": "200000000000000003"})
    hist = b.member_card("200000000000000003", now=clock["t"])["historial"]
    check("10. El dueño pulsa «Reintentar» → acceso recuperado y anotado", dc.has_role("200000000000000003")
          and any(a == "dueño (panel)" and act == "rol concedido" for _, a, act, _ in hist),
          "rol concedido; queda en el registro como acción del dueño")
    signup(client(), "200000000000000006", "Recuperación automática") if not dc.down else None
    dc.down = True
    signup(client(), "200000000000000007", "Pago con Discord caído (2)")
    dc.down = False
    from cookgroup.web import auto_reconcile_once
    auto_reconcile_once(app)
    check("10b. …o se recupera solo en la siguiente pasada automática (cada 5 min)", dc.has_role("200000000000000007"),
          "sin intervención: la pasada periódica concede el rol pendiente")
    check("11. Panel protegido por PIN", requests.get(base + "/admin?pin=mal").status_code == 403, "sin PIN: 403")

    # --- usuario 4: renovación + evento duplicado
    did4 = "200000000000000004"
    signup(client(), did4, "Renueva")
    cus4, sub4 = app.subs_by_member[did4]
    clock["t"] += 30 * DAY
    paid = app.sim.event("invoice.paid", {"id": "in_renov_1", "customer": cus4, "subscription": sub4, "amount_paid": 1999,
                                          "currency": "eur", "billing_reason": "subscription_cycle"}, clock["t"], eid="evt_renov_1")
    upd = app.sim.event("customer.subscription.updated", app.sim.sub_obj(sub4, cus4, did4, "active", clock["t"] + 30 * DAY), clock["t"])
    app.process(*paid, simulated=True); app.process(*upd, simulated=True)
    check("12. Renovación: nuevo periodo y cobro de renovación", b.entitled(did4, clock["t"] + 20 * DAY)[0]
          and b.summary(now=clock["t"])["prueba"]["renovaciones"] == 1, "acceso hasta el nuevo fin de periodo")
    dup = app.process(*app.sim.event("invoice.paid", {"id": "in_renov_1", "customer": cus4, "amount_paid": 1999,
                                                      "billing_reason": "subscription_cycle"}, clock["t"], eid="evt_renov_1"), simulated=True)
    check("13. Evento duplicado: se ignora", dup.startswith("duplicado") and b.summary(now=clock["t"])["prueba"]["renovaciones"] == 1,
          "Stripe repite el mismo evento: no se cuenta dos veces")
    r = requests.post(base + "/stripe/webhook", data=b'{"id":"evt_falso"}', headers={"Stripe-Signature": "t=1,v1=abc"})
    check("14. Evento con firma falsa: rechazado", r.status_code == 400, r.text)

    # --- usuario 5: pago fallido en la renovación
    did5 = "200000000000000005"
    signup(client(), did5, "Tarjeta caducada")
    cus5, sub5 = app.subs_by_member[did5]
    end5 = b._q("SELECT current_period_end FROM subscriptions WHERE id=?", (sub5,))[0][0]
    clock["t"] = end5 + 3600
    app.process(*app.sim.event("invoice.payment_failed", {"id": "in_fail_5", "customer": cus5, "amount_due": 1999,
                                                          "billing_reason": "subscription_cycle"}, clock["t"]), simulated=True)
    app.process(*app.sim.event("customer.subscription.updated", app.sim.sub_obj(sub5, cus5, did5, "past_due", end5), clock["t"]), simulated=True)
    check("15. Pago fallido: acceso durante la gracia", b.entitled(did5, clock["t"])[0] and dc.has_role(did5),
          b.entitled(did5, clock["t"])[1])
    clock["t"] = end5 + 4 * DAY
    b.reconcile(dc, now=clock["t"])
    check("16. Gracia agotada: acceso retirado", not dc.has_role(did5), b.entitled(did5, clock["t"])[1])
    an = b.anomalies(dc, now=clock["t"])
    check("17. Al final, nada descuadrado", not an["pagado_sin_acceso"] and not an["acceso_sin_derecho"], "panel: todo cuadra")
    srv.shutdown()
    snapshot(b, dc, clock["t"], "PANEL_DUENO_final.html", "DEMO · AL TERMINAR EL RECORRIDO (fecha simulada)")
    return {"ok": ok_all, "steps": steps, "summary": b.summary(now=clock["t"])}


def write_log(res, path=ROOT / "docs/v09/MEMBRESIAS_REGISTRO.md"):
    now = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d/%m/%Y %H:%M")
    L = [f"# Membresías en PRUEBA LOCAL (ejecutado {now}, Madrid)", "",
         "Web local real (HTTP) + simulador de Stripe (eventos firmados como Stripe, livemode=false) + Discord simulado.",
         "No se cobra nada y no se toca Discord.", "", f"Resultado: **{'TODO OK' if res['ok'] else 'HAY FALLOS'}**", "",
         "| Paso | Resultado | Detalle |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in res["steps"]]
    L += ["", f"Cifras de prueba al terminar: {res['summary']['prueba']}", "", "Repetir: `python tools/membresias_demo.py`"]
    path.write_text("\n".join(L), encoding="utf-8")
    return path


if __name__ == "__main__":
    r = run()
    print(write_log(r))
    sys.exit(0 if r["ok"] else 1)
