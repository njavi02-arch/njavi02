@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === 1/3 Comprobando las tiendas y feeds (no envia nada) ===
call .venv\Scripts\cookgroup probe
echo.
echo === 2/3 Enviando un mensaje de PRUEBA a tu canal de Discord ===
call .venv\Scripts\cookgroup test-webhook
echo.
echo === 3/3 Generando vista previa de todas las alertas ===
call .venv\Scripts\cookgroup preview --out preview.html
start "" preview.html
echo Si todo esta OK, ejecuta INSTALAR_AUTOARRANQUE.bat (24/7) o ARRANCAR.bat (ventana visible)
pause
