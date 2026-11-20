"""Acceso de pago (v0.9): roles de acceso, sobrescrituras de permisos y cálculo de permisos efectivos.

El cálculo reproduce el algoritmo de Discord (permisos de servidor por roles → sobrescritura @everyone → roles →
miembro) para poder PROBAR la matriz sin tocar Discord: visitante, suscriptor, antiguo suscriptor, moderador, staff y
propietario. Los roles de preferencia (marcas, tallas, región, familias) no tienen ningún permiso.
"""
from __future__ import annotations

from dataclasses import dataclass, field

VIEW, SEND, MANAGE_MESSAGES, MANAGE_THREADS = 1 << 10, 1 << 11, 1 << 13, 1 << 34
CREATE_PUBLIC_THREADS, CREATE_PRIVATE_THREADS, SEND_IN_THREADS = 1 << 35, 1 << 36, 1 << 38
READ_HISTORY, ADD_REACTIONS, MODERATE_MEMBERS, ADMIN, MANAGE_ROLES = 1 << 16, 1 << 6, 1 << 40, 1 << 3, 1 << 28
EVERYONE = "@everyone"
SUB, MOD, STAFF, OWNER = "Suscriptor activo", "Moderador", "Staff", "Propietario"

# Permisos de servidor por rol (lo que el instalador pone en cada rol)
GUILD_PERMS = {
    EVERYONE: VIEW | READ_HISTORY | ADD_REACTIONS,    # el visitante ve lo público; los canales de pago lo deniegan
    SUB: 0,                                           # el acceso lo dan las sobrescrituras de cada canal
    MOD: MANAGE_MESSAGES | MANAGE_THREADS | MODERATE_MEMBERS,
    STAFF: MANAGE_MESSAGES | MANAGE_THREADS | MODERATE_MEMBERS,
    OWNER: ADMIN,                                     # además, tu cuenta es la dueña del servidor
}
TEAM = (OWNER, STAFF, MOD)


def channel_overwrites(audiencia: str, acceso: str) -> dict[str, tuple[int, int]]:
    """{rol: (allow, deny)} para un canal según quién lo ve (audiencia) y quién escribe (acceso)."""
    ow: dict[str, tuple[int, int]] = {}
    no_write = SEND | SEND_IN_THREADS | CREATE_PUBLIC_THREADS | CREATE_PRIVATE_THREADS
    team = (VIEW | SEND | SEND_IN_THREADS, 0)
    if acceso == "tickets":            # todos ven el canal y solo pueden abrir hilos PRIVADOS
        ow[EVERYONE] = (VIEW | CREATE_PRIVATE_THREADS | SEND_IN_THREADS, SEND | CREATE_PUBLIC_THREADS)
    elif audiencia == "todos":
        ow[EVERYONE] = (VIEW, no_write) if acceso == "lectura" else (VIEW, 0)
    elif audiencia == "suscriptores":
        ow[EVERYONE] = (0, VIEW | no_write)
        ow[SUB] = (VIEW, 0) if acceso == "lectura" else (VIEW | SEND | SEND_IN_THREADS | CREATE_PUBLIC_THREADS, 0)
    else:                              # equipo
        ow[EVERYONE] = (0, VIEW)
    for r in TEAM:
        ow[r] = team
    return ow


def effective(roles: set[str], overwrites: dict[str, tuple[int, int]]) -> int:
    perms = GUILD_PERMS[EVERYONE]
    for r in roles:
        perms |= GUILD_PERMS.get(r, 0)                # roles de preferencia → 0
    if perms & ADMIN:
        return -1                                     # todo
    a, d = overwrites.get(EVERYONE, (0, 0))
    perms = (perms & ~d) | a
    allow = deny = 0
    for r in roles:
        if r in overwrites:
            allow |= overwrites[r][0]
            deny |= overwrites[r][1]
    perms = (perms & ~deny) | allow
    if not perms & VIEW:
        return 0                                      # sin ver el canal no hay nada más
    return perms


def can(perms: int, bit: int) -> bool:
    return perms == -1 or bool(perms & bit)


@dataclass
class Identity:
    name: str
    roles: set[str] = field(default_factory=set)
    note: str = ""


TEST_IDENTITIES = [
    Identity("visitante", set(), "acaba de entrar, sin pagar"),
    Identity("suscriptor", {SUB, "Sneakers", "Nike", "EU 44,5", "Envío a España"}, "pago al día"),
    Identity("ex-suscriptor", {"Sneakers", "Nike", "EU 44,5", "Envío a España"},
             "venció su periodo: conserva sus preferencias y un enlace antiguo a #sneakers-eu"),
    Identity("moderador", {MOD}, "equipo"),
    Identity("staff", {STAFF}, "equipo"),
    Identity("propietario", {OWNER}, "tu cuenta (además es la dueña del servidor)"),
]


def matrix(design: dict) -> list[dict]:
    """Una fila por canal: qué puede hacer cada identidad (ver / escribir / abrir ticket privado)."""
    rows = []
    for cat in design["categoria"]:
        aud = cat.get("audiencia", "suscriptores")
        for ch in cat["canal"]:
            ow = channel_overwrites(aud, ch["acceso"])
            row = {"categoria": cat["nombre"], "canal": ch["nombre"], "audiencia": aud, "acceso": ch["acceso"]}
            for idn in TEST_IDENTITIES:
                p = effective(idn.roles, ow)
                if not can(p, VIEW):
                    row[idn.name] = "—"
                elif can(p, SEND):
                    row[idn.name] = "ve y escribe"
                elif can(p, CREATE_PRIVATE_THREADS):
                    row[idn.name] = "ve y abre ticket privado"
                else:
                    row[idn.name] = "ve"
            rows.append(row)
    return rows


def private_thread_visible(viewer_roles: set[str], is_participant: bool, parent_ow: dict) -> bool:
    """Un hilo privado (ticket) lo ve quien participa o quien puede gestionar hilos en el canal (equipo)."""
    p = effective(viewer_roles, parent_ow)
    return can(p, VIEW) and (is_participant or can(p, MANAGE_THREADS))


def is_entitled(roles: set[str]) -> bool:
    return bool(roles & {SUB, *TEAM})
