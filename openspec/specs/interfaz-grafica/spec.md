# interfaz-grafica Specification

## Purpose

Ofrecer una ventana sencilla de PRUEBAESTANDAR para seleccionar los ficheros de entrada (SALALM, MAESTRO, MAESTRO DE CADUCIDAD, MOVIMIENTOS y TABLA DE TIENDAS Y MEDIOS), indicar el nº de artículos y el TIPO de palet estándar, ejecutar el cálculo y ver el resultado o los errores sin usar la consola.

## Requirements

### Requirement: Ventana principal
Al iniciar PRUEBAESTANDAR, el sistema SHALL abrir una ventana titulada `PRUEBAESTANDAR` con:
- un selector, con el nombre del fichero elegido, para cada entrada:
  - SALALM (`.xlsx`),
  - MAESTRO (`.xlsx`),
  - MAESTRO DE CADUCIDAD (`.xlsx`),
  - MOVIMIENTOS (Access, `.accdb` o `.mdb`),
  - TABLA DE TIENDAS Y MEDIOS (`.xlsx`);
- debajo de los selectores del MAESTRO y del MAESTRO DE CADUCIDAD, una nota visible con el texto exacto `Filtrar para un solo almacén` (sin nada más). Es sólo una indicación: el programa no cambia cómo lee esos ficheros;
- una caja de texto para el nº de artículos del FICHERO BASE;
- un selector de TIPO de palet estándar con las opciones `ALTA ROTACIÓN`, `DROGUERÍA`, `ALIMENTACIÓN` y `TODOS`, en ese orden y sin ninguna elegida al abrir;
- un botón `Ejecutar`.

La ventana MUST NOT tener caja para el nº de días de datos, porque se calcula desde el Access. Todos los textos MUST estar en español.

#### Scenario: Apertura del programa
- **WHEN** el usuario inicia PRUEBAESTANDAR
- **THEN** ve los cinco selectores de fichero, la nota «Filtrar para un solo almacén» bajo el MAESTRO y el MAESTRO DE CADUCIDAD, la caja del nº de artículos, el selector de TIPO sin valor y con las cuatro opciones, el botón Ejecutar y ninguna caja de días

#### Scenario: Nota del MAESTRO y del MAESTRO DE CADUCIDAD
- **WHEN** el usuario abre PRUEBAESTANDAR
- **THEN** bajo el selector del MAESTRO y bajo el del MAESTRO DE CADUCIDAD lee `Filtrar para un solo almacén`, y bajo los demás selectores no aparece ninguna nota

### Requirement: Validación de datos antes de ejecutar
Al pulsar `Ejecutar`, el sistema MUST comprobar que:
- se han elegido los cinco ficheros,
- el nº de artículos es un entero ≥ 1,
- se ha elegido un TIPO.

Si falta algo, SHALL mostrar un mensaje que indique qué falta y no iniciar el proceso.

#### Scenario: Falta la tabla de tiendas
- **WHEN** el usuario pulsa Ejecutar sin haber elegido la tabla de tiendas
- **THEN** ve un mensaje pidiendo seleccionar la TABLA DE TIENDAS Y MEDIOS

#### Scenario: Días no numéricos
- **WHEN** el usuario pulsa Ejecutar
- **THEN** no se le pide ni se valida un nº de días escrito a mano, porque el nº de días se cuenta desde el Access

#### Scenario: Nº de artículos no válido
- **WHEN** el usuario escribe `mil` en la caja del nº de artículos y pulsa Ejecutar
- **THEN** ve un mensaje pidiendo un nº entero de artículos mayor que 0

#### Scenario: Falta el TIPO
- **WHEN** el usuario pulsa Ejecutar sin haber elegido TIPO
- **THEN** ve un mensaje pidiendo elegir el TIPO de palet estándar (ALTA ROTACIÓN, DROGUERÍA, ALIMENTACIÓN o TODOS)

### Requirement: Ejecución y confirmación de sobrescritura
Durante el proceso, la ventana MUST seguir respondiendo y el botón `Ejecutar` MUST estar desactivado. SHALL mostrarse la fase en curso, por ejemplo la lectura del Access, que puede tardar unos minutos.

Si alguno de estos ficheros ya existe en la carpeta del SALALM, el sistema MUST pedir una única confirmación antes de empezar, que nombre sólo los ficheros que ya existen:
- `SALALM FILTRADO_<AAAAMMDD>.xlsx`,
- `FICHERO BASE_<AAAAMMDD>.xlsx`,
- `PRUEBAESTANDAR_<TIPO>_<AAAAMMDD>.xlsx`,
- `REPARTOESTANDAR_<TIPO>_<AAAAMMDD>.xls`.

Estos nombres llevan el TIPO elegido y la fecha del momento de pulsar Ejecutar, según la capacidad `pruebaestandar-integrado`.

Si el usuario no confirma, no se genera ni se modifica ninguno.

#### Scenario: Proceso en curso
- **WHEN** el proceso está en marcha
- **THEN** el botón Ejecutar está desactivado y se muestran un indicador de progreso y la fase en curso

#### Scenario: Salida ya existente
- **WHEN** ya existe `PRUEBAESTANDAR_AR_20261103.xlsx`, el usuario ejecuta ALTA ROTACIÓN ese día y responde `No` a la confirmación
- **THEN** el fichero existente no cambia, no se genera ninguno de los otros tres y la ventana vuelve a quedar lista

#### Scenario: Sólo existe el fichero de reparto
- **WHEN** de los 4 ficheros de la ejecución sólo existe ya `REPARTOESTANDAR_AR_20261103.xls`
- **THEN** la confirmación nombra sólo ese fichero y, si el usuario responde `No`, no se genera ninguno de los cuatro ficheros

### Requirement: Resultado y errores
Al terminar correctamente, el sistema SHALL mostrar:
- las rutas de los cuatro ficheros generados;
- el TIPO elegido y el nº de artículos de ese TIPO frente a los del FICHERO BASE;
- el nº de días de datos contado en el Access (fechas MVFECI distintas de las filas PI), con la primera y la última fecha;
- los totales de control de GENERABASE;
- el resumen de PRUEBAESTANDAR: nº de tiendas procesadas, nº de tiendas sin selección, total de cajas seleccionadas y total de unidades;
- la lista de avisos.

Si se han reutilizado el FICHERO BASE y los días de la ejecución anterior, el resumen SHALL decirlo. Si ocurre un error de validación o de escritura, SHALL mostrarse un mensaje en español comprensible, sin trazas técnicas, y la ventana MUST quedar lista para corregir y volver a ejecutar.

#### Scenario: Ejecución correcta
- **WHEN** el proceso termina sin errores con el TIPO ALTA ROTACIÓN
- **THEN** el usuario ve las rutas de los cuatro ficheros (con `_AR_` y la fecha en los del palet), el TIPO y su nº de artículos, el nº de días contado y el resumen de tiendas, cajas, unidades y avisos

#### Scenario: Error de validación
- **WHEN** faltan tiendas del FICHERO BASE en la tabla
- **THEN** el usuario ve un mensaje con las tiendas que faltan y puede elegir otra tabla y ejecutar de nuevo sin volver a leer el Access

### Requirement: Tiempo de respuesta
Lo que más tarda es la lectura del Access, unos 10 minutos con el Access real en una carpeta de red. Sin contar esa lectura, el resto del proceso MUST terminar en menos de 60 segundos en un PC de oficina actual, con un FICHERO BASE de 1000 artículos y 180 tiendas. Ese resto incluye el filtrado, el FICHERO BASE, el cálculo del TIPO, la verificación y el guardado de los cuatro ficheros. Al cambiar sólo el TIPO o la tabla, la nueva ejecución MUST NOT volver a leer el Access.

#### Scenario: Fichero grande
- **WHEN** el usuario ejecuta con un FICHERO BASE de 1000 artículos y 180 tiendas ya leído en la ejecución anterior y cambia sólo el TIPO
- **THEN** obtiene los cuatro ficheros en menos de 60 segundos
