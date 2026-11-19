@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Arranque automatico del cookgroup al iniciar sesion en Windows ===
schtasks /Create /TN "Cookgroup" /TR "wscript.exe \"%~dp0ARRANCAR_OCULTO.vbs\"" /SC ONLOGON /RL LIMITED /F
if errorlevel 1 (echo No se pudo crear la tarea. Prueba con clic derecho ^> Ejecutar como administrador. & pause & exit /b 1)
schtasks /Run /TN "Cookgroup" >nul
echo.
echo Listo: el bot se ha arrancado en segundo plano y volvera a arrancar cada vez que inicies sesion.
echo Para ver si funciona: ESTADO.bat   ·   Para quitarlo: QUITAR_AUTOARRANQUE.bat
echo IMPORTANTE: si el PC entra en suspension el bot se para. Configuracion ^> Sistema ^> Energia ^> Suspension: Nunca (enchufado).
pause
