# generabase-interfaz Specification

## Purpose

Ofrecer una ventana sencilla de GENERABASE para elegir los cuatro ficheros de entrada y el nº de artículos, ejecutar el proceso y revisar el resultado, los avisos y los totales de control del Access.

## Requirements

### Requirement: Ventana principal
Al iniciar GENERABASE, el sistema SHALL abrir una ventana titulada `GENERABASE` con:
- un selector con el nombre del fichero elegido para cada entrada: SALALM (`.xlsx`), MAESTRO (`.xlsx`), MAESTRO DE CADUCIDAD (`.xlsx`) y MOVIMIENTOS (Access, `.accdb` o `.mdb`);
- una caja de texto para el nº de artículos del FICHERO BASE;
- un botón `Ejecutar`.

Todos los textos MUST estar en español.

#### Scenario: Apertura
- **WHEN** el usuario inicia GENERABASE
- **THEN** ve los cuatro selectores, la caja del nº de artículos y el botón Ejecutar

### Requirement: Validación antes de ejecutar
Al pulsar `Ejecutar`, el sistema MUST comprobar que se han elegido los cuatro ficheros y que el nº de artículos es un entero ≥ 1. Si falta algo, SHALL indicar qué falta y no iniciar el proceso. Si `SALALM FILTRADO.xlsx` o `FICHERO BASE.xlsx` ya existen en la carpeta del SALALM, MUST pedir una única confirmación que los nombre; si el usuario no confirma, no se genera nada.

#### Scenario: Falta el Access
- **WHEN** el usuario pulsa Ejecutar sin elegir el fichero de MOVIMIENTOS
- **THEN** ve un mensaje pidiendo seleccionar el fichero de MOVIMIENTOS (Access)

#### Scenario: Salidas ya existentes
- **WHEN** ya existe FICHERO BASE.xlsx y el usuario responde `No`
- **THEN** no se genera ningún fichero y FICHERO BASE.xlsx no cambia

### Requirement: Ejecución y resultado
Durante el proceso, la ventana MUST seguir respondiendo, con `Ejecutar` desactivado y un indicador de progreso que diga en qué fase está (leyendo el Access, cruzando datos, guardando). Al terminar, SHALL mostrar:
- las rutas de los dos ficheros generados;
- el nº de filas de SALALM FILTRADO y las excluidas por cada regla;
- el nº de artículos y de tiendas del FICHERO BASE;
- los totales de control del Access;
- los avisos.

Los errores SHALL mostrarse en español, sin trazas técnicas, y la ventana MUST quedar lista para corregir y volver a ejecutar. Si un fichero de salida está abierto en Excel, SHALL ofrecer `Reintentar` sin repetir la lectura.

#### Scenario: Ejecución correcta
- **WHEN** el proceso termina sin errores
- **THEN** el usuario ve las dos rutas, los recuentos, los totales de control del Access y los avisos

#### Scenario: Fichero de salida abierto
- **WHEN** FICHERO BASE.xlsx está abierto en Excel
- **THEN** el usuario ve un aviso para cerrarlo y, al pulsar Reintentar, se guarda sin volver a leer el Access

### Requirement: Tiempo de respuesta
Con la copia de ejemplo del Access (52.150 filas) y los Excel de ejemplo, el proceso completo MUST terminar en menos de 60 segundos. Con el Access real (unos 400 MB), el tiempo y la memoria SHALL medirse en la prueba de aceptación, con el objetivo de menos de 5 minutos en un PC de oficina con 8 GB de memoria.

#### Scenario: Datos de ejemplo
- **WHEN** se ejecuta con los ficheros de ejemplo y N = 1000
- **THEN** los dos ficheros se generan en menos de 60 segundos
