# Spec Delta

## Purpose

Generar FICHERO BASE.xlsx con los N artículos de más salida de SALALM FILTRADO y, para cada tienda de los movimientos seleccionados del Access, los bultos y líneas de cada artículo, con la estructura de la plantilla aportada.

## ADDED Requirements

### Requirement: Nº de artículos
El usuario SHALL indicar el nº de artículos N como entero ≥ 1. El FICHERO BASE SHALL contener las N primeras filas de SALALM FILTRADO, en el mismo orden (más CAJAS primero). Si N es mayor que el nº de filas de SALALM FILTRADO, SHALL contener todas y el resumen MUST avisarlo. Cualquier otro valor (0, negativo, decimal, texto o vacío) MUST rechazarse antes de calcular.

#### Scenario: 1000 artículos
- **WHEN** el usuario indica 1000 y SALALM FILTRADO tiene 7.808 filas
- **THEN** el FICHERO BASE tiene los 1000 artículos con más CAJAS, en ese orden

#### Scenario: Más artículos de los disponibles
- **WHEN** el usuario indica 9000 y SALALM FILTRADO tiene 7.808 filas
- **THEN** el FICHERO BASE tiene las 7.808 y el resumen avisa de que sólo había 7.808

#### Scenario: Valor no válido
- **WHEN** el usuario escribe `mil`, `0` o `2,5`
- **THEN** el sistema pide un nº entero de artículos mayor que 0 y no calcula

### Requirement: Movimientos que se usan
Del Access SHALL usarse sólo las filas con MVTMOV = `PI` y con tienda (MVDESM como número) entre 10081 y 10349, o entre 10399 y 10999, ambos extremos incluidos. A cada tienda se le SHALL restar 10000 (10389 → 389). Para cada fila SHALL calcularse CAJAS = |MVCANM| ÷ MVUNCA. Una fila con MVUNCA vacío o ≤ 0 MUST excluirse y contarse en los avisos.

#### Scenario: Filtro de tipo y tienda
- **WHEN** hay movimientos PI de las tiendas 10080, 10081, 10349, 10350, 10398, 10399, 10999 y 11000, y un movimiento SI de la tienda 10100
- **THEN** sólo se usan los de 10081, 10349, 10399 y 10999, que pasan a ser las tiendas 81, 349, 399 y 999

#### Scenario: Cajas de un movimiento
- **WHEN** un movimiento tiene MVCANM -18 y MVUNCA 12
- **THEN** aporta 1,5 cajas

### Requirement: Estructura del FICHERO BASE
El fichero SHALL tener una hoja llamada `TODOS` con:
- Fila 1: vacía en A–E y, desde la columna F, el código de tienda (sin el 10000) repetido en las 3 columnas de su bloque.
- Fila 2: `CODIGO`, `TIPO`, `PESO (Kg)`, `Volumen (L)`, `UNIxCAJA` en A–E y, por cada tienda, `BULTOS`, `LINEAS`, `ELECCIÓN`.
- Desde la fila 3, un artículo por fila:
  - A: CODIGO como número.
  - B: TIPO DE UBICACIÓN.
  - C: PESO.
  - D: VOLUMEN.
  - E: UNIXCAJA.
  - Valores tomados de SALALM FILTRADO.

Habrá un bloque por cada tienda distinta de los movimientos usados, aunque ninguno de los N artículos haya tenido movimiento en ella. Los bloques SHALL ir ordenados por código de tienda ascendente.

#### Scenario: Estructura con los datos de ejemplo
- **WHEN** se genera con los ficheros de ejemplo y N = 1000
- **THEN** la hoja TODOS tiene 2 filas de encabezado, 1000 filas de artículos y 124 bloques de tienda, de la columna F en adelante, en orden ascendente desde la 81

### Requirement: BULTOS, LINEAS y ELECCIÓN
Para cada artículo y tienda:
- BULTOS SHALL ser la suma de CAJAS de sus movimientos usados, sin redondear. Si el resultado es entero se escribe como entero.
- LINEAS SHALL ser el nº de movimientos usados.
- Si no hay ningún movimiento, BULTOS y LINEAS MUST quedar vacías.
- ELECCIÓN MUST quedar siempre vacía.

Un artículo de los N sin ningún movimiento en ninguna tienda SHALL aparecer igualmente, con todas las celdas de tienda vacías.

#### Scenario: Suma y recuento
- **WHEN** el artículo 2465665 tiene en la tienda 389 dos movimientos de 16 y 8 unidades con MVUNCA 16
- **THEN** en el bloque de la tienda 389 su BULTOS es 1,5 y su LINEAS es 2

#### Scenario: Sin movimientos en una tienda
- **WHEN** un artículo no tiene movimientos en la tienda 82
- **THEN** sus celdas BULTOS y LINEAS de la tienda 82 están vacías

### Requirement: Formato y guardado
El FICHERO BASE SHALL guardarse como `FICHERO BASE.xlsx` en la carpeta del fichero SALALM, con los anchos de columna de la plantilla: A 22,43; B 15,14; C y D 13; E 15,14; resto 13. Antes de guardar, el sistema MUST comprobar que la suma de todos los BULTOS y LINEAS del fichero coincide con la de los movimientos usados de esos N artículos. Si no coincide, MUST NOT guardar.

#### Scenario: Comprobación de totales
- **WHEN** los movimientos usados de los N artículos suman 12.345,5 cajas y 9.876 líneas
- **THEN** el fichero sólo se guarda si sus BULTOS suman 12.345,5 y sus LINEAS 9.876
