@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Cookgroup: instalacion ===
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% -c "import sys; sys.exit(0 if sys.version_info>=(3,11) else 1)" 2>nul
if errorlevel 1 (
  echo Necesitas Python 3.11 o superior: https://www.python.org/downloads/  ^(marca "Add python.exe to PATH"^)
  pause & exit /b 1
)
if not exist .venv %PY% -m venv .venv
call .venv\Scripts\python -m pip install --upgrade pip >nul
call .venv\Scripts\pip install -e . || (echo Error instalando dependencias & pause & exit /b 1)
if not exist .env copy .env.example .env >nul
echo.
echo Listo. Ahora se abre el fichero .env con el Bloc de notas.
echo Rellena estas dos lineas y guarda (Ctrl+G o Archivo ^> Guardar):
echo    DISCORD_BOT_TOKEN=  el token de tu bot ^(no lo pegues en ningun chat^)
echo    DISCORD_GUILD_ID=1572928642999255120
notepad .env
echo Despues ejecuta VERIFICAR.bat
pause
