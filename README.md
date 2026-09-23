# PRUEBAESTANDAR

Programa de escritorio que rellena las columnas **ELECCIÓN** del *fichero base* con el nº de cajas de cada artículo que irá en el medio (palet o carros) de cada tienda, respetando peso, volumen y densidad del medio y dando prioridad a los artículos con más líneas de pedido.

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

El resultado se guarda como **`PRUEBAESTANDAR.xlsx`** en la misma carpeta que el fichero base. El fichero base original no se modifica. Si `PRUEBAESTANDAR.xlsx` ya existe, el programa pide confirmación antes de sobrescribirlo, y si está abierto en Excel ofrece *Reintentar* después de cerrarlo.

Al terminar, la ventana muestra un resumen con las tiendas procesadas, las tiendas sin selección, el total de cajas y los avisos.

## Formato de los ficheros

### Fichero base (primera hoja)

| Fila | A | B | C | D | E, F, G (se repite cada 3 columnas por tienda) |
|---|---|---|---|---|---|
| 1 | | | | | código de tienda en las 3 columnas |
| 2 | CODIGO | PESO (Kg) | Volumen (L) | Densidad (kg/l) | `BULTOS`, `LINEAS`, `ELECCIÓN` |
| 3… | artículo | kg por caja | L por caja | kg/L | bultos y líneas del periodo; ELECCIÓN la rellena el programa |

- Admite cualquier nº de artículos y de tiendas.
- BULTOS o LINEAS vacíos cuentan como 0.
- Un artículo sin peso o volumen válido (vacío o ≤ 0) no se selecciona y aparece en los avisos.

### Tabla de tiendas y medios (primera hoja)

Encabezados en la fila 1 y, a partir de la fila 2: `TIENDA`, `TIPO DE MEDIO` (`PALET` o `CARRO`), `PESO MAX (Kg)`, `VOLUMEN MÁX (L)`, `DENSIDAD` (kg/L). Puede tener más tiendas que el fichero base, pero **todas** las tiendas del fichero base deben estar en la tabla.

Si algo no cuadra (encabezados, tiendas repetidas o que faltan, valores no numéricos…), el programa no genera salida y muestra qué fila o columna revisar.

## Reglas de selección (por tienda)

1. **Artículos elegibles:** solo los que tienen BULTOS > 0 en esa tienda y peso y volumen válidos.
2. **Máximo de cajas por artículo:** ⌈BULTOS / nº de días⌉ (redondeo hacia arriba).
3. **Capacidad:** PALET = 1 medio; CARRO = 2 medios (2 × peso y 2 × volumen).
4. **Restricciones, siempre:** peso total ≤ peso máximo, volumen total ≤ volumen máximo y densidad de la selección (kg/L) **estrictamente menor** que la del medio.
5. **Reparto proporcional a las líneas:** las cajas se asignan de una en una. Cada caja siguiente va al artículo con mayor índice `LÍNEAS / (cajas ya asignadas + 1)` cuya caja todavía cabe (como el reparto de escaños D'Hondt). En caso de empate gana, por este orden: el artículo que aún no tiene cajas, el de más líneas, el de menor volumen y el de menor código.
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
- `escritura.py`: escritura de la salida.
- `proceso.py`: orquestación.
- `gui.py`: ventana.

La especificación completa está en `openspec/changes/pruebaestandar/`.
