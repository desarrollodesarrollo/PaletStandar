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
