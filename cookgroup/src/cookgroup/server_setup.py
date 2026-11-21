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
TYPES = {"texto": 0, "voz": 2, "categoria": 4, "anuncios": 5, "foro": 15}
VIEW, SEND, SEND_THREADS, CREATE_PUB_THREADS, ADD_REACTIONS = 1 << 10, 1 << 11, 1 << 38, 1 << 35, 1 << 6


def load_design(path: str | Path = "config/servidor.toml", dedicated: str | Path | None = "auto") -> dict:
    """Diseño base + canales dedicados generados (tiendas, regiones, temas, foros) si existen."""
    path = Path(path)
    d = tomllib.loads(path.read_text(encoding="utf-8"))
    extra = path.parent / "canales_dedicados.toml" if dedicated == "auto" else (Path(dedicated) if dedicated else None)
    if extra and extra.exists():
        d["categoria"] = d["categoria"] + tomllib.loads(extra.read_text(encoding="utf-8")).get("categoria", [])
    return d


def all_roles(design: dict) -> list[str]:
    r = design["roles"]
    out = list(dict.fromkeys(r.get("acceso", []) + r.get("staff", []))) + r.get("familias", []) + r.get("marcas", []) + r.get("regiones", [])
    out += [f"EU {t}" for t in r.get("tallas_eu", [])]
    return out


def webhook_key(fuente: str) -> str | None:
    return fuente.split(":", 1)[1] if fuente.startswith("bot:") else None


def _norm(n: str) -> str:
    return re.sub(r"[^\w-]", "", n.lower().replace(" ", "-"))


def overwrites(audiencia: str, acceso: str, guild_id: str, role_ids: dict[str, str]) -> list[dict]:
    """Sobrescrituras de Discord a partir de la matriz de access.py (misma fuente que las pruebas de permisos)."""
    from .access import EVERYONE, channel_overwrites
    out = []
    for role, (allow, deny) in channel_overwrites(audiencia, acceso).items():
        rid = guild_id if role == EVERYONE else role_ids.get(role)
        if rid:
            out.append({"id": rid, "type": 0, "allow": str(allow), "deny": str(deny)})
    return out


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
        if all(ch.get("instalar") is False for ch in cat["canal"]):
            continue                                      # categoría entera pendiente de tu decisión (MARKET)
        if _norm(cat["nombre"]) not in cats and cat["nombre"] not in plan.categories:
            plan.categories.append(cat["nombre"])
        for ch in cat["canal"]:
            if ch.get("instalar") is False:
                continue                                  # p. ej. MARKET: solo si el dueño lo aprueba
            if _norm(ch["nombre"]) not in by_name and all(_norm(ch["nombre"]) != _norm(n) for _, n, _ in plan.channels):
                plan.channels.append((cat["nombre"], ch["nombre"], ch["tipo"]))
            k = webhook_key(ch["fuente"])
            if k and f"DISCORD_WEBHOOK_{k.upper()}" not in env_keys and all(key != f"DISCORD_WEBHOOK_{k.upper()}" for _, key in plan.webhooks) \
                    and ch.get("estado") != "pendiente":
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
    def create_role(self, name, permissions: int = 0): return self._ok(self.http.post(
        f"{API}/guilds/{self.g}/roles", headers=self.h, json={"name": name, "mentionable": False, "permissions": str(permissions)}))
    def create_channel(self, body): return self._ok(self.http.post(f"{API}/guilds/{self.g}/channels", headers=self.h, json=body))
    def create_webhook(self, channel_id, name): return self._ok(self.http.post(f"{API}/channels/{channel_id}/webhooks",
                                                                             headers=self.h, json={"name": name}))
    def post_message(self, channel_id, body): return self._ok(self.http.post(f"{API}/channels/{channel_id}/messages",
                                                                             headers=self.h, json=body))
    def pin(self, channel_id, message_id): return self._ok(self.http.put(f"{API}/channels/{channel_id}/pins/{message_id}",
                                                                         headers=self.h))
    def put_onboarding(self, body): return self._ok(self.http.put(f"{API}/guilds/{self.g}/onboarding", headers=self.h, json=body))


def read_env_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {l.split("=", 1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines() if "=" in l and l.split("=", 1)[1].strip()}


def apply(design: dict, api: DiscordAPI, env_path: Path, log=print) -> dict:
    roles, chans = api.roles(), api.channels()
    plan = make_plan(design, roles, chans, read_env_keys(env_path))
    role_ids = {r["name"]: r["id"] for r in roles}
    from .access import GUILD_PERMS, OWNER
    for name in plan.roles:
        perms = 0 if name == OWNER else GUILD_PERMS.get(name, 0)   # Propietario: tu cuenta ya es dueña; el rol es visible, sin admin
        role_ids[name] = api.create_role(name, perms)["id"]
    cat_ids = {_norm(c["name"]): c["id"] for c in chans if c["type"] == 4}
    ch_ids = {_norm(c["name"]): c["id"] for c in chans if c["type"] != 4}
    notes = []
    for cat in design["categoria"]:
        if all(ch.get("instalar") is False for ch in cat["canal"]):
            continue
        if _norm(cat["nombre"]) not in cat_ids:
            body = {"name": cat["nombre"], "type": 4,
                    "permission_overwrites": overwrites(cat.get("audiencia", "suscriptores"), "lectura", api.g, role_ids)}
            cat_ids[_norm(cat["nombre"])] = api.create_channel(body)["id"]
        for ch in cat["canal"]:
            if _norm(ch["nombre"]) in ch_ids or ch.get("instalar") is False:
                continue
            body = {"name": ch["nombre"], "type": TYPES[ch["tipo"]], "parent_id": cat_ids[_norm(cat["nombre"])],
                    "topic": ch.get("finalidad", "")[:1024],
                    "permission_overwrites": overwrites(cat.get("audiencia", "suscriptores"), ch["acceso"], api.g, role_ids)}
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
    # v1.1: mapa nombre → id de canal (no es secreto) para que el panel y el directorio abran cada canal en Discord
    import json as _json
    ids_path = env_path.parent / "data" / "canales_ids.json"
    ids_path.parent.mkdir(parents=True, exist_ok=True)
    ids_path.write_text(_json.dumps({"guild_id": api.g, "canales": {k: v for k, v in ch_ids.items()}}, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    pinned = pin_store_cards(api, ch_ids, env_path.parent / "data" / "tarjetas_fijadas.json", notes)
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
    return {"plan": plan, "notes": notes, "webhooks_added": len(new_env), "cards_pinned": pinned}


def pin_store_cards(api, ch_ids: dict, done_path: Path, notes: list, lote_path: Path = Path("config/lote_tiendas.toml")) -> int:
    """Publica y fija UNA vez la tarjeta de cada tienda del lote en su canal (país, web, envío a España, señales)."""
    import json as _json
    from .store_directory import load_lote, store_card
    done = _json.loads(done_path.read_text(encoding="utf-8")) if done_path.exists() else {}
    n = 0
    for t in load_lote(lote_path):
        cid = ch_ids.get(_norm(t["canal"]))
        if not cid or t["canal"] in done:
            continue
        try:
            m = api.post_message(cid, store_card(t))
            api.pin(cid, m["id"])
            done[t["canal"]] = m["id"]
            n += 1
        except (RuntimeError, KeyError) as e:
            notes.append(f"Tarjeta de #{t['canal']} no fijada ({e})")
    done_path.parent.mkdir(parents=True, exist_ok=True)
    done_path.write_text(_json.dumps(done, indent=1), encoding="utf-8")
    return n
