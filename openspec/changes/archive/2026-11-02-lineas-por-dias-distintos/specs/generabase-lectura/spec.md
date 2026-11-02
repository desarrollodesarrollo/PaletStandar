# Spec Delta

## MODIFIED Requirements

### Requirement: Columnas por nombre de encabezado
El sistema SHALL localizar cada columna por su nombre de encabezado en la primera fila de la primera hoja de cada Excel, y en la definición de la tabla del Access, sin distinguir mayúsculas ni espacios extremos. La posición de la columna MUST NOT importar: el fichero puede tener columnas adicionales o en otro orden, como la columna de autonumeración `Id` del Access, que puede existir o no.

Columnas necesarias:
- SALALM: `CODIGO`, `CAJAS`, `DESCRIPC`, `DESSEC`, `BAJA`, `UNIXCAJA`, `RADUBICA`, `PESO`, `VOLUMEN`.
- MAESTRO: `MAARTI`, `MACADU`, `MACLCA`.
- MAESTRO DE CADUCIDAD: `C3CADU`, `C3UTIL`, `C3COME`.
- Access, tabla `MOVIMIENTOS`: `MVARTI`, `MVTMOV`, `MVDESM`, `MVCANM`, `MVUNCA`, `MVFECI`.

Si falta alguna, el sistema MUST detenerse sin generar ficheros e indicar qué columna falta y en qué fichero.

#### Scenario: Access sin columna de autonumeración
- **WHEN** la tabla MOVIMIENTOS no tiene la columna `Id`
- **THEN** el sistema la lee igual que si la tuviera

#### Scenario: Columna necesaria ausente
- **WHEN** el MAESTRO no tiene la columna `MACLCA`
- **THEN** el sistema muestra «Falta la columna MACLCA en el fichero MAESTRO» y no genera ningún fichero

#### Scenario: Access sin fecha
- **WHEN** la tabla MOVIMIENTOS no tiene la columna `MVFECI`
- **THEN** el sistema muestra «Falta la columna MVFECI en la tabla MOVIMIENTOS del Access» y no genera ningún fichero

### Requirement: Comprobaciones de la lectura del Access
En cada ejecución, el sistema MUST verificar:
- que el nº de filas leídas es igual al nº de registros que la propia tabla declara;
- que todas las columnas leídas tienen el mismo nº de valores;
- que `MVCANM` y `MVUNCA` son numéricos en todas las filas que se usan;
- que `MVFECI` es una fecha numérica (AAAAMMDD) en todas las filas que se usan.

Si alguna comprobación falla, el sistema MUST detenerse sin generar ficheros y mostrar el detalle, por ejemplo «leídas 51.900 filas de 52.150 declaradas» o la fila del Access con MVFECI vacío.

#### Scenario: Lectura completa
- **WHEN** la tabla declara 52.150 registros y se leen 52.150
- **THEN** el proceso continúa

#### Scenario: Lectura incompleta
- **WHEN** la tabla declara 52.150 registros y se leen 51.900
- **THEN** el sistema se detiene con un error que muestra las dos cifras y no genera ningún fichero

#### Scenario: Movimiento usado sin fecha
- **WHEN** un movimiento PI de la tienda 10400 (dentro de los rangos) tiene MVFECI vacío
- **THEN** el sistema se detiene con un error que indica la fila del Access y que MVFECI no es una fecha válida, y no genera ningún fichero

#### Scenario: Movimiento no usado sin fecha
- **WHEN** un movimiento de tipo SI, o PI de la tienda 10378, tiene MVFECI vacío
- **THEN** el proceso continúa, porque esa fila no se usa

### Requirement: Totales de control del Access
Al terminar, el sistema SHALL mostrar los totales de lo leído del Access, para que el usuario pueda compararlos con una consulta de totales en Access:
- filas leídas y declaradas;
- filas con MVTMOV = «PI»;
- filas «PI» dentro de los rangos de tienda;
- nº de tiendas;
- nº de artículos distintos;
- suma de CAJAS (|MVCANM| ÷ MVUNCA);
- nº total de LINEAS (movimientos usados, es decir, filas del Access que se usan);
- nº de días distintos (valores distintos de MVFECI) y la fecha mínima y máxima de los movimientos usados.

#### Scenario: Totales de la copia de ejemplo
- **WHEN** se procesa la copia de ejemplo
- **THEN** el resumen muestra 52.150 filas leídas y declaradas, 51.835 filas PI, 38.947 dentro de rangos, 124 tiendas, 38.947 LINEAS y 1 día distinto (15/10/2025)
