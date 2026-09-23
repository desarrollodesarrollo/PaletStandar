# Spec Delta

## Purpose

Leer y validar el FICHERO BASE y la TABLA DE TIENDAS Y MEDIOS de PRUEBAESTANDAR, y generar el fichero de salida PRUEBAESTANDAR.xlsx con las columnas ELECCIÓN rellenas sin alterar el resto del fichero base.

## ADDED Requirements

### Requirement: Estructura del fichero base
El sistema SHALL leer la primera hoja del fichero base (.xlsx) con esta estructura:
- Fila 1: código de tienda en cada columna de los bloques de tienda (columnas A–D vacías).
- Fila 2: encabezados `CODIGO`, `PESO (Kg)`, `Volumen (L)`, `Densidad (kg/l)` en A–D y, desde la columna E, bloques de 3 columnas con los encabezados `BULTOS`, `LINEAS`, `ELECCIÓN`.
- Fila 3 en adelante: un artículo por fila hasta la última fila con código en la columna A.

El sistema MUST aceptar cualquier nº de artículos (filas) y cualquier nº de bloques de tienda, sin depender de que sean 130–650 artículos o 180 tiendas. Una celda de BULTOS o LINEAS vacía SHALL interpretarse como 0.

#### Scenario: Fichero base con estructura correcta
- **WHEN** el usuario aporta un fichero base con 130 artículos y 180 bloques de tienda (columnas A–TX)
- **THEN** el sistema identifica 130 artículos y 180 tiendas con sus BULTOS y LINEAS

#### Scenario: Nº de artículos y tiendas distinto al habitual
- **WHEN** el fichero base tiene 977 artículos y 3 bloques de tienda
- **THEN** el sistema procesa los 977 artículos y las 3 tiendas sin error

#### Scenario: Celdas vacías de salida
- **WHEN** un artículo tiene BULTOS y LINEAS vacíos para una tienda
- **THEN** el sistema considera 0 bultos y 0 líneas para esa tienda

### Requirement: Validación del fichero base
El sistema MUST rechazar el fichero base, sin generar salida y con un mensaje en español que indique la columna o fila afectada, cuando:
- algún bloque de tienda no tenga exactamente los encabezados `BULTOS`, `LINEAS`, `ELECCIÓN` en la fila 2 (comparación sin distinguir mayúsculas ni espacios extremos),
- las 3 columnas de un bloque no tengan el mismo código de tienda en la fila 1,
- un mismo código de tienda aparezca en más de un bloque,
- el nº de columnas desde la E no sea múltiplo de 3,
- un valor de BULTOS o LINEAS no sea numérico o sea negativo.

#### Scenario: Encabezado de bloque incorrecto
- **WHEN** la columna G tiene en la fila 2 el texto `TOTAL` en lugar de `ELECCIÓN`
- **THEN** el sistema muestra un error que menciona la columna G y no genera fichero de salida

#### Scenario: Tienda repetida
- **WHEN** la tienda 10081 aparece en dos bloques
- **THEN** el sistema muestra un error que indica la tienda 10081 repetida

### Requirement: Artículos sin peso o volumen válidos
Un artículo con PESO o VOLUMEN vacío, no numérico o menor o igual que 0 SHALL no seleccionarse en ninguna tienda, y el sistema MUST incluirlo en la lista de avisos del resumen final.

#### Scenario: Artículo con volumen 0
- **WHEN** el artículo 2101538 tiene volumen 0
- **THEN** su columna ELECCIÓN queda vacía en todas las tiendas y el resumen muestra un aviso con su código

### Requirement: Estructura y validación de la tabla de tiendas y medios
El sistema SHALL leer la primera hoja de la tabla de tiendas (.xlsx) con encabezados en la fila 1 y, desde la fila 2, una tienda por fila: A = TIENDA, B = TIPO DE MEDIO, C = PESO MAX (Kg), D = VOLUMEN MÁX (L), E = DENSIDAD (kg/L). El TIPO DE MEDIO SHALL aceptarse como `PALET` o `CARRO` sin distinguir mayúsculas ni espacios extremos. La tabla puede contener más tiendas que el fichero base; las sobrantes se ignoran.

El sistema MUST rechazar el proceso, sin generar salida, cuando alguna tienda del fichero base no exista en la tabla (listando todas las que faltan), o cuando alguna tienda usada tenga un TIPO DE MEDIO distinto de PALET/CARRO o un peso, volumen o densidad vacío, no numérico o menor o igual que 0.

#### Scenario: Tabla con más tiendas que el fichero base
- **WHEN** la tabla tiene 2467 tiendas y el fichero base 180, todas presentes en la tabla
- **THEN** el sistema usa sólo los datos de esas 180 tiendas

#### Scenario: Tiendas que faltan en la tabla
- **WHEN** las tiendas 10081 y 10949 del fichero base no están en la tabla
- **THEN** el sistema muestra un error que lista 10081 y 10949 y no genera fichero de salida

#### Scenario: Tipo de medio desconocido
- **WHEN** una tienda usada tiene TIPO DE MEDIO `CAMION`
- **THEN** el sistema muestra un error que indica la tienda y el valor `CAMION`

### Requirement: Fichero de salida PRUEBAESTANDAR.xlsx
Al terminar correctamente, el sistema SHALL guardar una copia del fichero base llamada `PRUEBAESTANDAR.xlsx` en la misma carpeta que el fichero base. En esa copia:
- cada celda ELECCIÓN de un artículo seleccionado MUST contener un número entero ≥ 1 (tipo numérico, no texto);
- cada celda ELECCIÓN de un artículo no seleccionado MUST quedar vacía, aunque en el fichero de entrada tuviera un valor;
- el resto de celdas, hojas, anchos de columna y formatos MUST mantenerse como en el fichero base.

El fichero base original MUST NOT modificarse nunca.

#### Scenario: Salida generada
- **WHEN** el proceso termina sin errores para el fichero `C:\datos\FICHERO_BASE_AR.xlsx`
- **THEN** existe `C:\datos\PRUEBAESTANDAR.xlsx` con las columnas ELECCIÓN rellenas y `FICHERO_BASE_AR.xlsx` no ha cambiado

#### Scenario: Valores previos en ELECCIÓN
- **WHEN** el fichero base trae un 3 en una celda ELECCIÓN de un artículo que el programa no selecciona
- **THEN** esa celda queda vacía en PRUEBAESTANDAR.xlsx

#### Scenario: Fichero de salida abierto en Excel
- **WHEN** PRUEBAESTANDAR.xlsx está abierto en Excel y no se puede escribir
- **THEN** el sistema muestra un error pidiendo cerrar el fichero y no pierde el cálculo hecho hasta volver a intentarlo o cancelar

### Requirement: Comprobación final antes de guardar
Antes de guardar, el sistema MUST verificar de forma independiente del cálculo que, para cada tienda, la selección cumple todas las restricciones de la capacidad `seleccion-bultos` (enteros, máximos por artículo, peso, volumen, densidad y artículos sin salida). Si alguna tienda las incumple, el sistema MUST NOT guardar el fichero y SHALL mostrar un error que identifique la tienda.

#### Scenario: Verificación correcta
- **WHEN** todas las tiendas cumplen las restricciones
- **THEN** el sistema guarda PRUEBAESTANDAR.xlsx

#### Scenario: Verificación fallida
- **WHEN** la selección de la tienda 10082 supera el volumen máximo
- **THEN** el sistema no guarda el fichero y muestra un error que menciona la tienda 10082
