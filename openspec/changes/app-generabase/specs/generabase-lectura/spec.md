# Spec Delta

## Purpose

Leer y validar los ficheros de entrada de GENERABASE (SALALM, MAESTRO, MAESTRO DE CADUCIDAD y el Access de MOVIMIENTOS), normalizar los códigos para poder cruzarlos y garantizar que el Access se ha leído completo y correctamente.

## ADDED Requirements

### Requirement: Columnas por nombre de encabezado
El sistema SHALL localizar cada columna por su nombre de encabezado en la primera fila de la primera hoja de cada Excel, y en la definición de la tabla del Access, sin distinguir mayúsculas ni espacios extremos. La posición de la columna MUST NOT importar: el fichero puede tener columnas adicionales o en otro orden, como la columna de autonumeración `Id` del Access, que puede existir o no.

Columnas necesarias:
- SALALM: `CODIGO`, `CAJAS`, `DESCRIPC`, `DESSEC`, `BAJA`, `UNIXCAJA`, `RADUBICA`, `PESO`, `VOLUMEN`.
- MAESTRO: `MAARTI`, `MACADU`, `MACLCA`.
- MAESTRO DE CADUCIDAD: `C3CADU`, `C3UTIL`, `C3COME`.
- Access, tabla `MOVIMIENTOS`: `MVARTI`, `MVTMOV`, `MVDESM`, `MVCANM`, `MVUNCA`.

Si falta alguna, el sistema MUST detenerse sin generar ficheros e indicar qué columna falta y en qué fichero.

#### Scenario: Access sin columna de autonumeración
- **WHEN** la tabla MOVIMIENTOS no tiene la columna `Id`
- **THEN** el sistema la lee igual que si la tuviera

#### Scenario: Columna necesaria ausente
- **WHEN** el MAESTRO no tiene la columna `MACLCA`
- **THEN** el sistema muestra «Falta la columna MACLCA en el fichero MAESTRO» y no genera ningún fichero

### Requirement: Normalización de códigos
Los códigos de artículo (`CODIGO`, `MAARTI`, `MVARTI`) y de tienda (`MVDESM`) SHALL convertirse a número entero aunque vengan como texto o con ceros a la izquierda (por ejemplo `"000010389"` → 10389, `"8682851"` → 8682851). Los códigos de caducidad (`MACLCA`, `C3CADU`) SHALL compararse como texto sin espacios extremos, de modo que `1` y `"1"` coincidan. Un código de artículo o de tienda que no sea un entero MUST contarse y mostrarse en los avisos; esa fila no se usa.

#### Scenario: Código de tienda con ceros
- **WHEN** MVDESM vale `"000010389"`
- **THEN** la tienda se trata como 10389 antes de filtrar y como 389 en el FICHERO BASE

#### Scenario: Código no numérico
- **WHEN** una fila del Access tiene MVARTI `"ABC"`
- **THEN** esa fila no se usa y el resumen avisa de 1 fila con código de artículo no válido

### Requirement: Lectura del Access sin controladores
El sistema SHALL leer la tabla `MOVIMIENTOS` de ficheros `.accdb` y `.mdb` sin necesitar el controlador de Access de Microsoft ni Office. Si el fichero no es una base de Access válida, está protegido con contraseña o no contiene la tabla `MOVIMIENTOS`, el sistema MUST detenerse con un mensaje que lo explique, listando las tablas encontradas cuando sea posible.

#### Scenario: Lectura de la copia de ejemplo
- **WHEN** se lee `MOVIMIENTOS_CLAUDE.accdb`
- **THEN** se obtienen 52.150 filas con 40 columnas, idénticas a las que lee una herramienta independiente (mdbtools)

#### Scenario: Tabla con otro nombre
- **WHEN** el Access sólo contiene la tabla `MOVS_2025`
- **THEN** el sistema muestra que no encuentra la tabla MOVIMIENTOS y que la base contiene `MOVS_2025`

### Requirement: Comprobaciones de la lectura del Access
En cada ejecución, el sistema MUST verificar:
- que el nº de filas leídas es igual al nº de registros que la propia tabla declara;
- que todas las columnas leídas tienen el mismo nº de valores;
- que `MVCANM` y `MVUNCA` son numéricos en todas las filas que se usan.

Si alguna comprobación falla, el sistema MUST detenerse sin generar ficheros y mostrar el detalle, por ejemplo «leídas 51.900 filas de 52.150 declaradas».

#### Scenario: Lectura completa
- **WHEN** la tabla declara 52.150 registros y se leen 52.150
- **THEN** el proceso continúa

#### Scenario: Lectura incompleta
- **WHEN** la tabla declara 52.150 registros y se leen 51.900
- **THEN** el sistema se detiene con un error que muestra las dos cifras y no genera ningún fichero

### Requirement: Totales de control del Access
Al terminar, el sistema SHALL mostrar los totales de lo leído del Access, para que el usuario pueda compararlos con una consulta de totales en Access:
- filas leídas y declaradas;
- filas con MVTMOV = «PI»;
- filas «PI» dentro de los rangos de tienda;
- nº de tiendas;
- nº de artículos distintos;
- suma de CAJAS (|MVCANM| ÷ MVUNCA);
- nº total de LINEAS;
- y, si existe la columna `MVFECI`, la fecha mínima y máxima.

#### Scenario: Totales de la copia de ejemplo
- **WHEN** se procesa la copia de ejemplo
- **THEN** el resumen muestra 52.150 filas leídas y declaradas, 51.835 filas PI, 38.947 dentro de rangos y 124 tiendas

### Requirement: Validación de valores de los Excel
El sistema MUST rechazar el proceso, con un mensaje que indique fichero, fila y columna, cuando en SALALM un `CODIGO` esté duplicado, o un `CAJAS`, `PESO`, `VOLUMEN` o `UNIXCAJA` no sea numérico; o cuando en el MAESTRO DE CADUCIDAD un `C3CADU` esté duplicado o un `C3UTIL` no sea numérico. Un `MAARTI` duplicado en el MAESTRO SHALL usar la primera aparición y mostrarse en los avisos.

#### Scenario: Código repetido en SALALM
- **WHEN** el código 273137 aparece dos veces en SALALM
- **THEN** el sistema muestra un error con las dos filas y no genera ningún fichero
