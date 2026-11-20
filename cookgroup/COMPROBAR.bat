@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Solo LEE las fuentes. No envia nada a Discord.
rem   COMPROBAR.bat               todas las fuentes activas (lote completo)
rem   COMPROBAR.bat piloto        solo las 6 fuentes del piloto (config\piloto.toml)
rem   COMPROBAR.bat buscar bstn   solo las que contengan "bstn"
rem   COMPROBAR.bat reanudar      sigue el ultimo lote donde se corto
set CFG=config\monitors.toml
set EXTRA=
if /I "%1"=="piloto"   set CFG=config\piloto.toml
if /I "%1"=="buscar"   set EXTRA=--buscar %2
if /I "%1"=="reanudar" set EXTRA=--reanudar
echo === Comprobando fuentes (solo lectura) con %CFG% %EXTRA% ===
call .venv\Scripts\cookgroup --config %CFG% probe %EXTRA%
echo.
echo El informe CSV (se abre con Excel) esta en la carpeta logs\  (comprobacion_FECHA.csv)
pause
