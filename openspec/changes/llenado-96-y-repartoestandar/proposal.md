# Proposal

## Why

Tras usar PRUEBAESTANDAR con datos reales, hacen falta dos ajustes para que encaje en la operativa:
- los medios salen llenos casi al 100 % del volumen y se necesita un **margen de seguridad**;
- el resultado tiene que poder **importarse en otro programa en unidades**, no en cajas, con el formato `.xls` de la plantilla que ese programa ya acepta.

## What Changes

- **Llenado máximo del 96 %:** la selección de cada tienda no puede superar el 96 % del volumen máximo ni el 96 % del peso máximo de sus medios (1 palet o 2 carros). El límite es fijo y estricto. La densidad sigue exigiéndose igual, contra la densidad del medio.
  - Con los datos de ejemplo (5 días), el volumen usado baja de una mediana del 99,9 % al 95,9 %, con máximo 96,0 %. Salen 19.236 cajas en lugar de 19.814 (−2,9 %).
- **Columna D del fichero base = `UNIxCAJA`** (unidades por caja, entero ≥ 1), en lugar de la densidad del artículo. La densidad del artículo no hace falta: el programa nunca la leyó, porque calcula peso ÷ volumen. **BREAKING:** un fichero base con la densidad en la columna D se rechaza, para no multiplicar por un dato equivocado.
- **Nuevo fichero de salida `REPARTOESTANDAR.xls`** (Excel 97-2003, BIFF8), en la carpeta del fichero base y junto a `PRUEBAESTANDAR.xlsx`, que se sigue generando:
  - Hoja `Hoja1`: en A1 el texto `Código`, igual que la plantilla. En la fila 1, desde B, los códigos de tienda como números, en el orden del fichero base. Desde la fila 2, un artículo por fila con su código como número.
  - Cada celda contiene ELECCIÓN × UNIxCAJA en unidades. Si la tienda no lleva ese artículo, la celda queda vacía.
  - Estilos (fuentes, bordes, relleno, anchos, altos) y hojas `Hoja2` y `Hoja3` vacías, como en la `PLANTILLA.xls` aportada.
- **Ventana y resumen:** muestran las dos rutas generadas. La confirmación de sobrescritura cubre los dos ficheros. El resumen incluye el total de unidades.
- **Códigos de tienda sin el 10000** (p. ej. 82 en vez de 10082): el programa no necesita cambios, solo que el fichero base y la tabla de tiendas usen los mismos códigos. Con ficheros mezclados, el error ya existente lista las tiendas que faltan.

## Capabilities

### New Capabilities
<!-- Ninguna: el nuevo fichero se incorpora a la capacidad existente de ficheros. -->

### Modified Capabilities
- `seleccion-bultos`: la capacidad útil del medio pasa a ser el 96 % del peso y volumen máximos.
- `ficheros-excel`: la columna D del fichero base pasa a ser `UNIxCAJA`, con validación, y se añade el fichero `REPARTOESTANDAR.xls`. La comprobación final incluye el límite del 96 % y la coherencia de las unidades.
- `interfaz-grafica`: la confirmación de sobrescritura y el resultado cubren los dos ficheros de salida, y el resumen muestra las unidades.

## Impact

- Código: `lectura.py` (UNIxCAJA), `modelo.py`/`seleccion.py`/`verificacion.py` (capacidad al 96 %), nuevo `reparto.py` (escritura `.xls`), `escritura.py`/`proceso.py`/`gui.py` (dos salidas), pruebas y README.
- Nueva dependencia: `xlwt` (escritura `.xls` BIFF8) y, sólo para pruebas, `xlrd` (lectura `.xls`). También se incluyen en la compilación del `.exe`.
- Ficheros de entrada: hay que usar el nuevo fichero base (con UNIxCAJA) y la tabla de tiendas con los códigos nuevos.
