@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Cookgroup en marcha (cierra esta ventana o pulsa Ctrl+C para pararlo) ===
echo La primera vuelta de cada tienda solo guarda el catalogo (no avisa de todo como "nuevo").
call .venv\Scripts\cookgroup run
pause
