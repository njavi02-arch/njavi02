@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Comprobaciones SEPARADAS en tu PC. Cada paso dice OK o FALLA + como arreglarlo. El token nunca se muestra.
rem   VERIFICAR.bat              pasos 0, 1 y 2 (no envia nada a Discord) y pregunta antes del 3
rem   VERIFICAR.bat tienda       solo el paso 1: tu PC lee una tienda real (BSTN y FOOTDISTRICT)
rem   VERIFICAR.bat discord      solo el paso 2: el bot entra en tu servidor y existe #pruebas-bot
rem   VERIFICAR.bat alerta       solo el paso 3: UN aviso de PRUEBA a #pruebas-bot + enlace para el movil
rem   VERIFICAR.bat arranque     solo el paso 4: autoarranque instalado y bot funcionando
rem Todo queda anotado (sin token) en logs\verificar.txt

echo ================ PASO 0 - requisitos ================
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
%PY% -c "import sys; sys.exit(0 if sys.version_info>=(3,11) else 1)" 2>nul
if errorlevel 1 (
  echo PASO 0 - FALLA - Python 3.11 o superior no encontrado.
  echo          COMO ARREGLARLO: instala Python desde https://www.python.org/downloads/ marcando "Add python.exe to PATH" y ejecuta INSTALAR.bat
  goto fin_mal
)
if not exist .venv\Scripts\cookgroup.exe (
  echo PASO 0 - FALLA - el bot no esta instalado en esta carpeta.
  echo          COMO ARREGLARLO: doble clic en INSTALAR.bat y vuelve a ejecutar VERIFICAR.bat
  goto fin_mal
)
if not exist .env (
  echo PASO 0 - FALLA - falta el fichero .env
  echo          COMO ARREGLARLO: ejecuta INSTALAR.bat ^(lo crea a partir de .env.example^)
  goto fin_mal
)
echo PASO 0 - OK    - Python, bot instalado y .env presentes
echo.

if /I "%1"=="tienda"   goto tienda
if /I "%1"=="discord"  goto discord
if /I "%1"=="alerta"   goto alerta
if /I "%1"=="arranque" goto arranque

:tienda
echo ================ PASO 1 - tu PC lee una tienda real (solo lectura) ================
call .venv\Scripts\cookgroup verificar tienda
if errorlevel 1 goto fin_mal
if /I "%1"=="tienda" goto fin_ok
echo.

:discord
echo ================ PASO 2 - acceso del bot a tu Discord ================
call .venv\Scripts\cookgroup verificar discord
if errorlevel 1 goto fin_mal
if /I "%1"=="discord" goto fin_ok
echo.
set /p OK=Escribe SI para enviar UN aviso de PRUEBA a #pruebas-bot (paso 3):
if /I not "%OK%"=="SI" (echo Paso 3 no ejecutado. & goto fin_ok)

:alerta
:alerta_directa
echo ================ PASO 3 - aviso de PRUEBA en #pruebas-bot ================
call .venv\Scripts\cookgroup verificar alerta
if errorlevel 1 goto fin_mal
echo Abre el enlace de arriba en el movil (app de Discord) para ver el aviso.
if /I "%1"=="alerta" goto fin_ok
echo.

:arranque
echo ================ PASO 4 - autoarranque y bot en marcha ================
schtasks /Query /TN "Cookgroup" >nul 2>nul
if errorlevel 1 (
  echo PASO 4.1 - FALLA - el autoarranque no esta instalado
  echo          COMO ARREGLARLO: doble clic en INSTALAR_AUTOARRANQUE.bat
) else (
  echo PASO 4.1 - OK    - tarea "Cookgroup" instalada: arranca al iniciar sesion
)
call .venv\Scripts\cookgroup status
echo PASO 4.2 - mira arriba: cada tienda con su ultima lectura correcta. "BOT PARADO" = el bot no esta corriendo ^(ARRANCAR.bat^).
goto fin_ok

:fin_mal
echo.
echo Hay un paso que falla: arreglalo con la indicacion de arriba y vuelve a ejecutar VERIFICAR.bat
pause
exit /b 1
:fin_ok
echo.
pause
exit /b 0
