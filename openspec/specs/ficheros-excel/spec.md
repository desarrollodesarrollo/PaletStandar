# ficheros-excel Specification

## Purpose

Leer y validar el FICHERO BASE y la TABLA DE TIENDAS Y MEDIOS de PRUEBAESTANDAR, generar PRUEBAESTANDAR.xlsx con las columnas ELECCIÓN rellenas sin alterar el resto del fichero base, y generar REPARTOESTANDAR.xls con la elección en unidades para el programa de importación.

## Requirements

### Requirement: Estructura del fichero base
El sistema SHALL leer la primera hoja del fichero base (.xlsx) con esta estructura:
- Fila 1: código de tienda en cada columna de los bloques de tienda (columnas A–D vacías).
- Fila 2: encabezados `CODIGO`, `PESO (Kg)`, `Volumen (L)`, `UNIxCAJA` en A–D y, desde la columna E, bloques de 3 columnas con los encabezados `BULTOS`, `LINEAS`, `ELECCIÓN`.
- Fila 3 en adelante: un artículo por fila hasta la última fila con código en la columna A. La columna D (`UNIxCAJA`) contiene las unidades que lleva cada caja (bulto) del artículo.

El sistema MUST aceptar cualquier nº de artículos (filas) y cualquier nº de bloques de tienda, sin depender de que sean 130–650 artículos o 180 tiendas. Una celda de BULTOS o LINEAS vacía SHALL interpretarse como 0. Los códigos de tienda y de artículo pueden ser cualquier número (por ejemplo 82 en lugar de 10082); sólo MUST coincidir los códigos de tienda del fichero base con los de la tabla de tiendas y medios.

#### Scenario: Fichero base con estructura correcta
- **WHEN** el usuario aporta un fichero base con 130 artículos y 180 bloques de tienda (columnas A–TX)
- **THEN** el sistema identifica 130 artículos y 180 tiendas con sus BULTOS, LINEAS y UNIxCAJA

#### Scenario: Nº de artículos y tiendas distinto al habitual
- **WHEN** el fichero base tiene 977 artículos y 3 bloques de tienda
- **THEN** el sistema procesa los 977 artículos y las 3 tiendas sin error

#### Scenario: Celdas vacías de salida
- **WHEN** un artículo tiene BULTOS y LINEAS vacíos para una tienda
- **THEN** el sistema considera 0 bultos y 0 líneas para esa tienda

#### Scenario: Códigos de tienda cortos
- **WHEN** el fichero base y la tabla de tiendas usan los códigos 81 a 949
- **THEN** el sistema procesa las tiendas con esos códigos sin error

### Requirement: Validación del fichero base
El sistema MUST rechazar el fichero base, sin generar ningún fichero de salida y con un mensaje en español que indique la columna o fila afectada, cuando:
- la celda D2 no tenga el encabezado `UNIxCAJA` (comparación sin distinguir mayúsculas ni espacios extremos),
- el UNIxCAJA de algún artículo esté vacío, no sea numérico, no sea entero o sea menor que 1,
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

#### Scenario: Fichero base antiguo con densidad en la columna D
- **WHEN** la celda D2 contiene `Densidad (kg/l)`
- **THEN** el sistema muestra un error indicando que la columna D debe ser `UNIxCAJA` y no genera ningún fichero

#### Scenario: UNIxCAJA no válido
- **WHEN** el artículo de la fila 7 tiene UNIxCAJA vacío, `0`, `-2`, `2,5` o `abc`
- **THEN** el sistema muestra un error que menciona la fila 7 y la columna D y no genera ningún fichero

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

### Requirement: Fichero de salida REPARTOESTANDAR.xls
Al terminar correctamente, además de PRUEBAESTANDAR.xlsx, el sistema SHALL guardar `REPARTOESTANDAR.xls` en la misma carpeta que el fichero base, con el formato de la plantilla del programa de importación:
- Formato Excel 97-2003 (`.xls`, BIFF8), con las hojas `Hoja1`, `Hoja2` y `Hoja3`; los datos van en `Hoja1` y las otras dos quedan vacías.
- Celda A1: el texto `Código`.
- Fila 1, desde la columna B: una columna por tienda del fichero base, en el mismo orden, con el código de tienda como número.
- Desde la fila 2: una fila por cada artículo del fichero base, en el mismo orden, con el código de artículo como número en la columna A, aunque el artículo no se haya elegido en ninguna tienda.
- Cada celda artículo × tienda MUST contener el número entero ELECCIÓN × UNIxCAJA cuando el artículo se ha elegido en esa tienda, y MUST quedar vacía cuando no.
- Fuentes, bordes, relleno, anchos de columna y altos de fila SHALL imitar los de la plantilla: encabezado A1 en Arial 12 negrita con relleno y borde fino, códigos de tienda en Arial 10 negrita con borde fino, códigos de artículo con formato numérico `0`, datos con borde fino.

Como un `.xls` admite como máximo 256 columnas, si el fichero base tiene más de 255 tiendas el sistema MUST rechazar el proceso antes de calcular, con un mensaje que lo explique.

#### Scenario: Unidades por tienda
- **WHEN** en la tienda 82 se eligen 3 cajas del artículo 2101538, que tiene UNIxCAJA 18
- **THEN** la celda de ese artículo en la columna de la tienda 82 contiene 54

#### Scenario: Artículo no elegido
- **WHEN** el artículo 2102526 no se elige en la tienda 81
- **THEN** su celda en la columna de la tienda 81 queda vacía

#### Scenario: Estructura del fichero
- **WHEN** el fichero base tiene 130 artículos y 180 tiendas
- **THEN** REPARTOESTANDAR.xls tiene en Hoja1 una fila de encabezado (`Código` y los 180 códigos de tienda como números) y 130 filas de artículos, y las hojas Hoja2 y Hoja3 vacías

#### Scenario: Demasiadas tiendas para .xls
- **WHEN** el fichero base tiene 300 bloques de tienda
- **THEN** el sistema muestra un error indicando que REPARTOESTANDAR.xls admite como máximo 255 tiendas y no genera ningún fichero

#### Scenario: Fichero de reparto abierto
- **WHEN** REPARTOESTANDAR.xls está abierto en Excel y no se puede escribir
- **THEN** el sistema muestra un error pidiendo cerrarlo y, al reintentar, guarda los ficheros sin repetir el cálculo

### Requirement: Comprobación final antes de guardar
Antes de guardar, el sistema MUST verificar de forma independiente del cálculo que, para cada tienda, la selección cumple todas las restricciones de la capacidad `seleccion-bultos` (enteros, máximos por artículo, peso y volumen con el 96 % aplicado, densidad y artículos sin salida), y que cada valor de REPARTOESTANDAR es exactamente ELECCIÓN × UNIxCAJA. Si algo falla, el sistema MUST NOT guardar ninguno de los dos ficheros y SHALL mostrar un error que identifique la tienda.

#### Scenario: Verificación correcta
- **WHEN** todas las tiendas cumplen las restricciones
- **THEN** el sistema guarda PRUEBAESTANDAR.xlsx y REPARTOESTANDAR.xls

#### Scenario: Verificación fallida
- **WHEN** la selección de la tienda 10082 supera el 96 % del volumen máximo
- **THEN** el sistema no guarda ningún fichero y muestra un error que menciona la tienda 10082
