from __future__ import annotations

import logging
import os
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
    if mcfg.type == "bstn":
        from .sources.bstn import BstnSource
        return BstnSource(mcfg.regions, mcfg.listings)
    if mcfg.type == "shopify":
        return ShopifySource(mcfg.store, mcfg.base_url, mcfg.currency, pages=mcfg.pages, collection=mcfg.collection,
                             deep_pages=1 if mcfg.collection else mcfg.deep_pages)
    if mcfg.type == "jsonld":
        from .sources.jsonld import JsonLdSource
        return JsonLdSource(mcfg.store, mcfg.base_url, mcfg.currency, listing_urls=mcfg.listing_urls,
                            product_link_pattern=mcfg.product_link_pattern, watch_urls=mcfg.watch_urls,
                            products_per_cycle=mcfg.products_per_cycle)
    if mcfg.type == "rss":
        return RssSource(mcfg.store, mcfg.base_url, mcfg.currency)
    raise ValueError(f"tipo de fuente desconocido: {mcfg.type}")


def _edit_in_place(store, sender, key):
    """Devuelve edit(payload): edita el mensaje fijado `key` o lo crea la primera vez."""
    def edit(payload):
        mid = store.alert_message_id(key)
        try:
            if mid:
                return sender.edit(mid, payload)
        except RuntimeError:
            pass
        store.record_alert(key, "raffle_list", "-", "-", sender.send(payload))
    return edit


def raffle_targets(env, store_name: str):
    """Canales de un raffle de `store_name`, en orden: #raffles-<tienda> (las menciones van aquí), #<tienda> con
    etiqueta RAFFLE y el agregado #raffles. Solo los que tienen webhook propio en .env."""
    from .raffle_router import Target, keyname
    k = keyname(store_name).upper()
    out = []
    for ch, key, lab in ((f"raffles_{k.lower()}", f"DISCORD_WEBHOOK_RAFFLES_{k}", False),
                         (f"tienda_{k.lower()}", f"DISCORD_WEBHOOK_TIENDA_{k}", True),
                         ("raffles", "DISCORD_WEBHOOK_RAFFLES", False)):
        if env.get(key):
            out.append(Target(ch, WebhookSender(env[key]), lab))
    return out


def build_forum_and_raffles(cfg: Config, store: Store, mcfg=None):
    """Foro de lanzamientos y tablón de raffles si existen sus webhooks propios (no se usa el general para un foro)."""
    import os
    from .forum import Forum, WebhookForum
    from .members import load_profiles
    from .raffle_router import RaffleRouter, raffle_wants
    from .raffles import RaffleBoard
    forum = board = None
    if (u := os.environ.get("DISCORD_WEBHOOK_LANZAMIENTOS")):
        forum = Forum(store, WebhookForum(u))
    targets = raffle_targets(os.environ, getattr(mcfg, "store", "") or "")
    if targets:
        try:
            wants = raffle_wants(load_profiles(cfg.defaults.get("members_file", "config/miembros.toml")))
        except Exception:   # noqa: BLE001 — sin perfiles: los avisos salen sin mencionar a nadie
            wants = None
        router = RaffleRouter(store, targets, guild_id=os.environ.get("DISCORD_GUILD_ID"), wants=wants)
        agg = os.environ.get("DISCORD_WEBHOOK_RAFFLES")
        hoy = os.environ.get("DISCORD_WEBHOOK_RAFFLES_CIERRAN_HOY")
        board = RaffleBoard(store, router=router,
                            edit_list=_edit_in_place(store, WebhookSender(agg), "raffles-lista") if agg else None,
                            edit_today=_edit_in_place(store, WebhookSender(hoy), "raffles-cierran-hoy") if hoy else None)
    return forum, board


def next_wait(mcfg, res: dict, failures: int, cap: int, rnd=None) -> tuple[float, str]:
    """Espera hasta la próxima lectura: el intervalo con ±10 % de variación (las tiendas no reciben peticiones en el
    mismo segundo); tras errores, espera creciente; si la tienda pide frenar (429 / Retry-After), se respeta."""
    import random
    r = rnd or random.random
    base = mcfg.interval_seconds
    if res.get("ok"):
        return base * (0.9 + 0.2 * r()), "normal"
    wait = min(base * 2 ** failures, cap)
    if res.get("backoff", 0) > wait:
        return float(res["backoff"]), "la tienda pidió esperar"
    return wait * (0.9 + 0.2 * r()), "error, espera creciente"


def _launch_loop(mcfg, cfg: Config, store: Store, stop: threading.Event):
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    from .launches import build_launch_digest, run_launch_cycle
    senders = {}
    for kind, ch in mcfg.launch_channels.items():
        if (u := cfg.webhook_for(ch)):
            senders[kind] = WebhookSender(u).send
    for r in cfg.ping_rules:
        if (u := cfg.webhook_for(r.channel)):
            senders[r.channel] = WebhookSender(u).send
    if "launch" not in senders:
        log.error("monitor=%s sin webhook para '%s' ni DISCORD_WEBHOOK_DEFAULT; no arranca", mcfg.name, mcfg.launch_channels.get("launch"))
        return
    forum, board = build_forum_and_raffles(cfg, store, mcfg)
    source = make_source(mcfg)
    import zlib
    stop.wait(zlib.crc32(mcfg.name.encode()) % min(30, mcfg.interval_seconds))   # arranque escalonado
    failures = 0
    digest_at = cfg.defaults.get("launch_digest_time", "09:00")
    while not stop.is_set():
        try:
            res = run_launch_cycle(mcfg, cfg.defaults, source, store, senders, ping_rules=cfg.ping_rules,
                                   forum=forum, raffle_board=board)
        except Exception as e:  # p. ej. Discord caído: el hilo sigue vivo y reintenta con espera
            log.exception("monitor=%s fallo inesperado", mcfg.name)
            store.record_health(mcfg.name, False, error=f"{type(e).__name__}: {e}")
            res = {"ok": False, "error": str(e)}
        # resumen diario "abiertos ahora / próximos 7 días"
        now = datetime.now(ZoneInfo("Europe/Madrid"))
        key = f"digest|{mcfg.store}|{now.date().isoformat()}"
        if res.get("ok") and now.strftime("%H:%M") >= digest_at and not store.has_alert(key):
            dg = (forum.next_7_days(now.timestamp(), os.environ.get("DISCORD_GUILD_ID", "")) if forum is not None else
                  build_launch_digest(store.load_launch_states(mcfg.store), now,
                                      title=f"Resumen del día — {mcfg.store}: abiertos ahora y próximos 7 días"))
            if dg:
                send = senders.get("digest") or senders["launch"]
                store.record_alert(key, "launch_digest", mcfg.store, "-", send(dg))
        failures = 0 if res["ok"] else failures + 1
        wait, why = next_wait(mcfg, res, failures, 3600)
        store.set_schedule(mcfg.name, mcfg.interval_seconds, wait, why)
        if not res["ok"]:
            log.warning("monitor=%s error=%s próximo intento en %ss", mcfg.name, res.get("error"), wait)
        log.info("monitor=%s %s", mcfg.name, res)
        stop.wait(wait)


def store_channel_key(mcfg) -> str:
    """Clave del canal dedicado de una tienda: DISCORD_WEBHOOK_TIENDA_<NOMBRE> (lo crea INSTALAR_SERVIDOR)."""
    import re
    return "tienda_" + re.sub(r"[^a-z0-9]+", "_", mcfg.name.lower().removeprefix("shop:")).strip("_")


SAMPLE = None          # #muestra-gratis: se activa en run_all si existe DISCORD_WEBHOOK_MUESTRA


def _registro(text: str):
    """#registro-bot (staff): fuentes que caen y se recuperan. Sin webhook propio no se publica (nunca al general)."""
    if (u := os.environ.get("DISCORD_WEBHOOK_REGISTRO")):
        try:
            WebhookSender(u, max_retries=1).send({"content": text[:1900], "allowed_mentions": {"parse": []}})
        except Exception:   # noqa: BLE001
            log.warning("registro-bot no disponible")


def _loop(mcfg, cfg: Config, store: Store, market, stop: threading.Event, forum=None):
    if mcfg.type == "bstn":
        return _launch_loop(mcfg, cfg, store, stop)
    if mcfg.collection and forum is not None and mcfg.channel == "lanzamientos":
        # #lanzamientos es un FORO: los nuevos lanzamientos van a su hilo y las tallas que vuelven, a #restocks
        from dataclasses import replace as _r
        mcfg = _r(mcfg, channel="restocks")
    url = cfg.webhook_for(mcfg.channel)
    if not url:
        log.error("monitor=%s sin webhook DISCORD_WEBHOOK_%s; no arranca", mcfg.name, mcfg.channel.upper())
        return
    sender = WebhookSender(url)
    source = make_source(mcfg)
    # arranque escalonado: con cientos de tiendas, no todas a la vez (0-120 s según el nombre, estable entre reinicios)
    import zlib
    stop.wait(zlib.crc32(mcfg.name.encode()) % min(120, mcfg.interval_seconds))
    from .dedicated import load_dedicated
    dedicated = load_dedicated(cfg.defaults.get("dedicated_file", "config/canales_dedicados.toml"))
    possible = set(dedicated.by_monitor.get(mcfg.name, [])) | set(dedicated.by_country.get((mcfg.country or "").upper(), [])) \
        | {k for k, _ in dedicated.topics}
    wanted = ({r.channel for r in cfg.ping_rules} | {r["channel"] for r in cfg.defaults.get("discount_routes", [])}
              | {k for k in possible if os.environ.get("DISCORD_WEBHOOK_" + k.upper())})   # solo con webhook PROPIO
    channel_senders = {ch: WebhookSender(u).send for ch in wanted if (u := cfg.webhook_for(ch))}
    from .members import load_profiles
    profiles = load_profiles(cfg.defaults.get("members_file", "config/miembros.toml"))
    failures = 0
    send = sender.send
    if SAMPLE is not None:
        def send(p, _s=sender.send):           # lo entregado a suscriptores puede pasar a la muestra (con retraso)
            mid = _s(p)
            SAMPLE.offer(p, time.time())
            return mid
    while not stop.is_set():
        try:
            res = run_cycle(mcfg, cfg.defaults, source, store, market, send,
                            ping_rules=cfg.ping_rules, channel_senders=channel_senders, profiles=profiles,
                            forum=forum, dedicated=dedicated)
        except Exception as e:
            log.exception("monitor=%s fallo inesperado", mcfg.name)
            store.record_health(mcfg.name, False, error=f"{type(e).__name__}: {e}")
            res = {"ok": False, "error": str(e)}
        if res["ok"]:
            if failures >= 3:
                _registro(f"✅ {mcfg.name} vuelve a leer correctamente")
            failures = 0
        else:
            failures += 1
            if failures == 3:
                _registro(f"⚠️ {mcfg.name}: 3 fallos seguidos · {str(res.get('error'))[:300]}")
        wait, why = next_wait(mcfg, res, failures, 1800)
        store.set_schedule(mcfg.name, mcfg.interval_seconds, wait, why)
        if not res["ok"]:
            log.warning("monitor=%s error=%s próximo intento en %ss", mcfg.name, res.get("error"), wait)
        log.info("monitor=%s %s", mcfg.name, res)
        stop.wait(wait)


def _calendar_loop(cfg: Config, store: Store, stop: threading.Event, path: str):
    """Relee el calendario en cada vuelta: el staff puede editarlo sin reiniciar."""
    from datetime import datetime, timezone

    from .releases import calendar_tick, load_calendar
    sender = None
    while not stop.is_set():
        try:
            cal = load_calendar(path)
            url = cfg.webhook_for(cal.channel)
            if not url:
                log.error("calendario sin webhook DISCORD_WEBHOOK_%s; no se envía", cal.channel.upper())
            else:
                sender = sender or WebhookSender(url)
                n = calendar_tick(cal, datetime.now(timezone.utc), store, sender.send)
                if n:
                    log.info("calendario: %s avisos enviados", n)
        except Exception as e:  # un error de edición del fichero no debe tumbar los monitores
            log.error("calendario: %s", e)
        stop.wait(60)


def run_all(cfg: Config, db_path: str = "cookgroup.db"):
    store = Store(db_path)
    market = FileMarketProvider(cfg.defaults.get("market_file", "config/market_data.json"))
    stop = threading.Event()
    forum, _board = build_forum_and_raffles(cfg, store)
    global SAMPLE
    if (mu := os.environ.get("DISCORD_WEBHOOK_MUESTRA")):
        from .sample_feed import SampleFeed
        SAMPLE = SampleFeed()

        def _sample_loop(_snd=WebhookSender(mu)):
            while not stop.is_set():
                for p in SAMPLE.due(time.time()):
                    try:
                        _snd.send(p)
                    except Exception:   # noqa: BLE001
                        log.warning("muestra-gratis: envío fallido")
                stop.wait(60)
        threading.Thread(target=_sample_loop, name="muestra", daemon=True).start()
    threads = [threading.Thread(target=_loop, args=(m, cfg, store, market, stop, forum), name=m.name, daemon=True)
               for m in cfg.monitors if m.enabled]
    if (rf := cfg.defaults.get("releases_file")):
        threads.append(threading.Thread(target=_calendar_loop, args=(cfg, store, stop, rf), name="calendar", daemon=True))
    for t in threads:
        t.start()
    from .diagnostics import write_heartbeat
    beat = 0.0
    try:
        while any(t.is_alive() for t in threads):
            if time.monotonic() - beat >= 30:   # latido para ESTADO.bat: ¿sigue vivo el proceso?
                try:
                    write_heartbeat(len(threads), sum(t.is_alive() for t in threads))
                except OSError:
                    pass
                try:                            # v1.1: panel de tiendas en directo (la página se recarga sola)
                    from .store_panel import write_store_panel
                    write_store_panel(store, cfg)
                except Exception:   # noqa: BLE001 — el panel nunca debe parar el bot
                    log.exception("panel de tiendas")
                beat = time.monotonic()
            time.sleep(1)
    except KeyboardInterrupt:
        stop.set()
