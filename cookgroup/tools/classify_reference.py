"""Clasifica docs/reference_stores.tsv → docs/reference_classified.tsv y config/shopify_stores.csv.

Heurísticas (se registran como "inferido"; la verificación real la hace `cookgroup probe`):
- plataforma: Shopify si aparece en canales shopify-* / skateshops con firma ZTYSHOPIFY o dominio *.myshopify.com;
  "mesh" (grupo JD: JD Sports, size?, Footpatrol) por canal mesh-*; marcas y cadenas con plataforma propia aparte.
- categoría: TCG/coleccionables por palabras del dominio/nombre; skate; baloncesto; sneakers; streetwear/moda.
- país: TLD (.es → ES, .de → DE…); .com/.eu → por confirmar.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

TLD = {"es": "ES", "de": "DE", "fr": "FR", "it": "IT", "nl": "NL", "be": "BE", "at": "AT", "ch": "CH", "dk": "DK", "se": "SE",
       "pl": "PL", "cz": "CZ", "sk": "SK", "ro": "RO", "gr": "GR", "lu": "LU", "ie": "IE", "no": "NO", "uk": "GB", "co.uk": "GB",
       "com.au": "AU", "co.nz": "NZ", "ca": "CA", "com.sg": "SG", "my": "MY", "co.il": "IL", "com.tr": "TR", "co.id": "ID",
       "berlin": "DE", "paris": "FR", "pt": "PT"}
KNOWN = {  # dominios .com/.eu conocidos (país de la tienda)
    "aw-lab.com": "IT", "solebox.com": "DE", "snipes.com": "DE", "newbalance.com": "US", "nike.com": "US", "farfetch.com": "GB",
    "sportsshoes.com": "GB", "asphaltgold.com": "DE", "warsawsneakerstore.com": "PL", "sneakersnstuff.com": "SE",
    "oneblockdown.com": "IT", "footdistrict.com": "ES", "goodhoodstore.com": "GB", "flatspot.com": "GB", "slamjam.com": "IT",
    "starcowparis.com": "FR", "overkillshop.com": "DE", "endclothing.com": "GB", "nakedcph.com": "DK", "bstn.com": "DE",
    "basketballemotion.com": "ES", "43einhalb.com": "DE", "basket4ballers.com": "FR", "luisaviaroma.com": "IT", "kickz.com": "DE",
    "sivasdescalzo.com": "ES", "skatedeluxe.com": "DE", "voostore.com": "DE", "milk-store.com": "DE", "shoebacca.com": "US",
    "thinkempire.com": "US", "prm.com": "PL", "kith.com": "US", "eu.kith.com": "US", "dtlr.com": "US", "undefeated.com": "US",
    "extrabutterny.com": "US", "concepts.com": "US", "footpatrol.com": "GB", "size.co.uk": "GB", "family3-0.com": "FR",
    "afew-store.com": "DE", "en.afew-store.com": "DE", "de.afew-store.com": "DE", "rufusmacba.com": "ES", "laplazaskateshop.com": "ES",
    "titus-shop.com": "DE", "yellowshop.es": "ES", "tascon.es": "ES", "24segons.es": "ES", "elcorteingles.es": "ES",
    "breuninger.com": "DE", "boozt.com": "SE", "unisportstore.de": "DK", "mytheresa.com": "DE", "courir.com": "FR",
    "aboutyou.com": "DE", "asos.com": "GB", "farfetch": "GB", "ssense.com": "CA", "revolve.com": "US", "18montrose.com": "GB",
    "highrollersdublin.com": "IE", "routeone.co.uk": "GB", "juicestore.com": "HK", "lelabostore.com": "IT", "5pm.fr": "FR",
    "plaza.dk": "DK", "blackboxstore.com": "IT", "specialmilano.com": "IT", "nugnes1920.com": "IT", "maha-amsterdam.com": "NL",
    "capitansiroco.com": "ES", "patta.nl": "NL", "delastore.com": "NL", "dope-factory.com": "DE", "skstore.eu": "ES",
    "shinzo.paris": "FR", "opiumparis.com": "FR", "ferrari.com": "IT", "store.ferrari.com": "IT", "shop.rfef.es": "ES",
    "consortium.co.uk": "GB", "offspring.co.uk": "GB", "footasylum.com": "GB", "office.co.uk": "GB", "schuh.eu": "GB",
    "jbalvin.com": "CO", "jbalvinshop.com": "CO", "atmos.co.id": "ID", "nubiantokyo.com": "JP", "shoepalace.com": "US",
    "shopwss.com": "US", "gbny.com": "US", "humiditynola.com": "US", "sneakerjunkiesusa.com": "US", "losangelesarchive.com": "US",
    "scalperscompany.com": "ES", "esdemarca.com": "ES", "culturaurbanashop.es": "ES", "alcarrerskateshop.com": "ES",
    "sunnystore.es": "ES", "blackvinylrecordsspain.com": "ES", "bouncewear.com": "ES", "bouncewear.es": "ES", "dbrandstore.es": "ES",
    "cuylas.com": "ES", "ixudeviance.com": "ES", "kolablisbon.com": "PT", "futbolemotion.com": "ES", "es.miinto.com": "ES",
    "ajogar.com": "PT", "pukassurfshop.com": "ES", "1290sqm.com": "IT", "stress95.com": "IT", "hyperice.com": "US",
    "wit-training.com": "IT", "lovellsports.com": "GB", "gameon.games": "GB", "thedarkslide.com": "GB", "welcomesk8.com": "IT",
    "schuhdealer.de": "DE", "canary---yellow.com": "FR", "crtz.xyz": "GB", "supreme.com": "US", "eu.supreme.com": "US",
    "palace-skateboards-eu.myshopify.com": "GB", "eu.stussy.com": "US", "uk.stussy.com": "US", "carhartt-wip.com": "DE",
    "vans.com": "US", "ugg.com": "US", "asics.com": "JP", "converse.com": "US", "revolve": "US"}
NON_STORE = {"instagram.com", "e.yeet.ai", "supremecommunity.com", "newcop.com", "adidas.onelink.me", "raffle.bstn.com",
             "checkout.complex.com", "launchesuk.topps.com", "topps.runfair.com"}
DEALS = {"chollometro.com", "dealabs.com", "mydealz.de", "hotukdeals.com", "pepper.pl"}
TCG = re.compile(r"card|poke|tcg|ccg|game|manga|collect|cards|yonko|gargoyle|brick|dice|toys|vinyl|records|play-maniac|kingdultes|metamorph|"
                 r"protector|thronestore|lvlup|juwelier|plentyof|senpai|relic|kofuku|hikaru|gamesalley|strongames|lagilda|olakala|"
                 r"tradingcards|redgoblin|kimskram|magicnerd|funside|zardo|envoy|noteshop|loadeddice|hobbytech|cardyx|"
                 r"cherry|thepokehive|beatles|crashrecords", re.I)
SKATE = re.compile(r"skate|sk8|board|surf|ramp|darkslide|flatspot|plaze|tx-sports|colorskates|soohot|civilist|ben-g|lobby|"
                   r"rufusmacba|laplaza|routeone|highrollers|empireskate|welcome|milk-store|bonkers|alcarrer|pivot|7hills|streetart|"
                   r"skateshop|blitzsurf|subsect|localskate|boardcollective|ojskate|digitalskate|cybercafe", re.I)
BASKET = re.compile(r"basket|bounce|slamdunk|airdom|weplay|skstore|24segons", re.I)


def country(dom: str) -> str:
    if dom in KNOWN:
        return KNOWN[dom]
    base = dom.split(".", 1)[-1] if dom.count(".") > 1 else dom
    for k in sorted(TLD, key=len, reverse=True):
        if dom.endswith("." + k):
            return TLD[k]
    return KNOWN.get(base, "")


def platform(dom: str, names: str, chans: set[str]) -> str:
    if dom in NON_STORE:
        return "no es tienda"
    if dom in DEALS:
        return "rss pepper"
    if dom.endswith("myshopify.com") or "ZTYSHOPIFY" in names or chans & {"shopify-eu", "shopify-eu-unfiltered", "shopify-all",
            "shopify-rebajas-eu", "shopify-rebajas-30disc", "shopify-rebajas-60disc", "shopify-rebajas-all", "asos-sample",
            "corteiz", "palace", "stussy", "goodhood", "asphaltgold", "footdistrict", "kitheu", "naked", "slamjam",
            "sneakersnstuff", "voostore", "starcow", "canary-yellow", "overkill-oneblockdown", "dsml"}:
        return "shopify"
    if re.search(r"jdsports|sizeofficial|size\.co\.uk|footpatrol", dom):
        return "mesh (grupo JD)"
    if re.search(r"zalando|soleback", dom):
        return "zalando"
    if re.search(r"nike\.com|adidas|newbalance|asics|converse|vans\.com|ugg\.com|timberland|underarmour|supreme\.com|carhartt", dom):
        return "marca (web propia)"
    if dom in ("amazon.es",):
        return "amazon"
    if "privalia" in dom or "miravia" in dom or "lidl" in dom or "pccomponentes" in dom:
        return "retail/outlet propio"
    if chans & {"skateshops", "basket-shops"}:
        return "propia/por confirmar (skate/basket)"
    return "propia/por confirmar"


def category(dom: str, names: str, chans: set[str]) -> str:
    t = dom + " " + names
    if dom in DEALS:
        return "chollos"
    if TCG.search(t) and not re.search(r"sneaker|shoe|skate", t, re.I):
        return "coleccionables/TCG"
    if SKATE.search(t) or "skateshops" in chans:
        return "skate"
    if BASKET.search(t) or chans & {"basket-shops", "basket4ballers", "basketballemotion"}:
        return "baloncesto"
    if chans & {"privalia-productos", "privalia-campañas", "privalia-articulos", "zalando-prive", "zalandoprive-campañas",
                "amazon-haul", "amazon-error", "amazon-sale", "lidl", "miravia", "pccomponentes", "aboutyou-yoox", "asos-sample"}:
        return "outlet/retail"
    if re.search(r"ferrari|jacquemus|mytheresa|farfetch|ssense|luisaviaroma|revolve|tres-bien|ceciliebahnsen|walesbonner|"
                 r"nugnes|specialmilano|antonia|carmenboutique|deliberti|vittoriocitro|sergiofabbri|cappelletto|bananabenz|"
                 r"fusco|camden|space23|stoy|andpants|maharishi", t, re.I):
        return "moda/lujo"
    if chans & {"corteiz", "palace", "stussy", "supreme"} or re.search(r"stussy|supreme|crtz|corteiz|palace|kith|patta|"
                                                                       r"goodhood|carhartt|1290|stress95|maha", t, re.I):
        return "streetwear"
    return "sneakers/deporte"


def main():
    rows = list(csv.DictReader((DOCS / "reference_stores.tsv").open(encoding="utf-8"), delimiter="\t"))
    out = []
    for r in rows:
        dom = r["domain"].lower().removeprefix("www.")
        chans = set(filter(None, r["channels"].split(",")))
        r.update(platform=platform(dom, r["names"], chans), category=category(dom, r["names"], chans),
                 country=country(dom))
        out.append(r)
    with (DOCS / "reference_classified.tsv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), delimiter="\t")
        w.writeheader()
        w.writerows(out)
    # Lote de monitores Shopify (excluye dominios ya configurados a mano y los *.myshopify.com duplicados de una web pública)
    import tomllib
    cfg = tomllib.loads((ROOT / "config" / "monitors.toml").read_text())
    have = {re.sub(r"^https?://(www\.)?", "", m["base_url"]).split("/")[0] for m in cfg.get("monitor", [])}
    disabled = {"milk-store.com": "no responde (20-nov-2026)"}
    dup_myshopify = {"sns-prod.myshopify.com", "uk-goodhood.myshopify.com", "gymshark-eur.myshopify.com"}
    chan = {"sneakers/deporte": "sneakers", "streetwear": "streetwear", "moda/lujo": "streetwear", "skate": "skate",
            "baloncesto": "baloncesto", "coleccionables/TCG": "coleccionables", "outlet/retail": "outlet"}
    with (ROOT / "config" / "shopify_stores.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["domain", "name", "country", "category", "channel", "enabled", "source"])
        n = 0
        for r in out:
            dom = r["domain"].lower().removeprefix("www.")
            if r["platform"] != "shopify" or dom in have or dom in dup_myshopify or dom.startswith("checkout."):
                continue
            name = r["names"].split("/")[0].strip()
            if name.upper() in ("ZTYSHOPIFY", "SHOPIFY MONITOR", "OTROS RELEASES", "AIO CUSTOM") or name.startswith("http"):
                name = dom
            w.writerow([dom, name.title() if name.isupper() else name, r["country"], r["category"],
                        chan.get(r["category"], "sneakers"), "0" if dom in disabled else "1",
                        "referencia:" + r["channels"].split(",")[0]])
            n += 1
    print(f"{len(out)} dominios clasificados; {n} tiendas Shopify en config/shopify_stores.csv")


if __name__ == "__main__":
    main()
