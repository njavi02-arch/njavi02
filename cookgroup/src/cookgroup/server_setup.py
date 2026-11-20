"""Instalador repetible de la estructura de MI servidor (config/servidor.toml) mediante la API de Discord.

Necesita, SOLO en el .env de tu PC:
  DISCORD_BOT_TOKEN=…      token de un bot tuyo invitado al servidor con «Gestionar canales», «Gestionar roles» y
                           «Gestionar webhooks»
  DISCORD_GUILD_ID=…       id de tu servidor (Mi servidor privado)
Reglas:
  · Idempotente: busca por nombre; lo que existe no se duplica ni se modifica. Nunca borra nada.
  · Los canales y conversaciones que ya tienes (general, juegos, música…) se quedan como están.
  · Crea un webhook por canal que alimenta el bot y lo escribe en tu .env (DISCORD_WEBHOOK_<CANAL>) sin mostrarlo.
"""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

API = "https://discord.com/api/v10"
TYPES = {"texto": 0, "categoria": 4, "anuncios": 5, "foro": 15}
VIEW, SEND, SEND_THREADS, CREATE_PUB_THREADS, ADD_REACTIONS = 1 << 10, 1 << 11, 1 << 38, 1 << 35, 1 << 6


def load_design(path: str | Path = "config/servidor.toml") -> dict:
    return tomllib.loads(Path(path).read_text(encoding="utf-8"))


def all_roles(design: dict) -> list[str]:
    r = design["roles"]
    out = list(r.get("staff", [])) + r.get("familias", []) + r.get("marcas", []) + r.get("regiones", [])
    out += [f"EU {t}" for t in r.get("tallas_eu", [])]
    return out


def webhook_key(fuente: str) -> str | None:
    return fuente.split(":", 1)[1] if fuente.startswith("bot:") else None


def _norm(n: str) -> str:
    return re.sub(r"[^\w-]", "", n.lower().replace(" ", "-"))


def overwrites(acceso: str, guild_id: str, staff_role_id: str | None) -> list[dict]:
    if acceso == "lectura":
        return [{"id": guild_id, "type": 0, "allow": str(VIEW), "deny": str(SEND | SEND_THREADS | CREATE_PUB_THREADS)}]
    if acceso == "privado":
        ow = [{"id": guild_id, "type": 0, "allow": "0", "deny": str(VIEW)}]
        if staff_role_id:
            ow.append({"id": staff_role_id, "type": 0, "allow": str(VIEW | SEND), "deny": "0"})
        return ow
    return []


@dataclass
class Plan:
    roles: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    channels: list[tuple[str, str, str]] = field(default_factory=list)   # (categoría, canal, tipo)
    kept: list[str] = field(default_factory=list)                        # ya existían: no se tocan
    webhooks: list[tuple[str, str]] = field(default_factory=list)        # (canal, clave .env)

    @property
    def empty(self) -> bool:
        return not (self.roles or self.categories or self.channels or self.webhooks)


def make_plan(design: dict, existing_roles: list[dict], existing_channels: list[dict], env_keys: set[str]) -> Plan:
    plan = Plan()
    have_roles = {r["name"] for r in existing_roles}
    plan.roles = [r for r in all_roles(design) if r not in have_roles]
    cats = {_norm(c["name"]): c for c in existing_channels if c["type"] == 4}
    chans = {(_norm(c["name"]), c.get("parent_id")): c for c in existing_channels if c["type"] != 4}
    by_name = {_norm(c["name"]) for c in existing_channels if c["type"] != 4}
    for c in existing_channels:
        if c["type"] != 4:
            plan.kept.append(c["name"])
    for cat in design["categoria"]:
        if _norm(cat["nombre"]) not in cats:
            plan.categories.append(cat["nombre"])
        for ch in cat["canal"]:
            if _norm(ch["nombre"]) not in by_name:
                plan.channels.append((cat["nombre"], ch["nombre"], ch["tipo"]))
            k = webhook_key(ch["fuente"])
            if k and f"DISCORD_WEBHOOK_{k.upper()}" not in env_keys:
                plan.webhooks.append((ch["nombre"], f"DISCORD_WEBHOOK_{k.upper()}"))
    return plan


def render_plan(plan: Plan) -> str:
    L = [f"Roles a crear ({len(plan.roles)}): " + (", ".join(plan.roles) or "ninguno"),
         f"Categorías a crear ({len(plan.categories)}): " + (", ".join(plan.categories) or "ninguna"),
         f"Canales a crear ({len(plan.channels)}):"]
    L += [f"  · {c} → #{n} ({t})" for c, n, t in plan.channels] or ["  ninguno"]
    L += [f"Webhooks a crear y guardar en .env ({len(plan.webhooks)}): " + (", ".join(f"#{c}" for c, _ in plan.webhooks) or "ninguno"),
          f"Canales que ya tienes y NO se tocan: " + (", ".join(plan.kept) or "ninguno")]
    return "\n".join(L)


class DiscordAPI:
    """Cliente mínimo. `http` es una requests.Session (en pruebas, un objeto falso con get/post/put)."""
    def __init__(self, token: str, guild_id: str, http=None):
        import requests
        self.g, self.http = guild_id, http or requests.Session()
        self.h = {"Authorization": f"Bot {token}", "User-Agent": "cookgroup-instalador (v0.8)"}

    def _ok(self, r):
        if r.status_code >= 400:
            raise RuntimeError(f"Discord HTTP {r.status_code}: {r.text[:200]}")
        return r.json() if r.content else {}

    def roles(self): return self._ok(self.http.get(f"{API}/guilds/{self.g}/roles", headers=self.h))
    def channels(self): return self._ok(self.http.get(f"{API}/guilds/{self.g}/channels", headers=self.h))
    def create_role(self, name): return self._ok(self.http.post(f"{API}/guilds/{self.g}/roles", headers=self.h,
                                                                json={"name": name, "mentionable": False}))
    def create_channel(self, body): return self._ok(self.http.post(f"{API}/guilds/{self.g}/channels", headers=self.h, json=body))
    def create_webhook(self, channel_id, name): return self._ok(self.http.post(f"{API}/channels/{channel_id}/webhooks",
                                                                             headers=self.h, json={"name": name}))
    def put_onboarding(self, body): return self._ok(self.http.put(f"{API}/guilds/{self.g}/onboarding", headers=self.h, json=body))


def read_env_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {l.split("=", 1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines() if "=" in l and l.split("=", 1)[1].strip()}


def apply(design: dict, api: DiscordAPI, env_path: Path, log=print) -> dict:
    roles, chans = api.roles(), api.channels()
    plan = make_plan(design, roles, chans, read_env_keys(env_path))
    role_ids = {r["name"]: r["id"] for r in roles}
    for name in plan.roles:
        role_ids[name] = api.create_role(name)["id"]
    staff = next((role_ids.get(n) for n in design["roles"].get("staff", [])), None)
    cat_ids = {_norm(c["name"]): c["id"] for c in chans if c["type"] == 4}
    ch_ids = {_norm(c["name"]): c["id"] for c in chans if c["type"] != 4}
    notes = []
    for cat in design["categoria"]:
        if _norm(cat["nombre"]) not in cat_ids:
            body = {"name": cat["nombre"], "type": 4}
            if cat.get("privada"):
                body["permission_overwrites"] = overwrites("privado", api.g, staff)
            cat_ids[_norm(cat["nombre"])] = api.create_channel(body)["id"]
        for ch in cat["canal"]:
            if _norm(ch["nombre"]) in ch_ids:
                continue
            body = {"name": ch["nombre"], "type": TYPES[ch["tipo"]], "parent_id": cat_ids[_norm(cat["nombre"])],
                    "topic": ch.get("finalidad", "")[:1024],
                    "permission_overwrites": overwrites(ch["acceso"], api.g, staff)}
            try:
                ch_ids[_norm(ch["nombre"])] = api.create_channel(body)["id"]
            except RuntimeError as e:   # foros/anuncios exigen «Comunidad»: se crea como texto y se anota
                if body["type"] in (5, 15):
                    body["type"] = 0
                    ch_ids[_norm(ch["nombre"])] = api.create_channel(body)["id"]
                    notes.append(f"#{ch['nombre']} creado como texto ({e}); activa «Comunidad» para foros/anuncios")
                else:
                    raise
    new_env = []
    for chname, key in plan.webhooks:
        wh = api.create_webhook(ch_ids[_norm(chname)], f"cookgroup · {chname}")
        new_env.append(f"{key}=" + "https://discord.com/api/" + f"webhooks/{wh['id']}/{wh['token']}")
    if new_env:
        with open(env_path, "a", encoding="utf-8") as f:
            f.write("\n# Añadido por INSTALAR_SERVIDOR (no compartir)\n" + "\n".join(new_env) + "\n")
    prompts = []
    for i, q in enumerate(design.get("pregunta", [])):
        names = design["roles"][q["roles"]] if q["roles"] != "tallas_eu" else [f"EU {t}" for t in design["roles"]["tallas_eu"]]
        prompts.append({"id": str(i), "type": 0, "title": q["titulo"], "single_select": not q.get("multiple", True),
                        "required": False, "in_onboarding": True,
                        "options": [{"title": n, "role_ids": [role_ids[n]], "channel_ids": []} for n in names[:50] if n in role_ids]})
    try:
        api.put_onboarding({"prompts": prompts, "enabled": True, "mode": 0,
                            "default_channel_ids": [ch_ids[k] for k in (_norm("bienvenida"), _norm("normas")) if k in ch_ids]})
    except RuntimeError as e:
        notes.append(f"Preguntas de bienvenida no aplicadas ({e}). Activa «Comunidad» en Ajustes del servidor y repite.")
    log(render_plan(plan))
    for n in notes:
        log("NOTA: " + n)
    return {"plan": plan, "notes": notes, "webhooks_added": len(new_env)}
