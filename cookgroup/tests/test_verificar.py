"""v1.6 · lote 5: VERIFICAR.bat — cada comprobación dice OK o el PASO exacto que falla y cómo arreglarlo.
Simulación: tienda y Discord falsos (aquí no hay red hacia las tiendas ni token)."""
from types import SimpleNamespace as NS

import requests

from cookgroup.verificar import GUILD_ESPERADO, informe, paso_alerta, paso_discord, paso_tienda

TOKEN = "TOKEN-SECRETO-NO-DEBE-SALIR"


class R:
    def __init__(self, code, data=None):
        self.status_code, self._d = code, data

    def json(self):
        return self._d


class FakeDiscord:
    def __init__(self, token_ok=True, in_guild=True, canales=("general", "pruebas-bot")):
        self.token_ok, self.in_guild, self.canales = token_ok, in_guild, canales

    def get(self, url, headers=None, timeout=None):
        assert headers["Authorization"] == f"Bot {TOKEN}"
        if not self.token_ok:
            return R(401)
        if url.endswith("/users/@me"):
            return R(200, {"username": "cookbot", "id": "42"})
        if url.endswith(f"/guilds/{GUILD_ESPERADO}"):
            return R(200, {"name": "Mi servidor privado"}) if self.in_guild else R(403)
        if url.endswith("/channels"):
            return R(200, [{"id": str(100 + i), "name": n} for i, n in enumerate(self.canales)])
        raise AssertionError(url)


ENV = {"DISCORD_BOT_TOKEN": TOKEN, "DISCORD_GUILD_ID": GUILD_ESPERADO, "DISCORD_WEBHOOK_PRUEBAS": "https://x/y"}


def txt(pasos):
    t, code = informe(pasos)
    assert TOKEN not in t                                     # el token nunca aparece en la salida
    return t, code


def test_discord_ok():
    t, code = txt(paso_discord(ENV, FakeDiscord()))
    assert code == 0 and "cookbot" in t and "Mi servidor privado" in t and "todo correcto" in t


def test_discord_each_failure_names_the_exact_step():
    cases = [({**ENV, "DISCORD_BOT_TOKEN": ""}, FakeDiscord(), "2.1", "DISCORD_BOT_TOKEN"),
             (ENV, FakeDiscord(token_ok=False), "2.1", "Reset Token" if False else "vuelve a copiarlo"),
             ({**ENV, "DISCORD_GUILD_ID": "1"}, FakeDiscord(), "2.2", GUILD_ESPERADO),
             (ENV, FakeDiscord(in_guild=False), "2.2", "OAuth2"),
             (ENV, FakeDiscord(canales=("general",)), "2.3", "INSTALAR_SERVIDOR.bat"),
             ({**ENV, "DISCORD_WEBHOOK_PRUEBAS": ""}, FakeDiscord(), "2.3", "DISCORD_WEBHOOK_PRUEBAS")]
    for env, http, paso, pista in cases:
        t, code = txt(paso_discord(env, http))
        assert code == 1 and f"falla el PASO {paso}" in t and pista in t, (paso, t)


def test_tienda_ok_and_blocked():
    class Ok:
        def fetch(self):
            return [NS(title="Nike Dunk Low")]

    class Bloqueada:
        def fetch(self):
            r = requests.Response()
            r.status_code = 403
            raise requests.HTTPError(response=r)
    mons = [NS(name="bstn-eu", store="BSTN"), NS(name="footdistrict", store="FOOTDISTRICT")]
    t, code = txt(paso_tienda(mons, lambda m: Ok()))
    assert code == 0 and "Nike Dunk Low" in t
    t, code = txt(paso_tienda(mons, lambda m: Ok() if m.name == "bstn-eu" else Bloqueada()))
    assert code == 1 and "falla el PASO 1.2" in t and "HTTP 403" in t


def test_alerta_gives_mobile_link_or_refuses():
    from cookgroup.real_delivery import Refused
    ok = lambda store: {"estado": "entrega real confirmada", "guild_id": GUILD_ESPERADO, "channel_id": "101", "message_id": "999"}  # noqa: E731
    t, code = txt(paso_alerta(ok, None))
    assert code == 0 and f"https://discord.com/channels/{GUILD_ESPERADO}/101/999" in t

    def no(store):
        raise Refused("falta DISCORD_WEBHOOK_PRUEBAS en .env")
    t, code = txt(paso_alerta(no, None))
    assert code == 1 and "no se ha enviado nada" in t and "VERIFICAR.bat discord" in t
