@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Panel de tiendas: con el bot en marcha (ARRANCAR.bat) se regenera cada 30 s y la pagina se recarga sola.
rem Si el bot esta parado, se genera ahora con lo ultimo que se sabe y lo avisa arriba en rojo.
if exist .venv\Scripts\cookgroup.exe call .venv\Scripts\cookgroup panel-tiendas >nul
start "" "docs\v11\PANEL_TIENDAS.html"
