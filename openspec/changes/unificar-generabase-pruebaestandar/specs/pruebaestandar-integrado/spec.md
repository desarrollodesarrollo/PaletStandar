## Purpose

Unir en PRUEBAESTANDAR la generación del FICHERO BASE y el cálculo del palet estándar. En una sola ejecución, a partir de SALALM, MAESTRO, MAESTRO DE CADUCIDAD, MOVIMIENTOS (Access) y la TABLA DE TIENDAS Y MEDIOS, se obtienen SALALM FILTRADO, FICHERO BASE, PRUEBAESTANDAR y REPARTOESTANDAR para el TIPO de palet elegido.

## ADDED Requirements

### Requirement: Generación del FICHERO BASE dentro de PRUEBAESTANDAR
En cada ejecución, el sistema SHALL generar `SALALM FILTRADO.xlsx` y `FICHERO BASE.xlsx` exactamente como lo hace GENERABASE, con el nº de artículos N indicado por el usuario. Se aplican las mismas reglas de lectura, filtrado, selección de los N artículos con más CAJAS (de cualquier TIPO), BULTOS, LINEAS, estructura, comprobaciones y totales de control del Access, definidas en las capacidades `generabase-lectura`, `generabase-salalm-filtrado` y `generabase-fichero-base`. El TIPO elegido MUST NOT cambiar el contenido de estos dos ficheros.

#### Scenario: Mismo FICHERO BASE que GENERABASE
- **WHEN** se ejecuta PRUEBAESTANDAR con unos ficheros, N = 1000 y el TIPO DROGUERÍA
- **THEN** `FICHERO BASE.xlsx` y `SALALM FILTRADO.xlsx` tienen el mismo contenido que los que genera GENERABASE con esos ficheros y N = 1000

#### Scenario: El TIPO no cambia el FICHERO BASE
- **WHEN** se ejecuta dos veces con los mismos ficheros y N, una con ALTA ROTACIÓN y otra con ALIMENTACIÓN
- **THEN** los dos `FICHERO BASE.xlsx` tienen el mismo contenido

### Requirement: Selección del TIPO de palet estándar
El usuario SHALL elegir uno de estos tres TIPOS de palet estándar: `ALTA ROTACIÓN`, `DROGUERÍA` o `ALIMENTACIÓN`. Primero se forman los N artículos del FICHERO BASE. Después, el palet estándar se calcula sólo con los artículos del FICHERO BASE cuya columna B (TIPO) coincide con el TIPO elegido. La comparación no distingue mayúsculas, tildes ni espacios extremos. Esos artículos se usan en el mismo orden en que aparecen en el FICHERO BASE.

Si ningún artículo del FICHERO BASE es del TIPO elegido, el sistema MUST mostrar un error que lo diga, con el TIPO y N, y MUST NOT guardar ningún fichero. Si hay menos artículos del TIPO que N, no es un error: el resumen SHALL indicar cuántos hay.

#### Scenario: Artículos de un TIPO
- **WHEN** el FICHERO BASE tiene 1000 artículos, de ellos 412 de ALTA ROTACIÓN, y el usuario elige ALTA ROTACIÓN
- **THEN** PRUEBAESTANDAR.xlsx y REPARTOESTANDAR.xls contienen esos 412 artículos, en el orden del FICHERO BASE, y el resumen indica `ALTA ROTACIÓN: 412 artículos de los 1000 del FICHERO BASE`

#### Scenario: Ningún artículo del TIPO
- **WHEN** ninguno de los N artículos del FICHERO BASE es de DROGUERÍA y el usuario elige DROGUERÍA
- **THEN** el sistema muestra un error indicando que no hay artículos de DROGUERÍA entre los N del FICHERO BASE y no genera ningún fichero

### Requirement: Nº de días de datos desde el Access
El sistema SHALL calcular el nº de días de datos como el nº de valores distintos de la columna `MVFECI` en las filas de la tabla MOVIMIENTOS cuya columna `MVTMOV` es `PI`. La comparación de `PI` no distingue mayúsculas ni espacios extremos. Cuentan las filas PI de todas las tiendas, estén o no en los rangos de tienda usados para el FICHERO BASE.

Las filas PI con `MVFECI` vacío no se cuentan, y el resumen SHALL avisar de cuántas hay. Si el recuento resulta 0, el sistema MUST mostrar un error y MUST NOT guardar ningún fichero. El nº de días obtenido es el que se usa en el cálculo del máximo de cajas por artículo.

#### Scenario: Días distintos de las filas PI
- **WHEN** las filas PI del Access tienen las fechas 20251001, 20251001, 20251002 y 20251006, y una fila de tipo `PS` tiene la fecha 20251003
- **THEN** el nº de días de datos es 3

#### Scenario: Fecha de una tienda fuera de rango
- **WHEN** la única fila PI con fecha 20251007 es de la tienda 10350, que no está en los rangos de tienda
- **THEN** el 20251007 cuenta igualmente como día de datos

#### Scenario: Sin filas PI con fecha
- **WHEN** el Access no tiene ninguna fila PI con MVFECI
- **THEN** el sistema muestra un error indicando que no se ha podido contar el nº de días de datos y no genera ningún fichero

### Requirement: Base del TIPO con la estructura de PRUEBAESTANDAR
Para calcular el palet estándar, el sistema SHALL formar la base del TIPO con la estructura de fichero base de la capacidad `ficheros-excel`:
- `CODIGO`, `PESO (Kg)`, `Volumen (L)` y `UNIxCAJA` en A–D.
- Bloques `BULTOS`, `LINEAS`, `ELECCIÓN` desde la columna E, uno por cada tienda del FICHERO BASE, en el mismo orden y con el mismo código de tienda.
- Una fila por artículo del TIPO, con los mismos valores que su fila del FICHERO BASE, sin la columna TIPO.

Antes de guardar, el sistema MUST comprobar que cada fila de la base del TIPO coincide con la fila del mismo artículo en el FICHERO BASE. Las celdas que se comparan son CODIGO, PESO, Volumen, UNIxCAJA, y BULTOS y LINEAS de cada tienda. Si no coinciden, MUST NOT guardar ningún fichero.

#### Scenario: Columnas desplazadas por TIPO
- **WHEN** en el FICHERO BASE el artículo 2465665 tiene UNIxCAJA 6 en la columna E y BULTOS 1,5 en la columna F (tienda 81)
- **THEN** en la base del TIPO tiene UNIxCAJA 6 en la columna D y BULTOS 1,5 en la columna E (tienda 81)

### Requirement: Ficheros generados
Al terminar correctamente, el sistema SHALL guardar en la carpeta del fichero SALALM:
- `SALALM FILTRADO.xlsx` y `FICHERO BASE.xlsx`;
- `PRUEBAESTANDAR.xlsx`: la base del TIPO con las columnas ELECCIÓN rellenas según la capacidad `ficheros-excel`;
- `REPARTOESTANDAR.xls`: con el formato definido en la capacidad `ficheros-excel` y los artículos y tiendas de la base del TIPO.

Los nombres de los 4 ficheros MUST NOT depender del TIPO. Los 4 ficheros MUST calcularse y comprobarse antes de guardar el primero. Si un error de validación o una comprobación falla, no se guarda ninguno. Si un fichero no se puede escribir porque está abierto, el usuario SHALL poder reintentar el guardado sin repetir el cálculo ni la lectura del Access. Los ficheros de entrada MUST NOT modificarse nunca.

#### Scenario: Cuatro ficheros
- **WHEN** la ejecución termina sin errores con el SALALM `C:\datos\salalm.xlsx`
- **THEN** existen `C:\datos\SALALM FILTRADO.xlsx`, `C:\datos\FICHERO BASE.xlsx`, `C:\datos\PRUEBAESTANDAR.xlsx` y `C:\datos\REPARTOESTANDAR.xls`

#### Scenario: Error en la tabla de tiendas
- **WHEN** faltan en la TABLA DE TIENDAS Y MEDIOS tiendas del FICHERO BASE
- **THEN** el sistema muestra el error con las tiendas que faltan y no guarda ninguno de los 4 ficheros

#### Scenario: PRUEBAESTANDAR.xlsx abierto
- **WHEN** PRUEBAESTANDAR.xlsx está abierto en Excel al guardar y el usuario lo cierra y pulsa Reintentar
- **THEN** se guardan los ficheros sin volver a leer el Access

### Requirement: Cambiar de TIPO sin volver a leer el Access
Después de una ejecución correcta, si el usuario vuelve a ejecutar con los mismos ficheros SALALM, MAESTRO, MAESTRO DE CADUCIDAD y MOVIMIENTOS, sin cambios en disco desde la ejecución anterior, y con el mismo N, el sistema SHALL reutilizar el FICHERO BASE y el nº de días ya calculados. Lo único que puede cambiar es el TIPO o la TABLA DE TIENDAS Y MEDIOS, y no se vuelven a leer esos cuatro ficheros. Si cambia cualquiera de esos ficheros o N, el sistema MUST leerlos de nuevo. Cerrar el programa descarta lo reutilizable.

#### Scenario: Segundo TIPO rápido
- **WHEN** tras calcular ALTA ROTACIÓN el usuario elige DROGUERÍA y pulsa Ejecutar sin cambiar nada más
- **THEN** el proceso no vuelve a leer el Access, calcula DROGUERÍA y guarda los 4 ficheros

#### Scenario: Access modificado
- **WHEN** entre dos ejecuciones el fichero de MOVIMIENTOS ha cambiado de fecha de modificación o de tamaño
- **THEN** el sistema vuelve a leer el Access
