"""v0.9: matriz de permisos de un servidor de pago, comprobada con identidades de prueba."""
from pathlib import Path

from cookgroup.access import (EVERYONE, MOD, SUB, VIEW, can, channel_overwrites, effective, is_entitled, matrix,
                              private_thread_visible)
from cookgroup.members import Profile, decide
from cookgroup.server_setup import load_design

D = load_design(Path(__file__).resolve().parents[1] / "config/servidor.toml")
M = {r["canal"]: r for r in matrix(D)}


def test_visitor_sees_only_public():
    vis = {c for c, r in M.items() if r["visitante"] != "—"}
    assert vis == {"bienvenida", "normas", "elige-tus-avisos", "guía-de-avisos", "anuncios", "planes", "muestra-gratis", "soporte"}
    assert M["soporte"]["visitante"] == "ve y abre ticket privado"


def test_subscriber_gets_contracted_content_but_not_staff():
    assert M["sneakers-eu"]["suscriptor"] == "ve" and M["chat"]["suscriptor"] == "ve y escribe"
    assert M["pruebas-bot"]["suscriptor"] == "—" and M["moderación"]["suscriptor"] == "—"


def test_former_subscriber_loses_access_even_with_preferences_and_old_link():
    for c, r in M.items():
        assert r["ex-suscriptor"] == r["visitante"], c          # preferencias (Nike, EU 44,5…) no dan acceso
    ow = channel_overwrites("suscriptores", "lectura")
    assert not can(effective({"Nike", "EU 44,5", "Sneakers"}, ow), VIEW)   # el enlace antiguo no abre nada


def test_team_and_owner():
    assert all(r["propietario"] != "—" for r in M.values())
    assert M["moderación"]["moderador"] == "ve y escribe" and M["moderación"]["staff"] == "ve y escribe"


def test_tickets_private_to_client_and_team():
    ow = channel_overwrites("todos", "tickets")
    assert private_thread_visible(set(), True, ow)                    # el cliente que lo abrió
    assert not private_thread_visible({SUB}, False, ow)               # otro cliente no
    assert private_thread_visible({MOD}, False, ow)                   # el equipo sí


def test_preferences_only_personalize_for_entitled():
    from cookgroup.models import Event, EventType, Product, Variant
    p = Product("T", "1", "Nike Dunk", "https://t", "EUR", (Variant("v", "44.5", 10000, True),), vendor="Nike")
    ev = Event(EventType.RESTOCK, p, p.variants)
    roles = ["Sneakers", "Nike", "EU 44,5", "Envío a España"]
    ex = Profile.from_roles("1", "ex", roles, D)
    sub = Profile.from_roles("2", "sub", roles + [SUB], D)
    assert not ex.entitled and "sin suscripción" in decide(ex, ev, channel="sneakers", family="Sneakers", ships_es="sí").reason
    assert sub.entitled and decide(sub, ev, channel="sneakers", family="Sneakers", ships_es="sí").notify
    assert is_entitled({MOD}) and not is_entitled({"Nike"})
