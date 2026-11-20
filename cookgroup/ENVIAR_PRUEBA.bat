@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Envia UN mensaje marcado como PRUEBA SOLO a #pruebas-bot (DISCORD_WEBHOOK_PRUEBAS). Nunca usa el webhook general.
rem Antes de enviar comprueba servidor y canal; despues relee el mensaje por su ID.
rem Usa un canal PRIVADO de pruebas. El webhook se escribe solo en .env, nunca en el chat ni en el repositorio.
if not exist .env (
  echo Falta el fichero .env. Ejecuta antes INSTALAR_SERVIDOR.bat (crea #pruebas-bot y su webhook) o pega DISCORD_WEBHOOK_PRUEBAS.
  pause
  exit /b 1
)
call .venv\Scripts\cookgroup test-webhook
pause
