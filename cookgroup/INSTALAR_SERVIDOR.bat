@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Crea en TU servidor los roles, categorias, canales, permisos y webhooks de config\servidor.toml.
rem Se puede repetir: no duplica nada, no borra nada y no toca tus canales actuales.
rem Necesita en .env:  DISCORD_BOT_TOKEN=...  y  DISCORD_GUILD_ID=...
echo === Vista previa (no cambia nada) ===
call .venv\Scripts\cookgroup servidor
echo.
set /p OK=Escribe SI para crear lo que falta en Discord: 
if /I not "%OK%"=="SI" goto fin
call .venv\Scripts\cookgroup servidor --aplicar
:fin
pause
