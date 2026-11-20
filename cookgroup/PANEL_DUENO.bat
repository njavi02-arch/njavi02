@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Abre la web local: pagina de venta + panel del dueno (PIN en .env: PANEL_PIN). Cierra esta ventana para pararla.
if "%PANEL_PIN%"=="" for /f "tokens=2 delims==" %%a in ('findstr /b "PANEL_PIN=" .env 2^>nul') do set PANEL_PIN=%%a
start "" "http://127.0.0.1:8765/"
if not "%PANEL_PIN%"=="" start "" "http://127.0.0.1:8765/admin?pin=%PANEL_PIN%"
call .venv\Scripts\cookgroup web
pause
