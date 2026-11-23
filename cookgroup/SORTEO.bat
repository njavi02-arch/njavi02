@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Crea un sorteo interno en el canal de DISCORD_SORTEOS_CHANNEL_ID (.env). El bot (ARRANCAR.bat) elige ganador al cerrar.
set /p PREMIO=Que se sortea?: 
set /p MIN=Duracion en minutos (Enter = 1440, un dia): 
if "%MIN%"=="" set MIN=1440
set /p GAN=Numero de ganadores (Enter = 1): 
if "%GAN%"=="" set GAN=1
call .venv\Scripts\cookgroup sorteo --premio "%PREMIO%" --minutos %MIN% --ganadores %GAN%
pause
