"""Web local del cookgroup (v0.9): venta → vincular Discord → pago (prueba) → cuenta del cliente → panel del dueño.

Modos (se eligen solos según tu .env):
  · PRUEBA LOCAL: sin claves. Discord se vincula con una identidad de prueba y el pago lo hace un simulador que emite
    eventos con el mismo formato y firma que Stripe. Nada sale de tu PC.
  · STRIPE PRUEBA: STRIPE_SECRET_KEY=sk_test_… + STRIPE_PRICE_MENSUAL + STRIPE_WEBHOOK_SECRET y la app OAuth de
    Discord (DISCORD_CLIENT_ID/SECRET). Pagos con tarjetas de prueba de Stripe; no se cobra nada.
  · Cobros reales (sk_live_): bloqueados hasta que actives COBROS_REALES=si en .env tras revisar la oferta.
Arranque: PANEL_DUENO.bat (cookgroup web) → http://127.0.0.1:8765
"""
from __future__ import annotations

import hashlib
import hmac
import html
import json
import os
import secrets
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse
from zoneinfo import ZoneInfo

from .billing import BadSignature, Billing, StripeSimulator, verify

E = html.escape
MAD = ZoneInfo("Europe/Madrid")
CSS = """body{margin:0;font:16px/1.5 system-ui,Segoe UI,Roboto,sans-serif;background:#0f1115;color:#e8e9ec}
.w{max-width:980px;margin:auto;padding:24px 18px 60px}h1{font-size:30px;margin:6px 0 4px}h2{font-size:19px;margin:26px 0 8px}
a{color:#7aa7ff}.btn{display:inline-block;background:#3b82f6;color:#fff;border:0;border-radius:8px;padding:11px 18px;font-size:16px;cursor:pointer;text-decoration:none}
.btn.g{background:#2b2f38}.btn.r{background:#b42318}.card{background:#181b22;border:1px solid #2a2f3a;border-radius:10px;padding:14px 16px;margin:10px 0}
.tag{font-size:12px;font-weight:700;padding:2px 7px;border-radius:5px;background:#fde68a;color:#111}.tag.ok{background:#86efac}.tag.bad{background:#fca5a5}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #2a2f3a;padding:7px 6px;text-align:left;vertical-align:top}
.k{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.k div{background:#181b22;border-radius:10px;padding:12px}.k b{font-size:24px;display:block}
input{background:#0b0d11;color:#e8e9ec;border:1px solid #3a4150;border-radius:7px;padding:9px;font-size:16px}.muted{color:#9aa3b2;font-size:14px}"""


from .web_util import madrid  # noqa: E402


class App:
    def __init__(self, billing: Billing, roles_api, *, env=os.environ, clock=time.time, plan_id="mensual"):
        self.b, self.roles, self.env, self.now, self.plan = billing, roles_api, env, clock, billing.plans[plan_id]
        self.session_secret = env.get("SESSION_SECRET") or secrets.token_hex(16)
        self.sim_secret = "whsec_simulador_local"
        self.sim = StripeSimulator(self.sim_secret, self.plan.price_cents)
        self.stripe = None
        key = env.get("STRIPE_SECRET_KEY", "")
        if key and (key.startswith("sk_test_") or env.get("COBROS_REALES", "").lower() == "si"):
            from .billing import StripeAPI
            self.stripe = StripeAPI(key)
        self.oauth = bool(env.get("DISCORD_CLIENT_ID") and env.get("DISCORD_CLIENT_SECRET"))
        self.subs_by_member: dict[str, tuple[str, str]] = {}      # simulador: discord_id → (cus, sub)
        self.tasks_file = env.get("TAREAS_FILE", "config/tareas_editoriales.toml")

    @property
    def mode(self) -> str:
        if self.stripe and self.stripe.live:
            return "COBROS REALES"
        return "STRIPE PRUEBA" if self.stripe else "PRUEBA LOCAL (simulador de Stripe)"

    # --- sesión firmada (cookie)
    def cookie_for(self, did: str) -> str:
        return f"{did}.{hmac.new(self.session_secret.encode(), did.encode(), hashlib.sha256).hexdigest()[:32]}"

    def who(self, cookie_header: str | None) -> str | None:
        for part in (cookie_header or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "cg" and "." in v:
                did, sig = v.rsplit(".", 1)
                if hmac.compare_digest(self.cookie_for(did).rsplit(".", 1)[1], sig):
                    return did
        return None

    # --- procesado de eventos (mismo camino para Stripe real y simulador)
    def process(self, body: bytes, sig: str, *, simulated: bool) -> str:
        secret = self.sim_secret if simulated else self.env.get("STRIPE_WEBHOOK_SECRET", "")
        ev = verify(body, sig, secret, now=self.now())
        res = self.b.handle(ev, now=self.now())
        did = (ev["data"]["object"].get("metadata") or {}).get("discord_id") or ev["data"]["object"].get("client_reference_id")
        if did and not res.startswith("duplicado"):
            self.b.reconcile(self.roles, now=self.now(), only=did)
        return res

    def page(self, title: str, body: str) -> str:
        return (f"<!DOCTYPE html><html lang=es><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
                f"<title>{E(title)}</title><style>{CSS}</style></head><body><div class=w><div class=muted>Modo: <b>{E(self.mode)}</b></div>{body}</div></body></html>")

    # --- páginas
    def sales(self) -> str:
        import tomllib
        from pathlib import Path
        inc = tomllib.loads(Path("config/planes.toml").read_text(encoding="utf-8"))["plan"][self.plan.id].get("incluye", [])
        return self.page("Suscripción", f"""<h1>Drops Shoes Madrid</h1><p>Avisos de restocks, lanzamientos, raffles y rebajas para
España y Europa, filtrados por tu talla y tus marcas.</p><div class=card><h2>{E(self.plan.name)} · {self.plan.price_cents / 100:.2f} €/mes</h2>
<ul>{''.join(f'<li>{E(x)}</li>' for x in inc)}</ul><p class=muted>Sin permanencia. Si cancelas, mantienes el acceso hasta el final del periodo pagado.
Si falla un cobro, mantienes el acceso {self.plan.grace_days} días mientras se reintenta. Antes de pagar puedes ver ejemplos reales en #muestra-gratis.</p>
<a class=btn href=/alta>Darme de alta</a></div>""")

    def link_form(self) -> str:
        if self.oauth:
            q = urlencode({"client_id": self.env["DISCORD_CLIENT_ID"], "redirect_uri": self.env.get("DISCORD_REDIRECT_URI", "http://127.0.0.1:8765/oauth/callback"),
                           "response_type": "code", "scope": "identify"})
            return self.page("Vincular Discord", f"<h1>1 · Vincula tu cuenta de Discord</h1><p>Así sabremos a quién dar acceso.</p>"
                                                 f"<a class=btn href='https://discord.com/oauth2/authorize?{q}'>Entrar con Discord</a>")
        return self.page("Vincular Discord", """<h1>1 · Vincula tu cuenta de Discord</h1><p class=muted>PRUEBA LOCAL: sin la app OAuth de Discord
se usa una identidad de prueba.</p><form method=post action=/alta><p><input name=discord_id placeholder="ID de Discord (números)" required>
<input name=username placeholder="Nombre" required></p><button class=btn>Continuar al pago</button></form>""")

    def pay(self, did: str) -> tuple[str, str | None]:
        if self.stripe:
            price = self.env.get(self.plan.stripe_price_env, "")
            base = self.env.get("PUBLIC_URL", "http://127.0.0.1:8765")
            return "", self.stripe.checkout(price, did, f"{base}/cuenta", f"{base}/")
        return self.page("Pago de prueba", f"""<h1>2 · Pago</h1><div class=card><p><b>{E(self.plan.name)}</b> · {self.plan.price_cents / 100:.2f} €/mes</p>
<p class=muted>SIMULADOR: no se cobra nada. Emite los mismos eventos firmados que enviaría Stripe.</p>
<form method=post action=/simular><input type=hidden name=r value=ok><button class=btn>Pagar (prueba)</button></form><br>
<form method=post action=/simular><input type=hidden name=r value=fallo><button class="btn g">Simular tarjeta rechazada</button></form></div>"""), None

    def simulate(self, did: str, result: str) -> None:
        now = self.now()
        if result == "ok":
            cus, sub, evs = self.sim.subscribe(did, now)
            self.subs_by_member[did] = (cus, sub)
            for body, sig in evs:
                self.process(body, sig, simulated=True)

    def account(self, did: str) -> str:
        c = self.b.member_card(did, now=self.now())
        st = "ok" if c["derecho"] else "bad"
        cancel = ("" if not c["derecho"] or c["cancela_al_vencer"] else
                  "<form method=post action=/cancelar><button class='btn r'>Cancelar suscripción</button></form>"
                  "<p class=muted>Mantendrás el acceso hasta el final del periodo pagado.</p>")
        return self.page("Mi cuenta", f"""<h1>Mi suscripción</h1><div class=card><p>Estado: <span class="tag {st}">{E(c['motivo'])}</span></p>
<p>Plan: {E(c['plan'] or '—')} · vigente hasta {madrid(c['vigente_hasta'])} (Madrid)</p>
<p>Acceso en Discord: {'✅ rol «Suscriptor activo» concedido' if c['rol_en_discord'] else '⏳ pendiente' if c['derecho'] else '—'}
{('<br><span class=muted>Estamos activando tu acceso; si tarda más de 10 minutos, abre un ticket en #soporte.</span>' if c['derecho'] and not c['rol_en_discord'] else '')}</p>
{cancel}</div>""")

    def cancel(self, did: str) -> None:
        if self.stripe:
            return
        cus, sub = self.subs_by_member[did]
        end = self.b._q("SELECT current_period_end FROM subscriptions WHERE id=?", (sub,))[0][0]
        body, sig = self.sim.event("customer.subscription.updated", self.sim.sub_obj(sub, cus, did, "active", end, cancel=True), self.now())
        self.process(body, sig, simulated=True)

    def admin(self, pin: str) -> str:
        from .owner_panel import render_owner
        return self.page("Panel del dueño", render_owner(self.b, self.roles, now=self.now(), tasks_file=self.tasks_file,
                                                         live=True, pin=pin))


def make_handler(app: App, pin: str):
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body="", ctype="text/html; charset=utf-8", headers=None):
            raw = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(raw)

        def _redir(self, to, cookie=None):
            h = {"Location": to}
            if cookie:
                h["Set-Cookie"] = f"cg={cookie}; HttpOnly; SameSite=Lax; Path=/"
            self._send(303, "", headers=h)

        def _form(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n)
            return raw, {k: v[0] for k, v in parse_qs(raw.decode(errors="replace")).items()}

        def _admin_ok(self, q):
            return hmac.compare_digest(q.get("pin", [""])[0], pin)

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            did = app.who(self.headers.get("Cookie"))
            if u.path == "/":
                return self._send(200, app.sales())
            if u.path == "/alta":
                return self._send(200, app.link_form())
            if u.path == "/oauth/callback" and app.oauth:
                import requests
                tok = requests.post("https://discord.com/api/v10/oauth2/token", data={
                    "client_id": app.env["DISCORD_CLIENT_ID"], "client_secret": app.env["DISCORD_CLIENT_SECRET"],
                    "grant_type": "authorization_code", "code": q.get("code", [""])[0],
                    "redirect_uri": app.env.get("DISCORD_REDIRECT_URI", "http://127.0.0.1:8765/oauth/callback")}).json()
                me = requests.get("https://discord.com/api/v10/users/@me",
                                  headers={"Authorization": f"Bearer {tok.get('access_token')}"}).json()
                app.b.link(me["id"], me.get("username", ""), now=app.now())
                return self._redir("/pagar", app.cookie_for(me["id"]))
            if u.path == "/pagar" and did:
                body, url = app.pay(did)
                return self._redir(url) if url else self._send(200, body)
            if u.path == "/cuenta" and did:
                return self._send(200, app.account(did))
            if u.path == "/admin":
                if not self._admin_ok(q):
                    return self._send(403, app.page("Acceso", "<h1>PIN incorrecto</h1>"))
                return self._send(200, app.admin(pin))
            if u.path in ("/pagar", "/cuenta"):
                return self._redir("/alta")
            self._send(404, app.page("No encontrado", "<h1>No encontrado</h1>"))

        def do_POST(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            raw, f = self._form()
            did = app.who(self.headers.get("Cookie"))
            if u.path == "/alta" and not app.oauth:
                if not f.get("discord_id", "").isdigit():
                    return self._send(400, app.page("Error", "<h1>ID de Discord no válido</h1>"))
                app.b.link(f["discord_id"], f.get("username", ""), now=app.now())
                return self._redir("/pagar", app.cookie_for(f["discord_id"]))
            if u.path == "/simular" and did and not app.stripe:
                app.simulate(did, f.get("r", "ok"))
                return self._redir("/cuenta" if f.get("r") == "ok" else "/pagar?rechazada=1")
            if u.path == "/cancelar" and did:
                app.cancel(did)
                return self._redir("/cuenta")
            if u.path == "/stripe/webhook":
                try:
                    res = app.process(raw, self.headers.get("Stripe-Signature", ""), simulated=False)
                except BadSignature as e:
                    return self._send(400, json.dumps({"error": str(e)}), "application/json")
                return self._send(200, json.dumps({"ok": res}), "application/json")
            if u.path == "/admin/reintentar" and self._admin_ok(q):
                app.b.reconcile(app.roles, now=app.now(), only=f.get("d"), actor="dueño (panel)")
                return self._redir(f"/admin?pin={pin}")
            self._send(404, "")

        def log_message(self, *a):
            pass
    return H


def serve(app: App, pin: str, port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(app, pin))


def auto_reconcile_once(app: App) -> list[dict]:
    """Pasada automática: concede accesos pendientes y retira los vencidos (la lanza `cookgroup web` cada 5 min)."""
    return app.b.reconcile(app.roles, now=app.now(), actor="sistema (pasada automática)")


def start_auto_reconcile(app: App, every: int = 300):
    import threading

    def loop():
        while True:
            try:
                auto_reconcile_once(app)
            except Exception:   # noqa: BLE001 — nunca tumbar la web
                pass
            time.sleep(every)
    threading.Thread(target=loop, daemon=True, name="reconcile").start()


class LocalRoles:
    """Sin bot: «Discord» local en memoria para probar la web en tu PC (se indica como SIMULADO en el panel)."""
    def __init__(self):
        self.m: set[str] = set()
        self.welcomed: list[str] = []

    def add_role(self, uid): self.m.add(uid)
    def remove_role(self, uid): self.m.discard(uid)
    def has_role(self, uid): return uid in self.m
    def holders(self): return list(self.m)
    def welcome(self, uid): self.welcomed.append(uid)
