# PRUEBAESTANDAR

Programa de escritorio que rellena las columnas **ELECCIÓN** del *fichero base* con el nº de cajas de cada artículo que irá en el medio (palet o carros) de cada tienda. Respeta un llenado máximo del 96 % del peso y el volumen del medio y su densidad, y da prioridad a los artículos con más líneas de pedido. Además genera **REPARTOESTANDAR.xls**, con esa elección en unidades, para importarla en otro programa.

La forma más cómoda de usarlo en Windows es el ejecutable `PRUEBAESTANDAR.exe`, que no necesita Python. Se descarga como zip desde la pestaña **Actions** del repositorio, en la ejecución «Compilar PRUEBAESTANDAR.exe» (apartado *Artifacts*).

## Requisitos

- Windows, macOS o Linux con **Python 3.10 o superior** ([python.org](https://www.python.org/downloads/)). En Windows, marca *"Add Python to PATH"* al instalar; `tkinter` ya viene incluido.
- Dependencias del programa:

  ```
  pip install -r requirements.txt
  ```

## Uso

1. Haz doble clic en `PRUEBAESTANDAR.pyw` (o ejecuta `python -m pruebaestandar`).
2. Pulsa **Seleccionar…** y elige el **FICHERO BASE** (`.xlsx`).
3. Pulsa **Seleccionar…** y elige la **TABLA DE TIENDAS Y MEDIOS** (`.xlsx`).
4. Escribe el **nº de días de datos** del fichero base (entero mayor que 0).
5. Pulsa **Ejecutar**.

En la misma carpeta que el fichero base se guardan dos ficheros:
- **`PRUEBAESTANDAR.xlsx`**: copia del fichero base con las columnas ELECCIÓN rellenas, en cajas.
- **`REPARTOESTANDAR.xls`**: la misma elección en **unidades** (cajas × UNIxCAJA), en formato Excel 97-2003 y con el formato de la plantilla del programa de importación.

El fichero base original no se modifica. Si alguno de los dos ficheros ya existe, el programa pide una sola confirmación antes de sobrescribirlos. Si alguno está abierto en Excel, ofrece *Reintentar* después de cerrarlo.

Al terminar, la ventana muestra las dos rutas y un resumen con las tiendas procesadas, las tiendas sin selección, el total de cajas, el total de unidades y los avisos.

## Formato de los ficheros

### Fichero base (primera hoja)

| Fila | A | B | C | D | E, F, G (se repite cada 3 columnas por tienda) |
|---|---|---|---|---|---|
| 1 | | | | | código de tienda en las 3 columnas |
| 2 | CODIGO | PESO (Kg) | Volumen (L) | UNIxCAJA | `BULTOS`, `LINEAS`, `ELECCIÓN` |
| 3… | artículo | kg por caja | L por caja | unidades por caja | bultos (cajas) y líneas del periodo; ELECCIÓN la rellena el programa |

- Admite cualquier nº de artículos. En tiendas admite hasta 255, que es el límite de columnas del formato `.xls` de REPARTOESTANDAR.
- BULTOS o LINEAS vacíos cuentan como 0.
- **UNIxCAJA** es obligatorio en todos los artículos y debe ser un entero ≥ 1. Un fichero base antiguo, con la densidad en la columna D, se rechaza con un aviso.
- Un artículo sin peso o volumen válido (vacío o ≤ 0) no se selecciona y aparece en los avisos.
- Los códigos de tienda pueden ser cualquier número (por ejemplo 82 en lugar de 10082), pero **deben coincidir** con los de la tabla de tiendas y medios.

### Tabla de tiendas y medios (primera hoja)

Encabezados en la fila 1 y, a partir de la fila 2: `TIENDA`, `TIPO DE MEDIO` (`PALET` o `CARRO`), `PESO MAX (Kg)`, `VOLUMEN MÁX (L)`, `DENSIDAD` (kg/L). Puede tener más tiendas que el fichero base, pero **todas** las tiendas del fichero base deben estar en la tabla.

Si algo no cuadra (encabezados, tiendas repetidas o que faltan, valores no numéricos…), el programa no genera ningún fichero y muestra qué fila o columna revisar.

### REPARTOESTANDAR.xls (salida)

- Hoja `Hoja1`; las hojas `Hoja2` y `Hoja3` van vacías.
- En A1, el texto `Código`.
- En la fila 1, desde B, los códigos de tienda como números, en el orden del fichero base.
- Desde la fila 2, un artículo por fila (código como número) y, en cada tienda, las unidades elegidas (cajas × UNIxCAJA). La celda queda vacía si la tienda no lleva ese artículo.
- Fuentes, bordes, relleno, anchos y altos son como los de la plantilla del programa de importación.

## Reglas de selección (por tienda)

1. **Artículos elegibles:** solo los que tienen BULTOS > 0 en esa tienda y peso y volumen válidos.
2. **Máximo de cajas por artículo:** ⌈BULTOS / nº de días⌉ (redondeo hacia arriba).
3. **Capacidad con margen de seguridad:** PALET = 1 medio; CARRO = 2 medios. Se usa como máximo el **96 %** del peso y del volumen: un palet de 875 kg / 1300 L admite 840 kg / 1248 L, y dos carros de 475 kg / 600 L admiten 912 kg / 1152 L.
4. **Restricciones, siempre:** peso total ≤ 96 % del peso máximo, volumen total ≤ 96 % del volumen máximo y densidad de la selección (kg/L) **estrictamente menor** que la del medio.
5. **Reparto proporcional a las líneas:** las cajas se asignan de una en una. Cada caja siguiente va al artículo con mayor índice `LÍNEAS / (cajas ya asignadas + 1)` cuya caja todavía cabe (como el reparto de escaños D'Hondt). En caso de empate gana, por este orden: el artículo que aún no tiene cajas, el de más líneas, el de **más bultos de salida en la tienda** (lo que decide, sobre todo, entre los artículos de 1 o 2 líneas), el de menor volumen y el de menor código.
   - Por eso, los artículos con más líneas entran antes y llevan más cajas, y los de pocas líneas llevan menos o ninguna.
   - Si una caja no cabe, se prueba la del siguiente artículo, para aprovechar el hueco con más variedad.
   - Un artículo muy denso puede entrar más tarde, cuando las cajas ligeras ya elegidas bajan la densidad del conjunto.
6. Solo cajas enteras. Antes de guardar, el programa comprueba de nuevo todas las reglas en cada tienda y no guarda nada si alguna falla.

## Desarrollo

```
pip install -r requirements-dev.txt
python -m pytest          # todas las pruebas
python -m pytest -m "not lento"   # sin la prueba de rendimiento (650 artículos × 180 tiendas)
```

Las pruebas de la ventana necesitan pantalla; en Linux sin escritorio se pueden lanzar con `xvfb-run python -m pytest`.

Código en `pruebaestandar/`:
- `lectura.py`: lectura y validación de los ficheros.
- `seleccion.py`: algoritmo de selección.
- `verificacion.py`: comprobación final.
- `escritura.py`: escritura de PRUEBAESTANDAR.xlsx.
- `reparto.py`: REPARTOESTANDAR.xls.
- `proceso.py`: orquestación.
- `gui.py`: ventana.

La especificación vigente está en `openspec/specs/`.
