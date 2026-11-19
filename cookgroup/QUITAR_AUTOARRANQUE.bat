@echo off
chcp 65001 >nul
schtasks /End /TN "Cookgroup" >nul 2>nul
schtasks /Delete /TN "Cookgroup" /F
taskkill /FI "WINDOWTITLE eq Cookgroup*" >nul 2>nul
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'cookgroup' -and $_.CommandLine -match 'run|ARRANCAR' } | Invoke-CimMethod -MethodName Terminate | Out-Null"
echo Arranque automatico eliminado y bot detenido.
pause
