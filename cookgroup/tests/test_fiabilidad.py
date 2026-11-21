"""v1.6 · lote 4: fiabilidad de los avisos (SIMULACIONES identificadas sobre el lector de producción y la bandeja real)."""
import json

import requests

from cookgroup.config import MonitorConfig
from cookgroup.discord import UncertainDelivery, WebhookSender
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import deliver_outbox, run_cycle
from cookgroup.sources.jsonld import JsonLdSource
from cookgroup.store import Store

BASE = "https://tienda.example"


def ld(name, variants):
    return {"@type": "ProductGroup", "name": name, "productGroupID": name,
            "hasVariant": [{"@type": "Product", "sku": f"{name}-{c}-{s}", "size": s, "color": c,
                            "offers": {"@type": "Offer", "price": p, "priceCurrency": "EUR",
                                       "availability": "https://schema.org/" + ("InStock" if ok else "OutOfStock")}}
                           for c, s, p, ok in variants]}


class Shop:
    def __init__(self, n=10):
        self.pages = {f"/p/{i}": ld(f"P{i}", [("negro", "42", 100, True), ("negro", "43", 100, False)]) for i in range(n)}
        self.order, self.fail, self.truncated = list(self.pages), set(), set()

    def get(self, url, **kw):
        path = url.replace(BASE, "").split("?")[0]
        if path in self.fail:
            raise requests.ConnectionError("caída simulada")
        if path in self.pages:
            body = f'<script type="application/ld+json">{json.dumps(self.pages[path])}</script>'
            if path in self.truncated:
                body = body[: len(body) // 2]                     # página incompleta (cortada a mitad)
        else:
            body = "".join(f'<a href="{p}">x</a>' for p in self.order)

        class R:
            status_code, headers, text, content = 200, {}, body, body.encode()
        return R()


def setup(tmp_path, shop, country="ES", name="t"):
    cfg = MonitorConfig(name, "jsonld", "Tienda", BASE, channel="sneakers", country=country)
    src = JsonLdSource("Tienda", BASE, listing_urls=[BASE + "/lista"], product_link_pattern="/p/", session=shop,
                       products_per_cycle=20, market=country)
    st, mk, got = Store(tmp_path / "s.db"), FileMarketProvider(tmp_path / "m.json"), []
    return (lambda: run_cycle(cfg, {"min_drop_pct": 5}, src, st, mk, lambda p: got.append(p) or "1")), got, st


def test_one_page_of_ten_fails_then_recovers_without_false_alerts(tmp_path):
    shop = Shop()
    cycle, got, st = setup(tmp_path, shop)
    cycle()
    shop.fail = {"/p/3"}
    r = cycle()
    assert r["ok"] and got == []                                 # las otras 9 se leen; la 3 conserva su último estado
    shop.fail = set()
    cycle()
    assert got == [], "al volver la ficha no debe haber falsa reposición ni agotado"
    snap = st.load_snapshot("t")
    assert any(k.endswith("P3") for k in snap)


def test_incomplete_page_keeps_last_valid_state(tmp_path):
    shop = Shop()
    cycle, got, _ = setup(tmp_path, shop)
    cycle()
    shop.truncated = {"/p/5"}
    cycle()
    shop.truncated = set()
    cycle()
    assert got == []


def test_listing_order_change_is_not_news(tmp_path):
    shop = Shop()
    cycle, got, _ = setup(tmp_path, shop)
    cycle()
    shop.order.reverse()
    cycle()
    assert got == []


def test_two_colors_different_prices_no_false_drop(tmp_path):
    shop = Shop(1)
    shop.pages["/p/0"] = ld("P0", [("negro", "42", 120, True), ("blanco", "42", 90, True)])
    cycle, got, _ = setup(tmp_path, shop)
    cycle()
    shop.pages["/p/0"] = ld("P0", [("negro", "42", 120, True), ("blanco", "42", 90, False)])   # blanco se agota
    cycle()
    shop.pages["/p/0"] = ld("P0", [("negro", "42", 120, True), ("blanco", "42", 90, True)])    # blanco vuelve: 90 € como antes
    cycle()
    titles = [g["embeds"][0]["title"] for g in got]
    assert len(got) == 1 and "REBAJA" not in titles[0].upper() and "BAJADA" not in titles[0].upper(), titles
    shop.pages["/p/0"] = ld("P0", [("negro", "42", 99, True), ("blanco", "42", 90, True)])     # el negro SÍ baja
    cycle()
    drop = got[-1]["embeds"][0]
    blob = json.dumps(drop, ensure_ascii=False)
    assert len(got) == 2 and "negro" in blob and "120,00" in blob and "99,00" in blob


def test_same_code_in_two_markets_does_not_collide(tmp_path):
    es, fr = Shop(1), Shop(1)
    c_es, got_es, _ = setup(tmp_path, es, "ES", "tienda-es")
    c_fr, got_fr, _ = setup(tmp_path, fr, "FR", "tienda-fr")          # misma base de datos, mismo nombre de tienda
    c_es(); c_fr()
    fr.pages["/p/0"] = ld("P0", [("negro", "42", 100, True), ("negro", "43", 100, True)])       # vuelve la 43 SOLO en FR
    c_es(); c_fr()
    assert got_es == [] and len(got_fr) == 1


class Chan:
    def __init__(self, fail=False):
        self.fail, self.sent = fail, []

    def __call__(self, p):
        if self.fail:
            raise RuntimeError("Discord 503 (simulado)")
        self.sent.append(p)
        return str(len(self.sent))


def test_two_channels_ok_third_fails_restart_retries_only_pending(tmp_path):
    db = tmp_path / "bot.db"
    st = Store(db)
    for ch in ("a", "b", "c"):
        st.outbox_add(f"k|{ch}", "restock", "Tienda", "Tienda:1", ch, {"content": f"aviso {ch}"})
    a, b, c = Chan(), Chan(), Chan(fail=True)
    r = deliver_outbox(st, {"a": a, "b": b, "c": c})
    assert len(a.sent) == 1 and len(b.sent) == 1 and r["pending"] == 1
    pend = st.outbox_pending()
    assert [p[4] for p in pend] == ["c"]
    del st                                                             # REINICIO del proceso
    st2 = Store(db)
    a2, b2, c2 = Chan(), Chan(), Chan()
    r2 = deliver_outbox(st2, {"a": a2, "b": b2, "c": c2})
    assert (len(a2.sent), len(b2.sent), len(c2.sent)) == (0, 0, 1) and r2["pending"] == 0


def test_uncertain_send_is_marked_and_resent_once(tmp_path):
    class Sess:
        calls = 0

        def post(self, *a, **k):
            Sess.calls += 1
            if Sess.calls == 1:
                raise requests.ReadTimeout("se cortó tras enviar")        # SIMULACIÓN: ¿llegó o no?

            class R:
                status_code, content = 200, b"{}"

                def json(self):
                    return {"id": "999", "channel_id": "1"}
            return R()
    w = WebhookSender("https://example.invalid/hook", session=Sess())
    try:
        w.send({"content": "x"})
        raise AssertionError("debía marcarse como incierto")
    except UncertainDelivery:
        pass
    assert Sess.calls == 1, "no se reintenta en ráfaga"
    st = Store(tmp_path / "s.db")
    st.outbox_add("k", "restock", "T", "T:1", "a", {"content": "x"})
    deliver_outbox(st, {"a": WebhookSender("https://example.invalid/hook", session=type("S", (), {"post": lambda *a, **k: (_ for _ in ()).throw(requests.ReadTimeout("x"))})()).send})
    row = st.db.execute("SELECT last_error FROM outbox WHERE dedupe_key='k'").fetchone()
    assert row and row[0].startswith("incierto")
    deliver_outbox(st, {"a": w.send})                                  # siguiente ciclo: se reenvía una vez
    assert st.outbox_pending() == []
