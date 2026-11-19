"""Tests sobre MUESTRAS REALES capturadas el 19-nov-2026 (formato real de las fuentes; los datos cambian a diario)."""
import json
from pathlib import Path

import pytest

from cookgroup.config import MonitorConfig
from cookgroup.discord import base_sku, build_embed
from cookgroup.filters import product_passes
from cookgroup.models import Event, EventType
from cookgroup.normalize import clean_variants, is_kids_product, normalize_size, validate_product
from cookgroup.sources.rss import parse_feed
from cookgroup.sources.shopify import parse_products

F = Path(__file__).parent / "fixtures"


def test_family30_real_payload_parses_and_normalises():
    d = json.loads((F / "shopify_family30_REAL_2026-11-19.json").read_text())
    p = parse_products(d, store="Family 3.0", base_url="https://www.family3-0.com", currency="EUR")[0]
    p = clean_variants(p)
    assert validate_product(p) == []
    assert [v.title for v in p.available_variants] == ["40", "41", "42.5"]
    assert p.url == "https://www.family3-0.com/products/nike-mind-001-hq4307-001-fw26"
    assert base_sku([v.sku for v in p.variants]) == "HQ4307-001"
    e = build_embed(Event(EventType.RESTOCK, p, p.available_variants, detected_at="2026-11-19T12:00:00+00:00"))["embeds"][0]
    vals = {f["name"]: f["value"] for f in e["fields"]}
    assert vals["SKU"] == "`HQ4307-001`" and vals["Precio"] == "90,00 €" and "stockx.com/search?s=HQ4307-001" in vals["Enlaces"]


# Formatos de talla vistos el 19-nov-2026 en tiendas reales (Slam Jam, Kith EU, SNS, Goodhood, Voo, Starcow, Family 3.0)
@pytest.mark.parametrize("raw,exp", [
    ("M5.5/W6.5 / Grey", "M5.5/W6.5"), ("2T", "2T"), ("10.5C", "10.5C"), ("4.5", "4.5"), ("Small", "S"),
    ("X-Large", "XL"), ("ONE SIZE", "Única"), ("OS", "Única"), ("Default Title", "Única"), ("42,5", "42.5"),
])
def test_real_size_formats(raw, exp):
    assert normalize_size(raw) == exp


@pytest.mark.parametrize("title,kids", [
    ('Air Jordan 4 Retro OG GS "Bred"', True), ("Air Jordan Retro 4 Toddler (TD)", True),
    ("Kith Kids Toy Story Just Us Tee", True), ('Air Jordan 3 Retro "Not Nice"', False), ("Made in USA 990v7", False),
])
def test_kids_titles_seen_in_real_stores(title, kids):
    assert is_kids_product(title) is kids


def test_chollometro_real_feed():
    ps = parse_feed((F / "chollometro_REAL_2026-11-19.xml").read_text(), store="Chollometro")
    assert [p.title for p in ps][1] == "DOUBLE DRAGON REVIVE - EDICIÓN LIMITADA - PS5"
    a = ps[0]
    assert a.vendor == "AliExpress" and a.variants[0].price_cents == 1983 and "temp:191" in a.tags
    assert a.product_type == "Salud y belleza" and a.image_url.endswith("2078146_1.jpg")
    hot = MonitorConfig("c", "rss", "Chollometro", "https://x", min_temperature=185)
    assert [product_passes(p, hot) for p in ps] == [True, False]
    e = build_embed(Event(EventType.NEW_PRODUCT, a, a.variants, detected_at="2026-11-19T12:45:07+00:00"))["embeds"][0]
    assert e["title"] == "NUEVO CHOLLO — AliExpress vía Chollometro"
    assert {f["name"] for f in e["fields"]} >= {"Precio", "Temperatura", "Categoría"}


def test_preview_renders_all_samples(tmp_path):
    from cookgroup.preview import render_html, sample_payloads, test_payload
    items = sample_payloads()
    assert len(items) >= 9
    page = render_html(items)
    assert page.startswith("<!DOCTYPE html>") and "POSIBLE PRICE ERROR" in page and "Drops del día" in page
    assert "<script" not in page and "onerror" in page
    tp = test_payload()
    assert "PRUEBA" in tp["content"] and tp["allowed_mentions"] == {"parse": []}
