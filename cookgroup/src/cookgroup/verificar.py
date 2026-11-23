"""v1.6 · lote 5: comprobaciones SEPARADAS para el PC del dueño (VERIFICAR.bat).

  tienda   → el PC puede leer una tienda real (BSTN y FOOTDISTRICT; solo lectura, no envía nada)
  discord  → el token del bot es válido, el bot está en el servidor DISCORD_GUILD_ID y existe #pruebas-bot
  alerta   → un único aviso marcado PRUEBA llega a #pruebas-bot y se relee por su ID (enlace directo para el móvil)

Cada paso imprime «PASO n · OK» o «PASO n · FALLA» con la causa y CÓMO corregirlo. El token nunca se imprime ni se
escribe en logs: solo se dice si existe y su longitud no se muestra.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field

import requests

API = "https://discord.com/api/v10"
GUILD_ESPERADO = "1572928642999255120"          # «Mi servidor privado» del dueño
TIENDAS = ("bstn-eu", "footdistrict")


@dataclass
class Paso:
    n: str
    titulo: str
    ok: bool
    detalle: str
    arreglo: str = ""
    datos: dict = field(default_factory=dict)

    def texto(self) -> str:
        cab = f"PASO {self.n} · {'OK   ' if self.ok else 'FALLA'} · {self.titulo}"
        out = [cab, f"         {self.detalle}"]
        if not self.ok and self.arreglo:
            out.append(f"         CÓMO ARREGLARLO: {self.arreglo}")
        return "\n".join(out)


# ------------------------------------------------------------------ 1 · tienda
def _causa_red(e: Exception) -> tuple[str, str]:
    s = f"{e} {e.__cause__ or ''} {e.__context__ or ''}"
    if "403" in s or "429" in s:
        return ("la tienda rechaza la petición (" + ("429" if "429" in s else "403") + ")",
                "la tienda limita o bloquea esta conexión: espera 10 minutos o prueba otra red; el bot lo reintenta solo")
    if isinstance(e, requests.exceptions.SSLError):
        return ("certificado HTTPS rechazado", "un antivirus o proxy está inspeccionando HTTPS: desactiva esa función para Python o prueba otra red")
    if isinstance(e, requests.exceptions.Timeout):
        return ("la tienda no respondió a tiempo", "comprueba tu conexión; si va bien, repite en 5 minutos")
    if "NameResolution" in s or "getaddrinfo" in s:
        return ("sin DNS / sin internet", "comprueba que el PC tiene internet (abre la web de la tienda en el navegador)")
    return ("no se pudo conectar", "comprueba internet, VPN o cortafuegos de Windows para python.exe")


def paso_tienda(monitors, make_source, clock=time.monotonic) -> list[Paso]:
    out = []
    por_nombre = {m.name: m for m in monitors}
    for i, name in enumerate(TIENDAS, 1):
        m = por_nombre.get(name)
        if m is None:
            out.append(Paso(f"1.{i}", f"leer {name}", False, "ese monitor no está en config/monitors.toml",
                            "descarga de nuevo el proyecto (rama claude/cookgroup-v1.0)"))
            continue
        t0 = clock()
        try:
            src = make_source(m)
            prods = src.fetch_launches(datetime.now(timezone.utc)) if hasattr(src, "fetch_launches") else src.fetch()   # BSTN: lanzamientos/raffles
        except requests.HTTPError as e:
            code = getattr(e.response, "status_code", "?")
            arreglo = ("la tienda limita peticiones: espera 10 minutos" if code == 429 else
                       "la tienda bloquea esta conexión (desafío anti-bot): prueba otra red; el bot lo reintentará solo")
            out.append(Paso(f"1.{i}", f"leer {m.store}", False, f"respuesta HTTP {code}", arreglo))
            continue
        except Exception as e:                                                   # noqa: BLE001
            causa, arreglo = _causa_red(e)
            out.append(Paso(f"1.{i}", f"leer {m.store}", False, f"{causa} ({type(e).__name__})", arreglo))
            continue
        ms = int((clock() - t0) * 1000)
        if not prods:
            out.append(Paso(f"1.{i}", f"leer {m.store}", False, f"respondió en {ms} ms pero sin productos",
                            "repite en unos minutos; si sigue vacío, avísame con el fichero logs\\verificar.txt"))
            continue
        ej = getattr(prods[0], "title", None) or getattr(prods[0], "name", "")
        out.append(Paso(f"1.{i}", f"leer {m.store}", True, f"{len(prods)} productos leídos en {ms} ms · ejemplo: {str(ej)[:60]}",
                        datos={"ms": ms, "n": len(prods)}))
    return out


# ------------------------------------------------------------------ 2 · discord
def paso_discord(env: dict, http=None) -> list[Paso]:
    http = http or requests.Session()
    tok, gid = (env.get("DISCORD_BOT_TOKEN") or "").strip(), (env.get("DISCORD_GUILD_ID") or "").strip()
    out = []
    if not tok:
        return [Paso("2.1", "token del bot en .env", False, "DISCORD_BOT_TOKEN está vacío",
                     "abre .env con el Bloc de notas y pega el token tras DISCORD_BOT_TOKEN= (portal de desarrolladores › tu app › Bot › Reset Token). No lo pegues en ningún chat")]
    h = {"Authorization": f"Bot {tok}"}
    try:
        r = http.get(f"{API}/users/@me", headers=h, timeout=15)
    except Exception as e:                                                       # noqa: BLE001
        causa, arreglo = _causa_red(e)
        return [Paso("2.1", "conectar con Discord", False, causa, arreglo)]
    if r.status_code == 401:
        return [Paso("2.1", "token del bot", False, "Discord rechaza el token (401)",
                     "el token está mal copiado o se regeneró: vuelve a copiarlo en el portal de desarrolladores y pégalo en .env")]
    if r.status_code != 200:
        return [Paso("2.1", "token del bot", False, f"respuesta {r.status_code} de Discord", "repite en unos minutos")]
    bot = r.json()
    out.append(Paso("2.1", "token del bot", True, f"token válido · bot «{bot.get('username')}» (id {bot.get('id')})"))
    if not gid:
        out.append(Paso("2.2", "servidor en .env", False, "DISCORD_GUILD_ID está vacío",
                        f"pon DISCORD_GUILD_ID={GUILD_ESPERADO} en .env (tu servidor privado)"))
        return out
    if gid != GUILD_ESPERADO:
        out.append(Paso("2.2", "servidor correcto", False, f"DISCORD_GUILD_ID={gid} no es tu servidor privado ({GUILD_ESPERADO})",
                        f"cámbialo a DISCORD_GUILD_ID={GUILD_ESPERADO} salvo que quieras usar otro servidor a propósito"))
        return out
    g = http.get(f"{API}/guilds/{gid}", headers=h, timeout=15)
    if g.status_code in (403, 404):
        out.append(Paso("2.2", "bot dentro del servidor", False, "el bot no está en tu servidor",
                        "invítalo: portal de desarrolladores › OAuth2 › URL Generator › «bot» + permisos Gestionar canales, "
                        "Gestionar roles, Gestionar webhooks, Enviar mensajes › abre la URL y elige tu servidor"))
        return out
    out.append(Paso("2.2", "bot dentro del servidor", True, f"servidor «{g.json().get('name')}» ({gid})"))
    ch = http.get(f"{API}/guilds/{gid}/channels", headers=h, timeout=15)
    canales = ch.json() if ch.status_code == 200 else []
    pr = next((c for c in canales if str(c.get("name", "")).lstrip("#") in ("pruebas-bot", "🧪pruebas-bot")), None)
    if pr is None:
        out.append(Paso("2.3", "canal #pruebas-bot", False, "no existe en el servidor",
                        "ejecuta INSTALAR_SERVIDOR.bat (crea #pruebas-bot privado y su webhook) y repite este paso"))
        return out
    cid = env.get("DISCORD_PRUEBAS_CHANNEL_ID", "").strip()
    if cid and cid != str(pr["id"]):
        out.append(Paso("2.3", "canal #pruebas-bot", False, f"DISCORD_PRUEBAS_CHANNEL_ID no coincide con #pruebas-bot ({pr['id']})",
                        f"pon DISCORD_PRUEBAS_CHANNEL_ID={pr['id']} en .env"))
        return out
    wh = bool((env.get("DISCORD_WEBHOOK_PRUEBAS") or "").strip())
    out.append(Paso("2.3", "canal #pruebas-bot", wh, f"existe (id {pr['id']})" + ("" if wh else " pero falta su webhook"),
                    "ejecuta INSTALAR_SERVIDOR.bat (escribe DISCORD_WEBHOOK_PRUEBAS en .env) y repite", {"channel_id": pr["id"]}))
    return out


# ------------------------------------------------------------------ 3 · alerta
def paso_alerta(send_first_real, store) -> list[Paso]:
    from .real_delivery import Refused
    try:
        row = send_first_real(store=store)
    except Refused as e:
        return [Paso("3.1", "aviso de PRUEBA en #pruebas-bot", False, f"no se ha enviado nada: {e}",
                     "corrige el paso 2 (VERIFICAR.bat discord) y repite")]
    except Exception as e:                                                       # noqa: BLE001
        causa, arreglo = _causa_red(e)
        return [Paso("3.1", "aviso de PRUEBA en #pruebas-bot", False, causa, arreglo)]
    link = f"https://discord.com/channels/{row['guild_id']}/{row['channel_id']}/{row['message_id']}"
    ok = row.get("estado") == "entrega real confirmada"
    return [Paso("3.1", "aviso de PRUEBA en #pruebas-bot", ok,
                 (f"entregado y releído por su ID · enlace para el móvil: {link}" if ok else
                  f"enviado pero NO confirmado al releerlo ({row.get('estado')}) · {link}"),
                 "abre el enlace; si no aparece, mira logs\\verificar.txt y repite una sola vez", {"link": link})]


def informe(pasos: list[Paso]) -> tuple[str, int]:
    txt = "\n".join(p.texto() for p in pasos)
    malos = [p for p in pasos if not p.ok]
    fin = ("RESULTADO: todo correcto." if not malos else f"RESULTADO: falla el PASO {malos[0].n}. Arregla ese paso y vuelve a ejecutar.")
    return txt + "\n\n" + fin, (0 if not malos else 1)


def main(que: str, cfg, db: str, env: dict | None = None) -> int:
    env = dict(os.environ) if env is None else env
    if que == "tienda":
        from .runner import make_source
        pasos = paso_tienda(cfg.monitors, make_source)
    elif que == "discord":
        pasos = paso_discord(env)
    elif que == "alerta":
        from .real_delivery import send_first_real
        from .store import Store
        pasos = paso_alerta(send_first_real, Store(db))
    else:
        print("Uso: cookgroup verificar tienda|discord|alerta")
        return 2
    txt, code = informe(pasos)
    print(txt)
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", "verificar.txt"), "a", encoding="utf-8") as f:   # sin token: solo los textos de arriba
        f.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} · {que}\n{txt}\n")
    return code
