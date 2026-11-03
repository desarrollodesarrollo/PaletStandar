# PRUEBAESTANDAR

Programa de escritorio que, en una sola ejecución:
1. Genera el **SALALM FILTRADO** y el **FICHERO BASE** (como GENERABASE) a partir del SALALM, el MAESTRO, el MAESTRO DE CADUCIDAD y el Access de MOVIMIENTOS.
2. Calcula el **palet estándar** del TIPO elegido (ALTA ROTACIÓN, DROGUERÍA, ALIMENTACIÓN o TODOS). Para cada tienda decide el nº de cajas de cada artículo que irá en su medio (palet o carros). Respeta un llenado máximo del 96 % del peso y el volumen del medio y su densidad, y da prioridad a los artículos con más líneas de pedido.
3. Guarda **PRUEBAESTANDAR** (la elección en cajas) y **REPARTOESTANDAR** (la elección en unidades, para importarla en otro programa).

La forma más cómoda de usarlo en Windows es el ejecutable `PRUEBAESTANDAR.exe`, que no necesita Python. Se descarga como zip desde la pestaña **Actions** del repositorio, en la ejecución «Compilar PRUEBAESTANDAR.exe» (apartado *Artifacts*).

## Requisitos

- Windows, macOS o Linux con **Python 3.10 o superior** ([python.org](https://www.python.org/downloads/)). En Windows, marca *"Add Python to PATH"* al instalar; `tkinter` ya viene incluido.
- Dependencias del programa (incluyen el lector de Access, que no necesita Access ni controladores instalados):

  ```
  pip install -r requirements.txt
  ```

## Uso

1. Haz doble clic en `PRUEBAESTANDAR.pyw` (o ejecuta `python -m pruebaestandar`).
2. Con los botones **Seleccionar…**, elige:
   - el **SALALM**, el **MAESTRO** y el **MAESTRO DE CADUCIDAD** (`.xlsx`). Bajo los dos maestros, la ventana recuerda: «Filtrar para un solo almacén».
   - el Access de **MOVIMIENTOS** (`.accdb` o `.mdb`),
   - la **TABLA DE TIENDAS Y MEDIOS** (`.xlsx`).
3. Escribe el **nº de artículos** del FICHERO BASE (entero mayor que 0).
4. Elige el **TIPO** de palet estándar: ALTA ROTACIÓN, DROGUERÍA, ALIMENTACIÓN o **TODOS**. Con TODOS no se filtra por tipo: el palet se calcula con todos los artículos del FICHERO BASE (si pones 1000, con esos 1000).
5. Pulsa **Ejecutar**. Leer el Access es lo que más tarda (unos minutos con el Access real; mejor si está copiado en el propio PC que en una carpeta de red). La ventana muestra en qué fase está.

**El nº de días de datos ya no se escribe:** el programa lo calcula como el nº de valores distintos de `MVFECI` en las filas del Access con `MVTMOV = "PI"` (de cualquier tienda). Ese número es el que se usa en el máximo de cajas por artículo.

**Orden de la selección:** primero se toman los N artículos con más CAJAS del SALALM FILTRADO, de cualquier tipo (así se forma el FICHERO BASE). Después, de esos N, el palet se calcula sólo con los del TIPO elegido (con TODOS, con los N). Por eso, con un TIPO concreto, puede haber menos artículos que N; el resumen dice cuántos hay. Si no hay ninguno, el programa lo avisa y no genera nada.

### Ficheros generados

En la carpeta del SALALM se guardan 4 ficheros. Llevan la **fecha de ejecución** (`AAAAMMDD`) y, los dos del palet, el **TIPO abreviado**: `AR` = ALTA ROTACIÓN, `DR` = DROGUERÍA, `AL` = ALIMENTACIÓN y `TD` = TODOS. Por ejemplo, el 03/11/2026 con ALTA ROTACIÓN:

| Fichero | Contenido |
|---|---|
| `SALALM FILTRADO_20261103.xlsx` | igual que en GENERABASE |
| `FICHERO BASE_20261103.xlsx` | igual que en GENERABASE (hoja `TODOS`, con la columna TIPO); no depende del TIPO elegido |
| `PRUEBAESTANDAR_AR_20261103.xlsx` | sólo los artículos del TIPO, con la estructura de siempre (sin la columna TIPO) y las columnas ELECCIÓN rellenas, en cajas |
| `REPARTOESTANDAR_AR_20261103.xls` | la misma elección en **unidades** (cajas × UNIxCAJA), en formato Excel 97-2003 y con el formato de la plantilla del programa de importación |

- Calcular otro TIPO el mismo día crea su propio PRUEBAESTANDAR y REPARTOESTANDAR, sin tocar los de los otros TIPOS.
- Los ficheros de entrada no se modifican nunca.
- Si alguno de los 4 ficheros ya existe, el programa pide una sola confirmación, que nombra sólo los que existen.
- Si alguno está abierto en Excel, ofrece *Reintentar* después de cerrarlo, sin volver a calcular.

**Otro TIPO sin esperar al Access:** si, tras una ejecución, sólo cambias el TIPO o la tabla de tiendas y vuelves a pulsar Ejecutar, el programa reutiliza el FICHERO BASE y los días ya calculados y no vuelve a leer el Access. Si cambias el nº de artículos o cualquiera de los otros 4 ficheros (o se modifican en disco), lo vuelve a leer todo. Al cerrar el programa se olvida lo leído.

Al terminar, la ventana muestra un resumen con:
- las 4 rutas;
- los totales de control de SALALM FILTRADO, FICHERO BASE y el Access;
- el nº de días de datos con su primera y última fecha;
- el TIPO y su nº de artículos;
- las tiendas procesadas, las tiendas sin selección, el total de cajas y el total de unidades;
- los avisos.

## Formato de los ficheros

### Base del TIPO (PRUEBAESTANDAR)

El programa la forma a partir del FICHERO BASE: las filas del TIPO elegido, sin la columna B (TIPO). Es la estructura de siempre del fichero base de PRUEBAESTANDAR, que es la que tiene `PRUEBAESTANDAR_<TIPO>_<fecha>.xlsx`:

| Fila | A | B | C | D | E, F, G (se repite cada 3 columnas por tienda) |
|---|---|---|---|---|---|
| 1 | | | | | código de tienda en las 3 columnas |
| 2 | CODIGO | PESO (Kg) | Volumen (L) | UNIxCAJA | `BULTOS`, `LINEAS`, `ELECCIÓN` |
| 3… | artículo | kg por caja | L por caja | unidades por caja | bultos (cajas) y líneas del periodo; ELECCIÓN la rellena el programa |

- Admite cualquier nº de artículos. En tiendas admite hasta 255, que es el límite de columnas del formato `.xls` de REPARTOESTANDAR.
- BULTOS o LINEAS vacíos cuentan como 0. BULTOS puede tener decimales.
- **UNIxCAJA** es obligatorio en todos los artículos y debe ser un entero ≥ 1.
- Un artículo sin peso o volumen válido (vacío o ≤ 0) no se selecciona y aparece en los avisos.
- Los códigos de tienda pueden ser cualquier número (por ejemplo 82 en lugar de 10082), pero **deben coincidir** con los de la tabla de tiendas y medios.

### Tabla de tiendas y medios (primera hoja)

Encabezados en la fila 1 y, a partir de la fila 2: `TIENDA`, `TIPO DE MEDIO` (`PALET` o `CARRO`), `PESO MAX (Kg)`, `VOLUMEN MÁX (L)`, `DENSIDAD` (kg/L). Puede tener más tiendas que el FICHERO BASE, pero **todas** las tiendas del FICHERO BASE deben estar en la tabla.

Si algo no cuadra (encabezados, tiendas repetidas o que faltan, valores no numéricos…), el programa no genera ningún fichero y muestra qué fila o columna revisar.

### REPARTOESTANDAR_<TIPO>_<fecha>.xls (salida)

- Hoja `Hoja1`; las hojas `Hoja2` y `Hoja3` van vacías.
- En A1, el texto `Código`.
- En la fila 1, desde B, los códigos de tienda como números, en el orden del fichero base.
- Desde la fila 2, un artículo por fila (código como número) y, en cada tienda, las unidades elegidas (cajas × UNIxCAJA). La celda queda vacía si la tienda no lleva ese artículo.
- Fuentes, bordes, relleno, anchos y altos son como los de la plantilla del programa de importación.

## Reglas de selección (por tienda)

1. **Artículos elegibles:** solo los que tienen BULTOS > 0 en esa tienda y peso y volumen válidos.
2. **Máximo de cajas por artículo:** ⌈BULTOS / nº de días⌉ (redondeo hacia arriba), con el nº de días contado en el Access.
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

Código en `pruebaestandar/` (usa también el paquete `generabase/`):
- `integrado.py`: flujo unificado (FICHERO BASE, TIPO, días del Access, nombres con TIPO y fecha, los 4 ficheros).
- `lectura.py`: lectura y validación de la base del TIPO y de la tabla de tiendas.
- `seleccion.py`: algoritmo de selección.
- `verificacion.py`: comprobación final.
- `escritura.py`: escritura de PRUEBAESTANDAR.
- `reparto.py`: REPARTOESTANDAR.
- `proceso.py`: cálculo del palet a partir de una base del TIPO.
- `gui.py`: ventana.

La especificación vigente está en `openspec/specs/`.

---

# GENERABASE

Aplicación independiente que **sólo genera el FICHERO BASE** y un **SALALM FILTRADO** a partir de tres Excel y del Access de movimientos. Tiene su propio ejecutable, `GENERABASE.exe`. Se descarga como zip desde la pestaña **Actions**, en la ejecución «Compilar GENERABASE.exe» (apartado *Artifacts*). Si se usa con Python: `pip install -r requirements-generabase.txt` y doble clic en `GENERABASE.pyw`.

> PRUEBAESTANDAR ya incluye todo lo que hace GENERABASE. GENERABASE sigue disponible para quien sólo quiera el FICHERO BASE; sus ficheros se llaman, sin fecha, `SALALM FILTRADO.xlsx` y `FICHERO BASE.xlsx`.

## Entradas

| Fichero | Columnas que se usan (se buscan por nombre, en cualquier orden) |
|---|---|
| SALALM (.xlsx) | CODIGO, CAJAS, DESCRIPC, DESSEC, BAJA, UNIXCAJA, RADUBICA, PESO, VOLUMEN |
| MAESTRO (.xlsx) | MAARTI, MACADU, MACLCA |
| MAESTRO DE CADUCIDAD (.xlsx) | C3CADU, C3UTIL, C3COME |
| MOVIMIENTOS (Access .accdb/.mdb, tabla `MOVIMIENTOS`) | MVARTI, MVTMOV, MVDESM, MVCANM, MVUNCA, MVFECI |

Además se indica el **nº de artículos** del FICHERO BASE: un entero mayor que 0.

MVFECI es obligatoria: si un movimiento PI de las tiendas en rango no tiene una fecha válida, el programa se detiene indicando la fila.

El Access se lee **sin controladores de Microsoft**. En cada ejecución se comprueba que se han leído tantas filas como declara la tabla, y que todas las columnas tienen el mismo nº de valores. Si algo falla, no se genera nada.

## Salidas (en la carpeta del fichero SALALM)

### SALALM FILTRADO.xlsx
Un artículo por fila, con estas columnas:
- **CODIGO, DESCRIPCIÓN, CAJAS, UNIXCAJA:** se copian de SALALM.
- **PESO:** PESO ÷ 1000, en kg por caja.
- **VOLUMEN:** VOLUMEN ÷ 1000, en litros por caja.
- **SECCIÓN:** se copia de SALALM.
- **CADUCA y CADUCIDAD CODIGO:** MACADU y MACLCA del MAESTRO.
- **CADUCIDAD y DESCRIPCIÓN CADUCIDAD:** C3UTIL y C3COME del MAESTRO DE CADUCIDAD.
- **BAJAS:** se copia de SALALM.
- **UBICACIÓN:** las 3 primeras cifras de RADUBICA.
- **TIPO DE UBICACIÓN:** depende de la ubicación:
  - menos de 220: ALIMENTACIÓN;
  - de 220 a 290: ALTA ROTACIÓN;
  - de 291 a 399: PASILLO ESTRECHO;
  - de 400 a 599: BAZAR ABAJO;
  - 600 o más: DROGUERÍA.

**Se excluyen**, en este orden:
1. Las secciones SUMINISTROS Y SERVICIOS y CAMPAÑA FIDELIDAD.
2. Las bajas («B»).
3. Los artículos sin ubicación (vacía o 000).
4. PASILLO ESTRECHO y BAZAR ABAJO.
5. Las caducidades **conocidas** menores de 92 días.

Los artículos que no caducan, o que no están en el MAESTRO, se mantienen con la caducidad vacía. El fichero se ordena por CAJAS de mayor a menor.

### FICHERO BASE.xlsx (hoja `TODOS`)
- **Artículos:** los N primeros de SALALM FILTRADO, con CODIGO, TIPO, PESO (Kg), Volumen (L) y UNIxCAJA.
- **Tiendas:** se usan los movimientos con MVTMOV = PI de las tiendas 10081–10349 y 10399–10999. A cada código se le resta 10000 y hay un bloque BULTOS / LINEAS / ELECCIÓN por tienda, en orden ascendente.
- **Celdas de cada bloque:**
  - BULTOS = suma de |MVCANM| ÷ MVUNCA;
  - LINEAS = nº de **días distintos** (valores distintos de MVFECI) en que la tienda ha pedido el artículo; varios movimientos del mismo día cuentan como 1;
  - ELECCIÓN queda vacía.
- Antes de guardar se comprueba que los totales de BULTOS y LINEAS cuadran con los movimientos.

## Totales de control
Al terminar, la ventana muestra lo que se ha leído del Access para que puedas compararlo con una consulta de totales en Access:
- filas leídas y declaradas;
- filas PI y filas PI en los rangos de tienda;
- tiendas y artículos distintos;
- suma de CAJAS y LINEAS (nº de movimientos usados);
- días distintos (MVFECI) y fechas mínima y máxima;
- fechas.

También muestra cuántos artículos ha quitado cada regla y los avisos.

## Desarrollo
```
pip install -r requirements-generabase-dev.txt
python -m pytest tests_generabase
```
Código en `generabase/`:
- `lectura.py`: los Excel.
- `access.py`: el Access.
- `salalm.py`: SALALM FILTRADO.
- `fichero_base.py`: FICHERO BASE.
- `proceso.py`: orquestación.
- `gui.py`: ventana.
