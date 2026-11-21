"""v1.0: el panel responde de un vistazo: quién pagó y sigue fuera, qué canal no recibe datos, último aviso, tickets."""
from cookgroup.billing import Billing, DiscordRoles, load_plans
from cookgroup.owner_panel import render_owner
from cookgroup.store import Store


class R:
    def __init__(self, code, d):
        self.status_code, self._d = code, d

    def json(self):
        return self._d


class Http:
    def get(self, url, headers=None, params=None):
        if url.endswith("/threads/active"):
            return R(200, {"threads": [{"id": "t1", "parent_id": "SOP", "owner_id": "c1", "name": "No puedo entrar"},
                                       {"id": "t2", "parent_id": "SOP", "owner_id": "c2", "name": "Duda talla"},
                                       {"id": "t3", "parent_id": "OTRO", "owner_id": "c3", "name": "x"}]})
        if "/channels/t1/" in url:
            return R(200, [{"author": {"id": "c1"}, "timestamp": "2026-11-20T10:00:00+00:00"}])     # habló el cliente
        return R(200, [{"author": {"id": "staff1"}, "timestamp": "2026-11-20T11:00:00+00:00"}])     # respondió el equipo


def test_support_threads_need_reply():
    d = DiscordRoles("t", "g", "r", http=Http())
    t = d.support_threads("SOP", {"staff1"})
    assert [x["id"] for x in t if x["needs_reply"]] == ["t1"] and len(t) == 2      # solo #soporte; t2 ya respondido


def test_panel_channels_without_data_and_last_alert(tmp_path):
    st = Store(str(tmp_path / "s.db"))
    st.outbox_add("k1", "restock", "FOOTDISTRICT", "p", "sneakers", {"content": "x"})
    st.outbox_done("k1", "m1")
    b = Billing(st, load_plans())
    html = render_owner(b, channels_expected=["sneakers", "raffles"],
                        support=lambda: DiscordRoles("t", "g", "r", http=Http()).support_threads("SOP", {"staff1"}))
    assert "#sneakers" in html and "NUNCA HA RECIBIDO" in html and "#raffles" in html
    assert "No puedo entrar" in html and "Tickets que necesitan respuesta: <b>1</b>" in html
