# Spec Delta

## MODIFIED Requirements

### Requirement: Ejecución y confirmación de sobrescritura
Durante el cálculo, la ventana MUST seguir respondiendo, el botón `Ejecutar` MUST estar desactivado y SHALL mostrarse que el proceso está en curso. Si `PRUEBAESTANDAR.xlsx` o `REPARTOESTANDAR.xls` ya existen en la carpeta del fichero base, el sistema MUST pedir una única confirmación, que nombre los ficheros existentes, antes de sobrescribirlos; si el usuario no confirma, no se guarda nada.

#### Scenario: Proceso en curso
- **WHEN** el cálculo está en marcha
- **THEN** el botón Ejecutar está desactivado y se muestra un indicador de progreso

#### Scenario: Salida ya existente
- **WHEN** ya existe PRUEBAESTANDAR.xlsx y el usuario responde `No` a la confirmación
- **THEN** el fichero existente no cambia y la ventana vuelve a quedar lista

#### Scenario: Sólo existe el fichero de reparto
- **WHEN** sólo existe REPARTOESTANDAR.xls y el usuario responde `No` a la confirmación
- **THEN** no se genera ninguno de los dos ficheros y REPARTOESTANDAR.xls no cambia

### Requirement: Resultado y errores
Al terminar correctamente, el sistema SHALL mostrar las rutas de los dos ficheros generados (PRUEBAESTANDAR.xlsx y REPARTOESTANDAR.xls) y un resumen con: nº de tiendas procesadas, nº de tiendas sin selección, total de cajas seleccionadas, total de unidades y la lista de avisos (por ejemplo, artículos sin peso o volumen válidos). Si ocurre un error de validación o de escritura, SHALL mostrarse un mensaje en español comprensible, sin trazas técnicas, y la ventana MUST quedar lista para corregir y volver a ejecutar.

#### Scenario: Ejecución correcta
- **WHEN** el proceso termina sin errores
- **THEN** el usuario ve las rutas de PRUEBAESTANDAR.xlsx y REPARTOESTANDAR.xls y el resumen de tiendas, cajas, unidades y avisos

#### Scenario: Error de validación
- **WHEN** faltan tiendas del fichero base en la tabla
- **THEN** el usuario ve un mensaje con las tiendas que faltan y puede elegir otra tabla y ejecutar de nuevo

### Requirement: Tiempo de respuesta
Con un fichero base de 650 artículos y 180 tiendas, el proceso completo (lectura, cálculo, verificación y guardado de los dos ficheros) MUST terminar en menos de 60 segundos en un PC de oficina actual.

#### Scenario: Fichero grande
- **WHEN** el usuario ejecuta con 650 artículos y 180 tiendas
- **THEN** obtiene PRUEBAESTANDAR.xlsx y REPARTOESTANDAR.xls en menos de 60 segundos
