"""Membresías de pago (v0.9): eventos de Stripe → estado de suscripción → rol «Suscriptor activo» en Discord.

Principios:
  · La firma de cada evento se verifica (esquema de Stripe: HMAC-SHA256 de "t.payload"; tolerancia 5 min).
  · Idempotente: un evento con el mismo id se ignora (Stripe reintenta y puede repetir).
  · El derecho de acceso se CALCULA (no se guarda a mano): activo/en prueba hasta el fin del periodo; impagado con
    periodo de gracia; cancelado al vencer. Cancelar = mantener acceso hasta el fin del periodo pagado.
  · La sincronización del rol puede fallar (Discord caído): queda «pendiente», se reintenta sola y se ve en el panel.
  · Cada acción del equipo (reintentar, conceder, retirar) queda en `audit`.
  · livemode=0 → cifras «de prueba»; livemode=1 → «reales». El panel nunca las mezcla.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ACTIVE = {"active", "trialing"}


def _iso(ts: float | None = None) -> str:
    return datetime.fromtimestamp(ts if ts is not None else time.time(), timezone.utc).isoformat(timespec="seconds")


@dataclass
class Plan:
    id: str
    name: str
    price_cents: int
    currency: str
    interval: str
    grace_days: int
    stripe_price_env: str


def load_plans(path: str | Path = "config/planes.toml") -> dict[str, Plan]:
    d = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return {k: Plan(k, v["nombre"], round(v["precio_eur"] * 100), "eur", v.get("intervalo", "month"),
                    int(v.get("gracia_dias", 3)), v.get("stripe_price_env", "STRIPE_PRICE_MENSUAL"))
            for k, v in d["plan"].items()}


# ------------------------------------------------------------------ firma de Stripe
class BadSignature(Exception):
    pass


def sign(payload: bytes, secret: str, ts: int | None = None) -> str:
    ts = ts or int(time.time())
    mac = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"


def verify(payload: bytes, header: str, secret: str, tolerance: int = 300, now: float | None = None) -> dict:
    try:
        parts = dict(x.split("=", 1) for x in header.split(","))
        ts = int(parts["t"])
    except (ValueError, KeyError) as e:
        raise BadSignature("cabecera Stripe-Signature mal formada") from e
    sigs = [v for k, v in (x.split("=", 1) for x in header.split(",")) if k == "v1"]
    expected = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, s) for s in sigs):
        raise BadSignature("firma no válida")
    if abs((now or time.time()) - ts) > tolerance:
        raise BadSignature("evento demasiado antiguo (posible repetición)")
    return json.loads(payload)


# ------------------------------------------------------------------ estado
class Billing:
    def __init__(self, store, plans: dict[str, Plan] | None = None):
        self.s, self.db = store, store.db
        self.plans = plans or {}

    def _x(self, sql, args=()):
        with self.s._lock:
            cur = self.db.execute(sql, args)
            self.db.commit()
            return cur

    def _q(self, sql, args=()):
        with self.s._lock:
            return self.db.execute(sql, args).fetchall()

    def audit(self, actor: str, action: str, target: str, detail: str = "", now: float | None = None):
        self._x("INSERT INTO audit VALUES (?,?,?,?,?)", (_iso(now), actor, action, target, detail[:500]))

    def link(self, discord_id: str, username: str, now: float | None = None):
        self._x("INSERT INTO members(discord_id, username, linked_at) VALUES (?,?,?) ON CONFLICT(discord_id) "
                "DO UPDATE SET username=excluded.username", (discord_id, username, _iso(now)))

    # --- eventos de Stripe
    def handle(self, ev: dict, now: float | None = None) -> str:
        """Procesa un evento ya verificado. Devuelve el resultado (también se guarda)."""
        if self._q("SELECT 1 FROM stripe_events WHERE id=?", (ev["id"],)):
            return "duplicado: ignorado"
        o, t, live = ev["data"]["object"], ev["type"], int(bool(ev.get("livemode")))
        res = "sin efecto"
        if t == "checkout.session.completed":
            did = o.get("client_reference_id") or (o.get("metadata") or {}).get("discord_id")
            if did:
                self._x("UPDATE members SET stripe_customer=? WHERE discord_id=?", (o.get("customer"), did))
                res = f"alta vinculada a {did}"
        elif t.startswith("customer.subscription."):
            did = (o.get("metadata") or {}).get("discord_id") or self._discord_for_customer(o.get("customer"))
            status = "canceled" if t.endswith(".deleted") else o["status"]
            self._x("INSERT INTO subscriptions VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET status=excluded.status, "
                    "current_period_end=excluded.current_period_end, cancel_at_period_end=excluded.cancel_at_period_end, "
                    "updated_at=excluded.updated_at", (o["id"], did, (o.get("metadata") or {}).get("plan", "mensual"), status,
                                                       o.get("current_period_end"), int(bool(o.get("cancel_at_period_end"))),
                                                       live, _iso(o.get("start_date") or now), _iso(now)))
            res = f"suscripción {o['id']} → {status}" + (" (cancela al vencer)" if o.get("cancel_at_period_end") else "")
        elif t in ("invoice.paid", "invoice.payment_failed"):
            did = self._discord_for_customer(o.get("customer"))
            kind = {"subscription_create": "alta", "subscription_cycle": "renovación"}.get(o.get("billing_reason"), "otro")
            st = "pagado" if t == "invoice.paid" else "fallido"
            self._x("INSERT OR REPLACE INTO payments VALUES (?,?,?,?,?,?,?,?)",
                    (o["id"] + ("" if st == "pagado" else f"#{ev['id']}"), did,
                     o.get("amount_paid") if st == "pagado" else o.get("amount_due"), o.get("currency", "eur"), st, kind, live, _iso(now)))
            res = f"cobro {st} ({kind})"
        self._x("INSERT INTO stripe_events VALUES (?,?,?,?,?)", (ev["id"], t, live, _iso(now), res))
        return res

    def _discord_for_customer(self, customer):
        r = self._q("SELECT discord_id FROM members WHERE stripe_customer=?", (customer,))
        return r[0][0] if r else None

    # --- derecho de acceso
    def entitled(self, discord_id: str, now: float | None = None) -> tuple[bool, str]:
        now = now or time.time()
        rows = self._q("SELECT status, current_period_end, cancel_at_period_end, plan FROM subscriptions WHERE discord_id=? "
                       "ORDER BY updated_at DESC", (discord_id,))
        if not rows:
            return False, "sin suscripción"
        for status, end, cancel_end, plan in rows:
            grace = (self.plans.get(plan).grace_days if plan in self.plans else 3) * 86400
            if status in ACTIVE and now < (end or 0):
                return True, "activa" + (" (cancelada: acceso hasta el fin del periodo)" if cancel_end else "")
            if status == "past_due" and now < (end or 0) + grace:
                return True, "pago pendiente: en periodo de gracia"
        st = rows[0][0]
        return False, {"canceled": "cancelada y vencida", "past_due": "impagada: gracia agotada",
                       "unpaid": "impagada"}.get(st, "vencida" if st in ACTIVE else st)

    # --- sincronización con Discord
    def reconcile(self, roles_api, now: float | None = None, only: str | None = None, actor: str = "sistema") -> list[dict]:
        """Lleva el rol de Discord al estado que corresponde. Nunca lanza: los fallos quedan «pendientes»."""
        ids = [only] if only else [r[0] for r in self._q("SELECT discord_id FROM members")]
        out = []
        for did in ids:
            want, why = self.entitled(did, now)
            row = self._q("SELECT actual, attempts, welcomed FROM role_sync WHERE discord_id=?", (did,))
            actual, attempts, welcomed = row[0] if row else (None, 0, 0)
            if actual is not None and bool(actual) == want and (row and self._q(
                    "SELECT status FROM role_sync WHERE discord_id=?", (did,))[0][0] == "ok"):
                out.append({"discord_id": did, "accion": "nada", "estado": "ok", "motivo": why})
                continue
            if actual is None and not want:          # visitante que nunca tuvo acceso: no hay nada que retirar
                self._x("INSERT OR REPLACE INTO role_sync VALUES (?,?,?,?,?,?,?,?)", (did, 0, 0, "ok", 0, None, _iso(now), 0))
                out.append({"discord_id": did, "accion": "nada", "estado": "ok", "motivo": why})
                continue
            try:
                if want:
                    roles_api.add_role(did)
                    if not welcomed:
                        roles_api.welcome(did)
                        welcomed = 1
                else:
                    roles_api.remove_role(did)
                self._x("INSERT OR REPLACE INTO role_sync VALUES (?,?,?,?,?,?,?,?)",
                        (did, int(want), int(want), "ok", attempts, None, _iso(now), welcomed))
                acc = "rol concedido" if want else "rol retirado"
                self.audit(actor, acc, did, why, now)
                out.append({"discord_id": did, "accion": acc, "estado": "ok", "motivo": why})
            except Exception as e:  # noqa: BLE001 — Discord caído, permisos…
                self._x("INSERT OR REPLACE INTO role_sync VALUES (?,?,?,?,?,?,?,?)",
                        (did, int(want), actual, "pendiente", attempts + 1, f"{type(e).__name__}: {e}"[:200], _iso(now), welcomed))
                self.audit(actor, "sincronización fallida", did, str(e), now)
                out.append({"discord_id": did, "accion": "pendiente", "estado": "pendiente", "motivo": str(e)})
        return out

    # --- cifras para el panel
    def summary(self, now: float | None = None, period_days: int = 30) -> dict:
        now = now or time.time()
        since = _iso(now - period_days * 86400)
        out = {}
        for live, label in ((1, "real"), (0, "prueba")):
            subs = self._q("SELECT discord_id, plan, status, current_period_end, cancel_at_period_end, started_at, updated_at "
                           "FROM subscriptions WHERE livemode=?", (live,))
            active = [s for s in subs if self.entitled(s[0], now)[0]]
            mrr = sum(self.plans[s[1]].price_cents if s[1] in self.plans else 0 for s in active if s[2] in ACTIVE and not s[4])
            pays = self._q("SELECT kind, status, amount_cents FROM payments WHERE livemode=? AND at>=?", (live, since))
            out[label] = {
                "miembros_de_pago": len(active),
                "altas": sum(1 for k, st, _ in pays if k == "alta" and st == "pagado"),
                "renovaciones": sum(1 for k, st, _ in pays if k == "renovación" and st == "pagado"),
                "bajas": sum(1 for s in subs if s[2] == "canceled" and (s[6] or "") >= since),
                "cancelaciones_programadas": sum(1 for s in active if s[4]),
                "cobrado_cents": sum(a or 0 for _, st, a in pays if st == "pagado"),
                "cobros_fallidos": sum(1 for _, st, _ in pays if st == "fallido"),
                "mrr_cents": mrr,
            }
        return out

    def anomalies(self, roles_api=None, now: float | None = None) -> dict:
        """Pagado sin acceso / acceso sin derecho. Con roles_api compara con Discord; si no, con el último estado conocido."""
        paid_no_access, access_no_right = [], []
        for (did,) in self._q("SELECT discord_id FROM members"):
            want, why = self.entitled(did, now)
            if roles_api is not None and hasattr(roles_api, "has_role"):
                try:
                    has = roles_api.has_role(did)
                except Exception:   # noqa: BLE001
                    has = None
            else:
                r = self._q("SELECT actual FROM role_sync WHERE discord_id=?", (did,))
                has = bool(r[0][0]) if r and r[0][0] is not None else False
            if want and has is False:
                paid_no_access.append((did, why))
            if has and not want:
                access_no_right.append((did, why))
        if roles_api is not None and hasattr(roles_api, "holders"):
            known = {r[0] for r in self._q("SELECT discord_id FROM members")}
            for did in roles_api.holders():
                if did not in known:
                    access_no_right.append((did, "tiene el rol sin ninguna suscripción registrada"))
        return {"pagado_sin_acceso": paid_no_access, "acceso_sin_derecho": access_no_right}

    def member_card(self, discord_id: str, now: float | None = None) -> dict:
        m = self._q("SELECT username, stripe_customer, linked_at FROM members WHERE discord_id=?", (discord_id,))
        s = self._q("SELECT plan, status, current_period_end, cancel_at_period_end, livemode FROM subscriptions WHERE discord_id=? "
                    "ORDER BY updated_at DESC LIMIT 1", (discord_id,))
        r = self._q("SELECT actual, status, attempts, last_error, last_sync_at FROM role_sync WHERE discord_id=?", (discord_id,))
        want, why = self.entitled(discord_id, now)
        return {"discord_id": discord_id, "usuario": m[0][0] if m else None, "plan": s[0][0] if s else None,
                "estado_suscripcion": s[0][1] if s else None,
                "vigente_hasta": _iso(s[0][2]) if s and s[0][2] else None, "cancela_al_vencer": bool(s and s[0][3]),
                "modo": ("real" if s and s[0][4] else "prueba") if s else None, "derecho": want, "motivo": why,
                "rol_en_discord": bool(r[0][0]) if r and r[0][0] is not None else None,
                "sincronizacion": r[0][1] if r else "nunca", "intentos": r[0][2] if r else 0,
                "ultimo_error": r[0][3] if r else None, "ultima_sincronizacion": r[0][4] if r else None,
                "historial": self._q("SELECT at, actor, action, detail FROM audit WHERE target=? ORDER BY at", (discord_id,))}


# ------------------------------------------------------------------ Discord (rol + bienvenida)
class DiscordRoles:
    """Concede/retira «Suscriptor activo» con el bot (DISCORD_BOT_TOKEN). Errores → excepción (la recoge reconcile)."""
    API = "https://discord.com/api/v10"

    def __init__(self, token: str, guild_id: str, role_id: str, http=None, welcome_text: str | None = None):
        import requests
        self.h = {"Authorization": f"Bot {token}"}
        self.g, self.r, self.http = guild_id, role_id, http or requests.Session()
        self.welcome_text = welcome_text or ("¡Bienvenido! Tu suscripción está activa. Empieza en #elige-tus-avisos para "
                                             "elegir tallas y marcas.")

    def _ok(self, r):
        if r.status_code >= 400:
            raise RuntimeError(f"Discord HTTP {r.status_code}")
        return r

    def add_role(self, uid):
        self._ok(self.http.put(f"{self.API}/guilds/{self.g}/members/{uid}/roles/{self.r}", headers=self.h))

    def remove_role(self, uid):
        r = self.http.delete(f"{self.API}/guilds/{self.g}/members/{uid}/roles/{self.r}", headers=self.h)
        if r.status_code not in (204, 404):     # 404: ya no está en el servidor → nada que retirar
            self._ok(r)

    def has_role(self, uid) -> bool | None:
        r = self.http.get(f"{self.API}/guilds/{self.g}/members/{uid}", headers=self.h)
        if r.status_code == 404:
            return False
        return self.r in self._ok(r).json().get("roles", [])

    def welcome(self, uid):
        ch = self._ok(self.http.post(f"{self.API}/users/@me/channels", headers=self.h, json={"recipient_id": uid})).json()
        self._ok(self.http.post(f"{self.API}/channels/{ch['id']}/messages", headers=self.h,
                                json={"content": self.welcome_text, "allowed_mentions": {"parse": []}}))


# ------------------------------------------------------------------ Stripe (modo prueba real, si hay claves)
class StripeAPI:
    API = "https://api.stripe.com/v1"

    def __init__(self, secret_key: str, http=None):
        import requests
        if not secret_key.startswith(("sk_test_", "rk_test_")) and not secret_key.startswith(("sk_live_", "rk_live_")):
            raise ValueError("clave de Stripe no reconocida")
        self.key, self.http = secret_key, http or requests.Session()
        self.live = "_live_" in secret_key

    def checkout(self, price_id: str, discord_id: str, success_url: str, cancel_url: str) -> str:
        r = self.http.post(f"{self.API}/checkout/sessions", auth=(self.key, ""), data={
            "mode": "subscription", "line_items[0][price]": price_id, "line_items[0][quantity]": 1,
            "client_reference_id": discord_id, "subscription_data[metadata][discord_id]": discord_id,
            "success_url": success_url, "cancel_url": cancel_url, "locale": "es"})
        r.raise_for_status()
        return r.json()["url"]

    def portal(self, customer: str, return_url: str) -> str:
        r = self.http.post(f"{self.API}/billing_portal/sessions", auth=(self.key, ""),
                           data={"customer": customer, "return_url": return_url})
        r.raise_for_status()
        return r.json()["url"]


# ------------------------------------------------------------------ simulador local de Stripe (PRUEBA LOCAL)
class StripeSimulator:
    """Genera eventos con el MISMO formato y firma que Stripe (livemode=false) para probar sin claves ni red."""
    def __init__(self, secret: str, price_cents: int):
        self.secret, self.price, self.n = secret, price_cents, 0

    def _id(self, p):
        self.n += 1
        return f"{p}_sim{self.n:05d}"

    def event(self, etype: str, obj: dict, now: float, eid: str | None = None) -> tuple[bytes, str]:
        ev = {"id": eid or self._id("evt"), "type": etype, "livemode": False, "created": int(now), "data": {"object": obj}}
        body = json.dumps(ev).encode()
        return body, sign(body, self.secret, int(now))

    def subscribe(self, discord_id: str, now: float, days: int = 30):
        cus, sub = self._id("cus"), self._id("sub")
        so = {"id": sub, "customer": cus, "status": "active", "current_period_end": int(now + days * 86400),
              "cancel_at_period_end": False, "start_date": int(now), "metadata": {"discord_id": discord_id, "plan": "mensual"}}
        return cus, sub, [
            self.event("checkout.session.completed", {"id": self._id("cs"), "customer": cus, "subscription": sub,
                                                      "client_reference_id": discord_id}, now),
            self.event("customer.subscription.created", so, now),
            self.event("invoice.paid", {"id": self._id("in"), "customer": cus, "subscription": sub, "amount_paid": self.price,
                                        "currency": "eur", "billing_reason": "subscription_create"}, now)]

    def sub_obj(self, sub, cus, discord_id, status, end, cancel=False, start=None):
        return {"id": sub, "customer": cus, "status": status, "current_period_end": int(end), "cancel_at_period_end": cancel,
                "start_date": int(start or end - 30 * 86400), "metadata": {"discord_id": discord_id, "plan": "mensual"}}
