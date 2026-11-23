"""v1.6 · sorteos internos con un Discord simulado: anuncio + 🎉, cierre con ganador entre quienes reaccionaron
(sin bots), un solo resultado aunque se repita la resolución (reinicio), y sorteo desierto."""
from types import SimpleNamespace as NS

from cookgroup.sorteos import Sorteos


class FakeDiscord:
    def __init__(self, reactores):
        self.reactores, self.posts, self.puts, self.n = reactores, [], [], 0

    def post(self, url, headers=None, json=None):
        self.n += 1
        self.posts.append((url, json))
        return NS(status_code=200, json=lambda: {"id": str(9000 + self.n)})

    def put(self, url, headers=None):
        self.puts.append(url)
        return NS(status_code=204, json=lambda: {})

    def get(self, url, headers=None, params=None):
        after = (params or {}).get("after")
        lst = [u for u in self.reactores if not after or int(u["id"]) > int(after)][:100]
        return NS(status_code=200, json=lambda: lst)


def test_sorteo_completo(tmp_path):
    gente = [{"id": str(100 + i)} for i in range(150)] + [{"id": "1", "bot": True}]     # 150 miembros (2 páginas) + el bot
    d = FakeDiscord(gente)
    s = Sorteos(str(tmp_path / "s.db"), d, "TOKEN")
    s.crear("555", "Pokémon 151 ETB", minutos=60, ganadores=2, now=0)
    assert "SORTEO · Pokémon 151 ETB" in d.posts[0][1]["embeds"][0]["title"] and d.puts      # anuncio + 🎉 del bot
    assert s.resolver_vencidos(now=1800) == []                                              # aún abierto
    r = s.resolver_vencidos(now=3601)
    assert r[0]["participantes"] == 150 and len(r[0]["ganadores"]) == 2 and "1" not in r[0]["ganadores"]
    res = d.posts[-1][1]
    assert res["allowed_mentions"]["users"] == r[0]["ganadores"] and r[0]["semilla"] in res["content"]
    n = len(d.posts)
    assert s.resolver_vencidos(now=99999) == [] and len(d.posts) == n                     # tras reinicio: no se repite
    s2 = Sorteos(str(tmp_path / "s.db"), d, "TOKEN")
    assert s2.resolver_vencidos(now=99999) == []


def test_sorteo_desierto(tmp_path):
    d = FakeDiscord([{"id": "1", "bot": True}])
    s = Sorteos(str(tmp_path / "s.db"), d, "TOKEN")
    s.crear("555", "Gorra", minutos=1, now=0)
    r = s.resolver_vencidos(now=61)
    assert r[0]["ganadores"] == [] and "desierto" in d.posts[-1][1]["content"]
