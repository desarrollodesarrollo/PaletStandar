#!/usr/bin/env bash
# Construye un ejecutable independiente de calculadora_gui.py con PyInstaller.
# Uso: ./build_exe.sh
set -euo pipefail

cd "$(dirname "$0")"

if ! python3 -m PyInstaller --version >/dev/null 2>&1; then
    echo "PyInstaller no encontrado, instalando..."
    python3 -m pip install --user pyinstaller \
        || python3 -m pip install --user --break-system-packages pyinstaller
fi

python3 -m PyInstaller --onefile --windowed calculadora_gui.py

echo "Ejecutable generado en dist/"
