"""v1.6 · contador público de miembros (equivalente a «The Zesty Chefs: 490» de la referencia): el bot renombra el
canal de voz «Miembros» a «Miembros: N» con los miembros de PAGO, como mucho una vez por hora (Discord limita renombres)."""
from types import SimpleNamespace as NS

from cookgroup.billing import DiscordRoles
from cookgroup.web import update_counter


class Http:
    def __init__(self):
        self.calls = []

    def patch(self, url, headers=None, json=None, timeout=None):
        self.calls.append((url, json))
        return NS(status_code=200, json=lambda: {}, text="")


def test_counter_renames_once_per_hour_with_paying_members(monkeypatch):
    http = Http()
    roles = DiscordRoles.__new__(DiscordRoles)
    roles.http, roles.h, roles.API = http, {"Authorization": "Bot x"}, "https://discord.com/api/v10"
    roles._ok = lambda r: r
    app = NS(env={"DISCORD_CONTADOR_CHANNEL_ID": "555"}, roles=roles, b=NS(paying_members=lambda now: 37), now=lambda: 0)
    t = [10_000.0]
    monkeypatch.setattr("cookgroup.web.time.time", lambda: t[0])
    assert update_counter(app) == 37
    assert http.calls == [("https://discord.com/api/v10/channels/555", {"name": "Miembros: 37"})]
    t[0] += 1800
    assert update_counter(app) is None and len(http.calls) == 1        # antes de una hora: no renombra
    t[0] += 1801
    assert update_counter(app) == 37 and len(http.calls) == 2


def test_counter_off_without_channel_id():
    assert update_counter(NS(env={}, roles=None)) is None
