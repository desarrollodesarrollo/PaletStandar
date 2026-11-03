## MODIFIED Requirements

### Requirement: Estructura del fichero base
El fichero base que procesa PRUEBAESTANDAR SHALL ser la base del TIPO. El sistema la forma a partir del FICHERO BASE y del TIPO elegido, según la capacidad `pruebaestandar-integrado`. El usuario ya no la aporta. Tiene esta estructura:
- Fila 1: código de tienda en cada columna de los bloques de tienda (columnas A–D vacías).
- Fila 2: encabezados `CODIGO`, `PESO (Kg)`, `Volumen (L)`, `UNIxCAJA` en A–D y, desde la columna E, bloques de 3 columnas con los encabezados `BULTOS`, `LINEAS`, `ELECCIÓN`.
- Fila 3 en adelante: un artículo por fila hasta la última fila con código en la columna A. La columna D (`UNIxCAJA`) contiene las unidades que lleva cada caja (bulto) del artículo.

El sistema MUST aceptar cualquier nº de artículos (filas) y cualquier nº de bloques de tienda, sin depender de que sean 130–1000 artículos o 180 tiendas. Una celda de BULTOS o LINEAS vacía SHALL interpretarse como 0. BULTOS puede tener decimales. Los códigos de tienda y de artículo pueden ser cualquier número (por ejemplo 82 en lugar de 10082); sólo MUST coincidir los códigos de tienda del fichero base con los de la tabla de tiendas y medios.

#### Scenario: Fichero base con estructura correcta
- **WHEN** la base del TIPO tiene 130 artículos y 180 bloques de tienda (columnas A–TX)
- **THEN** el sistema identifica 130 artículos y 180 tiendas con sus BULTOS, LINEAS y UNIxCAJA

#### Scenario: Nº de artículos y tiendas distinto al habitual
- **WHEN** la base del TIPO tiene 977 artículos y 3 bloques de tienda
- **THEN** el sistema procesa los 977 artículos y las 3 tiendas sin error

#### Scenario: Celdas vacías de salida
- **WHEN** un artículo tiene BULTOS y LINEAS vacíos para una tienda
- **THEN** el sistema considera 0 bultos y 0 líneas para esa tienda

#### Scenario: Códigos de tienda cortos
- **WHEN** el FICHERO BASE y la tabla de tiendas usan los códigos 81 a 949
- **THEN** el sistema procesa las tiendas con esos códigos sin error

#### Scenario: Bultos con decimales
- **WHEN** un artículo tiene 1,5 BULTOS en una tienda
- **THEN** el máximo de cajas para esa tienda se calcula con 1,5 bultos

### Requirement: Fichero de salida PRUEBAESTANDAR.xlsx
Al terminar correctamente, el sistema SHALL guardar la base del TIPO como `PRUEBAESTANDAR.xlsx` en la carpeta del fichero SALALM. En ese fichero:
- cada celda ELECCIÓN de un artículo seleccionado MUST contener un número entero ≥ 1 (tipo numérico, no texto);
- cada celda ELECCIÓN de un artículo no seleccionado MUST quedar vacía;
- el resto de celdas MUST tener los valores de la base del TIPO: CODIGO, PESO, Volumen, UNIxCAJA, y BULTOS y LINEAS de cada tienda. No hay columna TIPO.

Ni el FICHERO BASE ni los ficheros de entrada MUST modificarse nunca.

#### Scenario: Salida generada
- **WHEN** el proceso termina sin errores con el SALALM `C:\datos\salalm.xlsx` y el TIPO ALTA ROTACIÓN
- **THEN** existe `C:\datos\PRUEBAESTANDAR.xlsx` con CODIGO, PESO, Volumen y UNIxCAJA en A–D, las tiendas desde la columna E y las columnas ELECCIÓN rellenas para los artículos de ALTA ROTACIÓN

#### Scenario: Valores previos en ELECCIÓN
- **WHEN** un artículo no se selecciona en una tienda
- **THEN** su celda ELECCIÓN de esa tienda queda vacía en PRUEBAESTANDAR.xlsx

#### Scenario: Fichero de salida abierto en Excel
- **WHEN** PRUEBAESTANDAR.xlsx está abierto en Excel y no se puede escribir
- **THEN** el sistema muestra un error pidiendo cerrar el fichero y no pierde el cálculo hecho hasta volver a intentarlo o cancelar

### Requirement: Fichero de salida REPARTOESTANDAR.xls
Al terminar correctamente, además de PRUEBAESTANDAR.xlsx, el sistema SHALL guardar `REPARTOESTANDAR.xls` en la carpeta del fichero SALALM, con el formato de la plantilla del programa de importación:
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
