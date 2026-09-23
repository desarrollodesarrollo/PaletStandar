# interfaz-grafica Specification

## Purpose

Ofrecer una ventana sencilla de PRUEBAESTANDAR para seleccionar los dos Excel de entrada, escribir el nº de días, ejecutar el cálculo y ver el resultado o los errores sin usar la consola.

## Requirements

### Requirement: Ventana principal
Al iniciar PRUEBAESTANDAR, el sistema SHALL abrir una ventana titulada `PRUEBAESTANDAR` con:
- un botón para seleccionar el FICHERO BASE y el nombre del fichero elegido,
- un botón para seleccionar la TABLA DE TIENDAS Y MEDIOS y el nombre del fichero elegido,
- una caja de texto para el nº de días de datos,
- un botón `Ejecutar`.

Los selectores de fichero SHALL mostrar por defecto sólo ficheros `.xlsx`. Todos los textos MUST estar en español.

#### Scenario: Apertura del programa
- **WHEN** el usuario inicia PRUEBAESTANDAR
- **THEN** ve la ventana con los dos selectores de fichero, la caja de días y el botón Ejecutar

### Requirement: Validación de datos antes de ejecutar
Al pulsar `Ejecutar`, el sistema MUST comprobar que se han elegido ambos ficheros y que el nº de días es un entero ≥ 1. Si falta algo, SHALL mostrar un mensaje que indique qué falta y no iniciar el cálculo.

#### Scenario: Falta la tabla de tiendas
- **WHEN** el usuario pulsa Ejecutar sin haber elegido la tabla de tiendas
- **THEN** ve un mensaje pidiendo seleccionar la TABLA DE TIENDAS Y MEDIOS

#### Scenario: Días no numéricos
- **WHEN** el usuario escribe `cinco` en la caja de días y pulsa Ejecutar
- **THEN** ve un mensaje pidiendo un nº entero de días mayor que 0

### Requirement: Ejecución y confirmación de sobrescritura
Durante el cálculo, la ventana MUST seguir respondiendo, el botón `Ejecutar` MUST estar desactivado y SHALL mostrarse que el proceso está en curso. Si `PRUEBAESTANDAR.xlsx` ya existe en la carpeta del fichero base, el sistema MUST pedir confirmación antes de sobrescribirlo; si el usuario no confirma, no se guarda nada.

#### Scenario: Proceso en curso
- **WHEN** el cálculo está en marcha
- **THEN** el botón Ejecutar está desactivado y se muestra un indicador de progreso

#### Scenario: Salida ya existente
- **WHEN** ya existe PRUEBAESTANDAR.xlsx y el usuario responde `No` a la confirmación
- **THEN** el fichero existente no cambia y la ventana vuelve a quedar lista

### Requirement: Resultado y errores
Al terminar correctamente, el sistema SHALL mostrar la ruta del fichero generado y un resumen con: nº de tiendas procesadas, nº de tiendas sin selección, total de cajas seleccionadas y la lista de avisos (por ejemplo, artículos sin peso o volumen válidos). Si ocurre un error de validación o de escritura, SHALL mostrarse un mensaje en español comprensible, sin trazas técnicas, y la ventana MUST quedar lista para corregir y volver a ejecutar.

#### Scenario: Ejecución correcta
- **WHEN** el proceso termina sin errores
- **THEN** el usuario ve la ruta de PRUEBAESTANDAR.xlsx y el resumen de tiendas, cajas y avisos

#### Scenario: Error de validación
- **WHEN** faltan tiendas del fichero base en la tabla
- **THEN** el usuario ve un mensaje con las tiendas que faltan y puede elegir otra tabla y ejecutar de nuevo

### Requirement: Tiempo de respuesta
Con un fichero base de 650 artículos y 180 tiendas, el proceso completo (lectura, cálculo, verificación y guardado) MUST terminar en menos de 60 segundos en un PC de oficina actual.

#### Scenario: Fichero grande
- **WHEN** el usuario ejecuta con 650 artículos y 180 tiendas
- **THEN** obtiene PRUEBAESTANDAR.xlsx en menos de 60 segundos
