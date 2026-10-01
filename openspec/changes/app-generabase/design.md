# Design

## Context

Datos observados en los ficheros de ejemplo:
- **SALALM** (`salalm.xlsx`, hoja `Hoja1`, 14.646 artículos × 49 columnas):
  - CODIGO es entero y no se repite.
  - CAJAS puede tener decimales.
  - PESO está en gramos y VOLUMEN en cm³: el art. 273137, 6 botellas de vino, tiene PESO 8000 y VOLUMEN 12648.
  - RADUBICA es texto de 8 posiciones; 3.402 filas valen `"   00000"`.
  - **DESCRIPC es igual a DESSEC en el 100 % de las filas.** Se copia tal cual, como pidió el usuario.
- **MAESTRO** (hoja `MSG001`, 22.621 filas): MAARTI es entero y único, y MAALMA vale siempre 1. MACADU es `S`/`N` y MACLCA va vacío si y sólo si MACADU = `N`. **4.886 artículos de SALALM no están en el MAESTRO.**
- **MAESTRO DE CADUCIDAD** (hoja `MVG003`, 51 códigos): C3CADU es texto y único (`1`, `A`, `B02`, `K`…). Todo MACLCA del MAESTRO existe en C3CADU.
- **Access** (`MOVIMIENTOS_CLAUDE.accdb`, ACE12 / Access 2007+, 22 MB):
  - Una única tabla de usuario, `MOVIMIENTOS`, con 52.150 filas y 40 columnas (incluida `Id`).
  - MVARTI y MVDESM son texto (`"000010389"`); MVCANM y MVUNCA son numéricos.
  - 51.835 filas son PI y 38.947 caen dentro de los rangos de tienda, que dan 124 tiendas.
  - No hay MVUNCA ≤ 0, y en 1.867 líneas CAJAS sale con decimales.
  - Los 5.835 artículos del Access están en SALALM.
- **Plantilla FICHERO BASE** (`FICHERO_BASE.xlsx`, hoja `TODOS`): A CODIGO, B TIPO, C PESO (Kg), D Volumen (L), E UNIxCAJA y bloques desde F. Tiendas ascendentes, BULTOS con decimales, celdas vacías sin movimiento y sin fórmulas. Sus volúmenes, del orden de 8 L para 6,8 kg, confirman el factor ÷ 1000 elegido.
- **Lectura del Access verificada**:
  - `access-parser` 0.0.6 (Python puro, Apache 2.0) lee las 52.150 filas y 40 columnas en 6,2 s con 150 MB de pico.
  - El resultado es **idéntico celda a celda** al de `mdbtools`.
  - La cabecera de la tabla declara `number_of_rows = 52150`.

## Goals / Non-Goals

**Goals:**
- Una app nueva y aislada de PRUEBAESTANDAR: ningún fichero de `pruebaestandar/`, `tests/`, `requirements*.txt` ni `compilar-exe.yml` cambia.
- Funciones de cálculo puras, probadas con datos sintéticos pequeños, y una prueba de aceptación con los ficheros reales fuera del repositorio.
- No generar nunca un fichero a medias o con totales que no cuadren.

**Non-Goals:**
- Adaptar PRUEBAESTANDAR para aceptar la columna TIPO (será un cambio aparte).
- Leer consultas guardadas de Access (sólo tablas), bases con contraseña o campos adjuntos y multivalor.
- Usar el controlador ODBC de Access de Microsoft. Si la memoria con el Access real fuese un problema, se valoraría en un cambio posterior.

## Decisions

### 1. Estructura aislada
- Paquete `generabase/` con estos módulos:
  - `columnas.py`: búsqueda de columnas por encabezado y normalización de códigos.
  - `lectura.py`: los 3 Excel.
  - `access.py`: lectura de MOVIMIENTOS y sus comprobaciones.
  - `salalm.py`: construcción, filtro y orden.
  - `fichero_base.py`: top N, agregación y escritura.
  - `proceso.py`: orquestación y resumen.
  - `gui.py`: la ventana.
- Arranque con `GENERABASE.pyw` y `python -m generabase`.
- Pruebas en `tests_generabase/`, que se añade a `testpaths` de `pytest.ini`.
- Dependencias en `requirements-generabase.txt` (openpyxl, access-parser) y `requirements-generabase-dev.txt` (+ pytest). Así no se tocan los `requirements*.txt` de PRUEBAESTANDAR, cuyo workflow se dispara al cambiar `requirements.txt`.
- Alternativa descartada: reutilizar módulos de `pruebaestandar/`. Acoplaría las dos apps, y el usuario pidió expresamente que no se toque la otra.

### 2. Lectura de Excel
- `openpyxl` en modo `read_only`, sobre la primera hoja.
- Un índice `{ENCABEZADO normalizado: posición}` permite pedir columnas por nombre. Si falta alguna, el error nombra fichero y columna.
- Los 3 Excel suman unos 13 MB y se leen en segundos.

### 3. Lectura del Access con `access-parser`
- `AccessParser(ruta)`. Si `MOVIMIENTOS` no está en `catalog`, el error lista las tablas que no son de sistema.
- `parse_table("MOVIMIENTOS")` devuelve `{columna: [valores]}`; se compara con `get_table(...).table_header.number_of_rows`.
- Se comprueba que todas las listas tienen la misma longitud.
- Justo después se conservan sólo las 5 columnas necesarias (más `MVFECI` si existe, para el resumen) y se libera el resto, para no mantener 40 columnas en memoria durante el cálculo.
- Errores de la librería (formato no soportado, base cifrada) → `ErrorValidacion` con un mensaje claro.
- La librería se mantiene detrás de una única función, `leer_movimientos(ruta) -> Movimientos`, por si en el futuro hay que añadir ODBC.

### 4. Normalización de códigos
- `entero(v)`: acepta int, float entero (`273137.0`) y texto de dígitos con espacios o ceros a la izquierda; cualquier otra cosa devuelve `None`.
- `codigo_texto(v)`: `str(v).strip()`, convirtiendo `1.0` en `"1"`, para que MACLCA cuadre con C3CADU.

### 5. SALALM FILTRADO
- Por fila: cruce con MAESTRO por diccionario `{MAARTI: (MACADU, MACLCA)}` y con caducidades por `{C3CADU: (C3UTIL, C3COME)}`.
- PESO ÷ 1000 y VOLUMEN ÷ 1000 se guardan como float.
- UBICACIÓN = `entero(RADUBICA[:3])`.
- TIPO se calcula con los tramos; el texto es «ALTA ROTACIÓN», no «AR».
- Exclusión en el orden fijado por la spec, contando cada fila en el primer motivo que cumple.
- Orden con `sorted(key=(-CAJAS, CODIGO))`.
- Escritura con `openpyxl` (no read_only): encabezados en negrita, primera fila fijada y anchos razonables. Se guarda primero en un fichero temporal en la misma carpeta y luego se renombra, para no dejar un fichero a medias.

### 6. FICHERO BASE
- Top N de SALALM FILTRADO.
- Agregación del Access en una sola pasada: `{(articulo, tienda): [cajas, lineas]}`, sólo para los artículos del top N.
- Tiendas = conjunto de tiendas de todos los movimientos usados, ordenado ascendente.
- La suma de cajas se hace con `math.fsum` por clave. Se escribe `int` cuando el valor es entero y el `float` sin redondear en otro caso, como en la plantilla.
- Hoja `TODOS`, filas 1–2 de encabezado y anchos de la plantilla.
- Comprobación previa al guardado: la suma de BULTOS y LINEAS escritos se recalcula desde los movimientos usados de los N artículos (usando `math.isclose`) y se compara.

### 7. Ventana
- Misma arquitectura que ya funciona en PRUEBAESTANDAR (tkinter, hilo de trabajo, cola y `after`), pero con código propio en `generabase/gui.py`.
- Cuatro selectores: el del Access filtra `*.accdb *.mdb`.
- Caja «Nº de artículos», etiqueta de fase y resumen en un cuadro de texto con barra de desplazamiento.
- Ofrece Reintentar ante `PermissionError`, guardando sin releer.

### 8. Ejecutable
- Nuevo workflow `compilar-generabase-exe.yml`, copia adaptada del existente. Se dispara con `generabase/**`, `GENERABASE.pyw`, `requirements-generabase*.txt` y el propio workflow.
- PyInstaller `--onefile --windowed --name GENERABASE`, con comprobación de que se abre la ventana «GENERABASE».
- Artefacto `GENERABASE-windows`. El workflow de PRUEBAESTANDAR no se modifica.

### 9. Pruebas
- **Sintéticas**:
  - Excel generados con openpyxl.
  - Para el Access se prueban los cálculos con un objeto `Movimientos` en memoria, y las comprobaciones de lectura con un sustituto de `AccessParser` que simula filas declaradas, columnas desiguales o tablas ausentes. Sin Access no se puede crear un `.accdb` (mdbtools solo lee), y no se sube al repositorio ningún fichero real. Por eso la lectura real se verifica en la aceptación con la copia de ejemplo.
- **Aceptación** (fuera del repo) con los ficheros de ejemplo:
  - recuentos de la spec (7.808 filas y exclusiones por regla);
  - 124 tiendas y totales de control;
  - comparación de la lectura del Access con mdbtools celda a celda;
  - comprobación independiente de BULTOS y LINEAS de unos cuantos artículos contra el CSV de mdbtools.

## Risks / Trade-offs

- [Memoria con el Access real: unos 2 GB estimados, porque access-parser carga la tabla entera] → Se liberan las columnas que no se usan nada más leer. Se medirá con el Access real; si no cabe en el PC, se valorará ODBC o exportar la tabla.
- [`access-parser` es joven (v0.0.6) y podría fallar con algún tipo de campo] → Comprobaciones de nº de filas y columnas en cada ejecución, totales de control visibles y verificación cruzada con mdbtools en la aceptación. MOVIMIENTOS sólo usa textos y números, que se leen bien.
- [DESCRIPC no trae la descripción del artículo, sino la sección] → Se copia tal cual, según lo pedido, y queda anotado. Si existe otra columna con la descripción real, se cambia el origen en un momento.
- [El FICHERO BASE no es compatible todavía con PRUEBAESTANDAR] → Decisión del usuario; queda documentado en el README y en el resumen de la ventana.
- [1.812 artículos sin datos en el MAESTRO pasan el filtro sin caducidad] → Decisión del usuario; el resumen indica cuántos son.

## Migration Plan

App nueva: se descarga el zip `GENERABASE-windows` desde GitHub Actions y se usa igual que PRUEBAESTANDAR. Para volver atrás basta con no usarla; PRUEBAESTANDAR no cambia.

## Open Questions

- Si en el futuro hay otra columna con la descripción real del artículo, ¿se usa en lugar de DESCRIPC? No cambia la arquitectura, solo de qué columna se copia el dato.
