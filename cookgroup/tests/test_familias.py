"""v1.0: prueba PROPIA de cada familia que antes solo «compartía motor»: sneakers-mundo, baloncesto, skate, outlet,
streetwear y pokémon-tcg. CAPTURA REAL de una tienda de cada familia (20-nov-2026, tests/fixtures/familias_REAL_*.json)
+ CAMBIO SIMULADO. Cada una: un aviso que debe salir (con la mención correcta) y al menos un caso que debe callar.
"""
import copy
import json
from pathlib import Path

import pytest

from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.members import Profile
from cookgroup.pipeline import run_cycle
from cookgroup.sources.shopify import parse_products
from cookgroup.store import Store

FIX = json.loads((Path(__file__).parent / "fixtures/familias_REAL_2026-11-20.json").read_text())


class Src:
    def __init__(self, key, base):
        self.cat, self.base, self.cur = copy.deepcopy(FIX[key]), base, FIX[key]["currency"]

    def fetch(self):
        return parse_products(self.cat, store=self.base.upper(), base_url=f"https://{self.base}", currency=self.cur)

    def set(self, title_part, size, avail):
        for p in self.cat["products"]:
            if title_part in p["title"]:
                for v in p["variants"]:
                    if v["title"] == size:
                        v["available"] = avail


def cycle(cfg, src, st, profiles, tmp):
    got = []
    r = run_cycle(cfg, {}, src, st, FileMarketProvider(tmp / "x.json"), lambda p: got.append(p) or f"m{len(got)}", profiles=profiles)
    return r, got


def mentioned(got):
    return [u for p in got for u in p.get("allowed_mentions", {}).get("users", [])]


SNK_EU = Profile("1", "zapas 44,5", sizes={"44.5"}, regions={"Envío a España"})


def test_sneakers_mundo_undefeated(tmp_path):
    cfg = MonitorConfig("undefeated", "shopify", "UNDEFEATED.COM", "https://undefeated.com", channel="sneakers_world",
                        country="US", include_vendors=["Nike", "Jordan"], ships_es="sí")
    src, st = Src("undefeated", "undefeated.com"), Store(tmp_path / "s.db")
    nike_fan = Profile("2", "Nike sin talla", brands={"Nike"})
    cycle(cfg, src, st, [SNK_EU, nike_fan], tmp_path)
    src.set("JERSEY", "- / M", True)
    r, got = cycle(cfg, src, st, [SNK_EU, nike_fan], tmp_path)
    assert r["sent"] == 1 and mentioned(got) == ["2"]                    # sale y menciona al que sigue Nike sin talla
    _, again = cycle(cfg, src, st, [SNK_EU, nike_fan], tmp_path)
    assert again == []                                                   # silencio: nada cambia


def test_baloncesto_baskets_half_sizes(tmp_path):
    cfg = MonitorConfig("shop:baskets-store.com", "shopify", "BASKETS-STORE.COM", "https://baskets-store.com", channel="baloncesto",
                        include_vendors=["New Balance"], ships_es="sí")
    src, st = Src("baskets", "baskets-store.com"), Store(tmp_path / "s.db")
    m445, m43 = Profile("3", "44,5", brands={"New Balance"}, sizes={"44.5"}), Profile("4", "43", brands={"New Balance"}, sizes={"43"})
    src.set("URC562DO", "44 1/2 / Green", False)
    cycle(cfg, src, st, [m445, m43], tmp_path)
    src.set("URC562DO", "44 1/2 / Green", True)                         # vuelve la «44 1/2» (formato real de la tienda)
    r, got = cycle(cfg, src, st, [m445, m43], tmp_path)
    assert r["sent"] == 1 and mentioned(got) == ["3"]                    # el de la 44,5 sí; el de la 43, silencio


def test_skate_flatspot_uk_sizes(tmp_path):
    cfg = MonitorConfig("shop:flatspot.com", "shopify", "FLATSPOT.COM", "https://flatspot.com", channel="skate", country="GB",
                        include_vendors=["Nike SB", "Nike"], ships_es="sí")
    src, st = Src("flatspot", "flatspot.com"), Store(tmp_path / "s.db")
    uk = Profile("5", "UK 9,5", sizes={"44.5"}, uk_sizes={"9.5"})
    cycle(cfg, src, st, [uk, SNK_EU], tmp_path)
    src.set("SB Dunk", "UK 9.5 / Black", True)
    r, got = cycle(cfg, src, st, [uk, SNK_EU], tmp_path)
    assert r["sent"] == 1 and mentioned(got) == ["5"]                    # solo quien dio su talla UK; el de EU, silencio


def test_outlet_asos_sample_apparel_never_matches_shoe_size(tmp_path):
    cfg = MonitorConfig("shop:eu.asossamplesale.com", "shopify", "ASOS SAMPLE", "https://eu.asossamplesale.com", channel="outlet",
                        ships_es="sí")
    src, st = Src("asossample", "eu.asossamplesale.com"), Store(tmp_path / "s.db")
    shoe44 = Profile("6", "EU 44", sizes={"44"})
    anyone = Profile("7", "outlet sin talla", families={"Rebajas"})
    cycle(cfg, src, st, [shoe44, anyone], tmp_path)
    src.set("HUGO", "XXL - EU 44 / White", True)                        # «EU 44» de ROPA
    r, got = cycle(cfg, src, st, [shoe44, anyone], tmp_path)
    assert r["sent"] == 1 and mentioned(got) == ["7"]                    # el de zapatilla EU 44 NO (es ropa)


def test_streetwear_goodhood_keeps_store_currency(tmp_path):
    cfg = MonitorConfig("goodhood", "shopify", "GOODHOOD", "https://goodhoodstore.com", channel="streetwear", currency="GBP",
                        country="GB", ships_es="sí")
    src, st = Src("goodhood", "goodhoodstore.com"), Store(tmp_path / "s.db")
    cycle(cfg, src, st, [], tmp_path)
    src.set("Goadome", "UK5", True)
    r, got = cycle(cfg, src, st, [], tmp_path)
    txt = json.dumps(got, ensure_ascii=False)
    assert r["sent"] == 1 and "GBP" in txt or "£" in txt
    assert "174,99 €" not in txt and "174.99 €" not in txt              # nunca se presenta en euros un precio en libras


def test_pokemon_tcg_redgoblin_no_size_claim(tmp_path):
    cfg = MonitorConfig("shop:redgoblin.ro", "shopify", "RED GOBLIN", "https://redgoblin.ro", channel="coleccionables", country="RO",
                        ships_es="sí")
    src, st = Src("redgoblin", "redgoblin.ro"), Store(tmp_path / "s.db")
    poke = Profile("8", "Pokémon", families={"Pokémon-TCG"}, keywords=["pokemon"])
    snk = Profile("9", "solo sneakers", families={"Sneakers"})
    cycle(cfg, src, st, [poke, snk], tmp_path)
    src.set("Ditto", "Default Title", True)
    r, got = cycle(cfg, src, st, [poke, snk], tmp_path)
    title = got[0]["embeds"][0]["title"]
    assert r["sent"] == 1 and mentioned(got) == ["8"] and "VUELVE LA" not in title    # sin talla inventada; el de sneakers calla
