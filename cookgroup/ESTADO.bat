@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Estado por fuente (ultimo ciclo correcto, errores seguidos, ultimo error) ===
call .venv\Scripts\cookgroup status
echo.
echo === Ultimas 15 lineas del log ===
powershell -NoProfile -Command "if (Test-Path logs\cookgroup.log) { Get-Content logs\cookgroup.log -Tail 15 } else { 'Aun no hay log: arranca el bot.' }"
pause
