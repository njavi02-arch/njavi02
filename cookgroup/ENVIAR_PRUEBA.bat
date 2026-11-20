@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Envia UN mensaje marcado como PRUEBA al canal cuyo webhook este en .env (DISCORD_WEBHOOK_DEFAULT).
rem Usa un canal PRIVADO de pruebas. El webhook se escribe solo en .env, nunca en el chat ni en el repositorio.
if not exist .env (
  echo Falta el fichero .env. Copia .env.example a .env y pega en DISCORD_WEBHOOK_DEFAULT el webhook de tu canal privado de pruebas.
  pause
  exit /b 1
)
call .venv\Scripts\cookgroup test-webhook
pause
