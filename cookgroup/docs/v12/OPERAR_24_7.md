# Funcionamiento 24/7 con lo que ya tienes (sin contratar nada)

**Qué ya hace el bot**
- **Persistencia**: todo el estado está en `cookgroup.db` (SQLite). Al reiniciar no repite avisos (probado).
- **Recuperación**: si una tienda falla, espera cada vez más; si pide esperar (429/Retry-After), lo respeta; avisa en #registro-bot tras 3 fallos seguidos y cuando se recupera.
- **Salud**: latido cada 30 s; `ESTADO.bat` y `PANEL_TIENDAS.bat` muestran si el bot va, qué tienda falla y desde cuándo.

**Arranque automático en tu PC con Windows** (ejecútalo una vez, en una terminal abierta en la carpeta del cookgroup):

```
schtasks /Create /TN "Cookgroup" /TR "\"%CD%\ARRANCAR.bat\"" /SC ONLOGON /RL LIMITED /F
```

Así arranca solo al iniciar sesión en Windows. Para que no se pare:
1. En Inicio → Configuración → Sistema → Energía, pon «Suspender: nunca» cuando esté enchufado.
2. Deja el PC encendido.

Si cierras la sesión o apagas el PC, el bot se para y el panel lo marca en rojo («BOT PARADO»).

**Si prefieres no depender del PC**: un servidor pequeño en la nube. Es un gasto, así que lo decides tú; el bot es el mismo y solo cambia dónde se ejecuta.
