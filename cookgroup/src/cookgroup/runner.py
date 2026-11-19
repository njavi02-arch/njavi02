from __future__ import annotations

import logging
import threading
import time

from .config import Config
from .discord import WebhookSender
from .market import FileMarketProvider
from .pipeline import run_cycle
from .sources.rss import RssSource
from .sources.shopify import ShopifySource
from .store import Store

log = logging.getLogger("cookgroup")


def make_source(mcfg):
    if mcfg.type == "shopify":
        return ShopifySource(mcfg.store, mcfg.base_url, mcfg.currency)
    if mcfg.type == "rss":
        return RssSource(mcfg.store, mcfg.base_url, mcfg.currency)
    raise ValueError(f"tipo de fuente desconocido: {mcfg.type}")


def _loop(mcfg, cfg: Config, store: Store, market, stop: threading.Event):
    url = cfg.webhook_for(mcfg.channel)
    if not url:
        log.error("monitor=%s sin webhook DISCORD_WEBHOOK_%s; no arranca", mcfg.name, mcfg.channel.upper())
        return
    sender = WebhookSender(url)
    source = make_source(mcfg)
    ping_senders = {r.channel: WebhookSender(u).send for r in cfg.ping_rules if (u := cfg.webhook_for(r.channel))}
    failures = 0
    while not stop.is_set():
        res = run_cycle(mcfg, cfg.defaults, source, store, market, sender.send,
                        ping_rules=cfg.ping_rules, ping_senders=ping_senders)
        if res["ok"]:
            failures = 0
            wait = mcfg.interval_seconds
        else:
            failures += 1
            wait = max(res.get("backoff", 0), min(mcfg.interval_seconds * 2 ** failures, 1800))
            log.warning("monitor=%s error=%s próximo intento en %ss", mcfg.name, res.get("error"), wait)
        log.info("monitor=%s %s", mcfg.name, res)
        stop.wait(wait)


def run_all(cfg: Config, db_path: str = "cookgroup.db"):
    store = Store(db_path)
    market = FileMarketProvider(cfg.defaults.get("market_file", "config/market_data.json"))
    stop = threading.Event()
    threads = [threading.Thread(target=_loop, args=(m, cfg, store, market, stop), name=m.name, daemon=True)
               for m in cfg.monitors if m.enabled]
    for t in threads:
        t.start()
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        stop.set()
