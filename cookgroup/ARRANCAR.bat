@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Cookgroup en marcha (cierra esta ventana o pulsa Ctrl+C para pararlo) ===
echo Logs: %~dp0logs\cookgroup.log     Diagnostico: ESTADO.bat
if not exist logs mkdir logs
echo La primera vuelta de cada tienda solo guarda el catalogo y envia un resumen.
:bucle
call .venv\Scripts\cookgroup run
echo [%date% %time%] El proceso se ha detenido; se reinicia en 30 segundos... >> logs\reinicios.log
timeout /t 30 /nobreak >nul
goto bucle
