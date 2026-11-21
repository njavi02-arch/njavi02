@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Simula la apertura de un raffle de BSTN y publica UN mensaje marcado PRUEBA SOLO en #pruebas-bot.
rem Muestra el enlace directo al mensaje y el tiempo medido. Despues simula un reinicio: no debe repetirse.
rem Sin .env todavia: PRUEBA_RAFFLE.bat --simulado (lo mismo contra un Discord falso, en local).
if not exist .env if "%1"=="" (
  echo Falta el fichero .env. Ejecuta INSTALAR_SERVIDOR.bat o prueba en local con: PRUEBA_RAFFLE.bat --simulado
  pause
  exit /b 1
)
call .venv\Scripts\cookgroup prueba-raffle %1
call .venv\Scripts\cookgroup panel-tiendas >nul
start "" "docs\v11\PANEL_TIENDAS.html"
pause
