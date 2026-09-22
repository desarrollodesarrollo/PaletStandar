# PaletStandar

## Calculadora de sumas (interfaz gráfica)

`calculadora_gui.py` es una pequeña aplicación de escritorio (tkinter) que suma dos números introducidos por el usuario.

### Ejecutar desde el código fuente

Requiere Python 3 con `tkinter` instalado (incluido por defecto en la mayoría de instalaciones de Python; en Debian/Ubuntu puede requerir `sudo apt install python3-tk`).

```bash
python3 calculadora_gui.py
```

### Generar el ejecutable independiente

```bash
./build_exe.sh
```

El script instala `pyinstaller` si hace falta y genera el binario en `dist/`. Una vez construido, se lanza directamente sin necesidad de tener Python instalado:

```bash
./dist/calculadora_gui
```

El ejecutable solo sirve para la plataforma en la que se construye (no es multiplataforma).

### Instalador para Windows

`installer/` contiene un instalador estilo Windows clásico (asistente con pantalla de bienvenida, selección de carpeta, barra de progreso, accesos directos en el Menú Inicio/Escritorio y desinstalador desde "Agregar o quitar programas").

Se genera **en un equipo Windows** (PyInstaller no compila de forma cruzada, así que el `.exe` de la app debe construirse en el propio Windows). Pasos, una sola vez:

1. Instala Python 3 desde [python.org](https://www.python.org/) (incluye `tkinter`).
2. Instala [NSIS](https://nsis.sourceforge.io/Download).

Luego, desde una consola (`cmd`) dentro de la carpeta `installer`:

```bat
build_installer.bat
```

Esto compila `calculadora_gui.py` a `installer\dist_windows\calculadora_gui.exe` con PyInstaller y genera `installer\CalculadoraSumasSetup.exe` con NSIS. Ese único archivo es el instalador: al ejecutarlo, el usuario final no necesita lanzar nada más ni tener Python instalado.
