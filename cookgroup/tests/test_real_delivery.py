"""v0.9: la primera prueba real solo puede ir a #pruebas-bot y se confirma releyendo el mensaje."""
import pytest

from cookgroup.real_delivery import Refused, send_first_real

URL = "https://discord.invalid/api/webhooks/77/TOKEN"


class R:
    def __init__(self, code, d):
        self.status_code, self._d = code, d

    def json(self):
        return self._d


class Http:
    def __init__(self, guild="G1", channel="C9", name="pruebas-bot", wh_name="cookgroup · pruebas-bot"):
        self.guild, self.channel, self.name, self.wh_name = guild, channel, name, wh_name

    def get(self, url, headers=None, timeout=None):
        if url == URL:
            return R(200, {"guild_id": self.guild, "channel_id": self.channel, "name": self.wh_name})
        if "/channels/" in url:
            return R(200, {"name": self.name})
        if "/messages/" in url:
            return R(200, {"channel_id": self.channel})
        return R(404, {})


def test_never_falls_back_to_default(tmp_path):
    with pytest.raises(Refused, match="DISCORD_WEBHOOK_PRUEBAS"):
        send_first_real({"DISCORD_WEBHOOK_DEFAULT": URL}, http=Http(), sender=lambda p: "1", log_path=tmp_path / "x.csv")


def test_refuses_other_guild_or_channel(tmp_path):
    env = {"DISCORD_WEBHOOK_PRUEBAS": URL, "DISCORD_GUILD_ID": "G1", "DISCORD_BOT_TOKEN": "t"}
    with pytest.raises(Refused, match="OTRO servidor"):
        send_first_real(env, http=Http(guild="G2"), sender=lambda p: "1", log_path=tmp_path / "x.csv")
    with pytest.raises(Refused, match="#general"):
        send_first_real(env, http=Http(name="general"), sender=lambda p: "1", log_path=tmp_path / "x.csv")
    with pytest.raises(Refused, match="no se puede confirmar"):
        send_first_real({"DISCORD_WEBHOOK_PRUEBAS": URL}, http=Http(wh_name="Captain Hook"), sender=lambda p: "1",
                        log_path=tmp_path / "x.csv")


def test_confirmed_delivery_is_logged(tmp_path):
    sent = []
    env = {"DISCORD_WEBHOOK_PRUEBAS": URL, "DISCORD_GUILD_ID": "G1", "DISCORD_BOT_TOKEN": "t"}
    row = send_first_real(env, http=Http(), sender=lambda p: sent.append(p) or "999", log_path=tmp_path / "e.csv")
    assert row["estado"] == "entrega real confirmada" and row["message_id"] == "999" and row["canal"] == "pruebas-bot"
    assert sent[0]["allowed_mentions"] == {"parse": []} and "999" in (tmp_path / "e.csv").read_text()
