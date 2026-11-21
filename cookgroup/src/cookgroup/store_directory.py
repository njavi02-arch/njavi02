"""Tiendas (v1.1): inventario reconciliado en comercios únicos, lote con canal propio, tarjeta fijada por canal y cifras.

Niveles de una tienda:
  descubierta → está en el inventario (referencia, listas de distribuidores oficiales…)
  piloto      → tiene fuente validada y al menos una señal probada con datos reales
  operativa   → su canal está instalado en Discord y ha recibido una entrega verificada (mensaje confirmado)
"""
from __future__ import annotations

import csv
import json
import re
import tomllib
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

SIGNALS = ("raffle", "lanzamiento", "restock", "rebaja")
SUBDOMAINS = {"www", "en", "de", "eu", "us", "uk", "it", "fr", "es", "nl", "drop", "shop", "store", "m", "row", "intl", "int"}
ALIAS = {"goodhoodstore": "goodhood", "uk-goodhood": "goodhood", "asossamplesale": "asos-sample", "afew-store": "afew",
         "overkillshop": "overkill", "sivasdescalzo": "svd", "endclothing": "end", "baskets-store": "baskets"}
FLAGS = {"ES": "🇪🇸", "DE": "🇩🇪", "FR": "🇫🇷", "IT": "🇮🇹", "PT": "🇵🇹", "NL": "🇳🇱", "BE": "🇧🇪", "GB": "🇬🇧", "SE": "🇸🇪",
         "DK": "🇩🇰", "NO": "🇳🇴", "FI": "🇫🇮", "RO": "🇷🇴", "PL": "🇵🇱", "AT": "🇦🇹", "CH": "🇨🇭", "US": "🇺🇸"}
EU_ORDER = ["ES", "FR", "DE", "IT", "PT", "NL", "BE", "GB", "SE", "DK", "NO", "FI"]


def merchant_key(domain: str) -> str:
    """aw-lab.com, en.afew-store.com, uk-goodhood.myshopify.com → aw-lab, afew, goodhood."""
    d = (domain or "").lower().strip().removeprefix("https://").removeprefix("http://").split("/")[0]
    parts = [p for p in d.split(".") if p]
    if len(parts) >= 3 and parts[-2] == "myshopify":
        base = parts[-3]
    else:
        while len(parts) > 2 and parts[0] in SUBDOMAINS:
            parts = parts[1:]
        if len(parts) >= 3 and len(parts[-2]) <= 3:      # co.uk, com.au
            parts = parts[:-1]
        base = parts[-2] if len(parts) >= 2 else (parts[0] if parts else "")
    base = ALIAS.get(base, base)
    return ALIAS.get(re.sub(r"(-?store|-?shop)$", "", base), re.sub(r"(-?store|-?shop)$", "", base)) or base


def load_lote(path=Path("config/lote_tiendas.toml")) -> list[dict]:
    """Tiendas con canal propio: lote 1 (a mano) y los lotes generados (config/lote2_tiendas.toml…), sin repetir canal."""
    p = Path(path)
    out, seen = [], set()
    for f in [p] + sorted(p.parent.glob("lote[0-9]*_tiendas.toml")):
        if not f.exists():
            continue
        for t in tomllib.loads(f.read_text(encoding="utf-8")).get("tienda", []):
            if t["canal"] not in seen:
                seen.add(t["canal"])
                out.append(t)
    return out


def tested(t: dict) -> list[str]:
    return [s for s in SIGNALS if t.get(s) == "probado"]


def store_card(t: dict) -> dict:
    """Tarjeta corta que se fija en el canal de la tienda."""
    lab = {"probado": "✅ activa", "por-probar": "⏳ en prueba (aún no se publica)", "sin-fuente": "— no disponible"}
    flag = FLAGS.get(t.get("pais", ""), "")
    fields = [{"name": "País", "value": f"{flag} {t.get('pais', '—')}", "inline": True},
              {"name": "Envío a España", "value": t.get("envio_es", "por confirmar"), "inline": True},
              {"name": "Raffles desde España", "value": t.get("raffle_es", "—"), "inline": True},
              {"name": "Web oficial", "value": f"[{urlparse(t['web']).netloc}]({t['web']})", "inline": False}]
    fields += [{"name": s.upper(), "value": lab.get(t.get(s, "sin-fuente"), t.get(s, "")), "inline": True} for s in SIGNALS]
    return {"embeds": [{"title": f"📌 {t['nombre']} — qué publica este canal", "color": 0x5865F2, "fields": fields,
                        "footer": {"text": "Cada aviso lleva su etiqueta: RAFFLE · LANZAMIENTO · RESTOCK · REBAJA. "
                                           "Solo se activan señales probadas con datos reales de la tienda."}}],
            "allowed_mentions": {"parse": []}}


def reconcile(inventory_csv="docs/inventory.csv", monitors=(), lote=()) -> list[dict]:
    """Agrupa las filas del inventario (y los monitores) por comercio único."""
    g = defaultdict(lambda: {"dominios": set(), "filas": 0, "pais": "", "envio_es": "", "estados": defaultdict(int),
                             "monitores": set(), "nombre": "", "categoria": ""})
    if Path(inventory_csv).exists():
        for r in csv.DictReader(open(inventory_csv, encoding="utf-8")):
            k = merchant_key(r["dominio"] or r["tienda"])
            x = g[k]
            x["dominios"].add(r["dominio"])
            x["filas"] += 1
            x["nombre"] = x["nombre"] or r["tienda"]
            x["pais"] = x["pais"] or r["pais"]
            x["categoria"] = x["categoria"] or r["categoria"]
            if r["envio_es"] == "sí" or not x["envio_es"]:
                x["envio_es"] = r["envio_es"]
            x["estados"][r["cobertura"] or "—"] += 1
    for m in monitors:
        k = merchant_key(urlparse(m.base_url).netloc)
        g[k]["monitores"].add(m.name)
        g[k]["dominios"].add(urlparse(m.base_url).netloc.removeprefix("www."))
        g[k]["nombre"] = g[k]["nombre"] or m.store
        g[k]["pais"] = g[k]["pais"] or (m.country or "")
    lot = {merchant_key(urlparse(t["web"]).netloc): t for t in lote}
    out = []
    for k, x in g.items():
        t = lot.get(k)
        out.append({"comercio": k, "nombre": t["nombre"] if t else x["nombre"], "pais": (t or {}).get("pais") or x["pais"],
                    "envio_es": (t or {}).get("envio_es") or x["envio_es"] or "por confirmar", "categoria": x["categoria"],
                    "dominios": sorted(d for d in x["dominios"] if d), "filas_inventario": x["filas"],
                    "duplicadas": max(0, x["filas"] - 1), "estados": dict(x["estados"]), "monitores": sorted(x["monitores"]),
                    "lote": bool(t), "canal": (t or {}).get("canal", ""), "senales": tested(t) if t else [],
                    "nivel": "piloto" if (t and tested(t)) else "descubierta"})
    return sorted(out, key=lambda r: (EU_ORDER.index(r["pais"]) if r["pais"] in EU_ORDER else 99, r["nombre"].lower()))


def write_reconciliation(rows: list[dict], path=Path("docs/v11/TIENDAS_UNICAS.csv")) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["comercio", "nombre", "pais", "envio_es", "nivel", "lote", "canal", "senales_probadas", "monitores",
                    "filas_inventario", "duplicadas", "estados_inventario", "dominios"])
        for r in rows:
            w.writerow([r["comercio"], r["nombre"], r["pais"], r["envio_es"], r["nivel"], "sí" if r["lote"] else "",
                        r["canal"], " ".join(r["senales"]), " ".join(r["monitores"]), r["filas_inventario"], r["duplicadas"],
                        "; ".join(f"{k}:{v}" for k, v in r["estados"].items()), " ".join(r["dominios"])])
    return path


def channel_ids(path=Path("data/canales_ids.json")) -> tuple[str | None, dict]:
    p = Path(path)
    if not p.exists():
        return None, {}
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("guild_id"), d.get("canales", {})
