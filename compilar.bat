@echo off
REM ==========================================================
REM  Crea el ejecutable dist\Agenda.exe con PyInstaller
REM  Uso: doble clic en este archivo (o ejecutarlo desde la consola)
REM ==========================================================
cd /d "%~dp0"

echo [1/3] Instalando dependencias...
python -m pip install --upgrade pillow pyinstaller || goto error

echo [2/3] Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Agenda.spec del Agenda.spec

echo [3/3] Compilando...
python -m PyInstaller --noconfirm --onefile --windowed ^
  --name "Agenda" ^
  --icon "imagenes\ICON.ico" ^
  --add-data "imagenes;imagenes" ^
  --exclude-module plotly ^
  --exclude-module pandas ^
  --exclude-module numpy ^
  main.py || goto error

echo.
echo ==========================================================
echo  Listo: dist\Agenda.exe
echo  La agenda se guardara en dist\libreta\agenda.json
echo ==========================================================
pause
exit /b 0

:error
echo.
echo  Ha ocurrido un error durante la compilacion.
pause
exit /b 1
