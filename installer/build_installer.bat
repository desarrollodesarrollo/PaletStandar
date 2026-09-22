@echo off
REM Construye el instalador de Windows de Calculadora de Sumas.
REM Ejecutar en Windows, dentro de la carpeta "installer" del repositorio.
REM
REM Requisitos previos (una sola vez):
REM   1. Python 3 instalado (con tkinter, que ya viene incluido en la
REM      instalacion oficial de python.org) y disponible como "python" en el PATH.
REM   2. NSIS instalado (https://nsis.sourceforge.io/Download), con
REM      makensis.exe accesible desde el PATH o en su carpeta habitual
REM      "C:\Program Files (x86)\NSIS".

setlocal

cd /d "%~dp0"

echo === 1/3: Instalando PyInstaller si hace falta ===
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    python -m pip install pyinstaller
    if errorlevel 1 goto :error
)

echo === 2/3: Compilando calculadora_gui.py a un .exe de Windows ===
python -m PyInstaller --onefile --windowed --distpath dist_windows --name calculadora_gui ..\calculadora_gui.py
if errorlevel 1 goto :error

echo === 3/3: Generando el instalador con NSIS ===
where makensis >nul 2>&1
if errorlevel 1 (
    set "MAKENSIS=C:\Program Files (x86)\NSIS\makensis.exe"
) else (
    set "MAKENSIS=makensis"
)

"%MAKENSIS%" calculadora_installer.nsi
if errorlevel 1 goto :error

echo.
echo Listo: installer\CalculadoraSumasSetup.exe
goto :eof

:error
echo.
echo Ha fallado la construccion del instalador. Revisa los mensajes anteriores.
exit /b 1
