# Proposal

## Why

Hoy la composición de los medios (palets y carros) de cada tienda se decide a mano sobre un Excel de 180 tiendas × cientos de artículos, lo que es lento y propenso a errores de peso, volumen y densidad. PRUEBAESTANDAR automatiza esa elección: a partir del histórico de salidas de cada tienda y de las dimensiones de su medio, rellena las columnas ELECCIÓN con un número entero de cajas por artículo que respete siempre las restricciones físicas y priorice los artículos con más líneas de pedido.

## What Changes

- Nuevo programa de escritorio en Python, **PRUEBAESTANDAR**, con una ventana gráfica sencilla que permite:
  - seleccionar el FICHERO BASE (.xlsx),
  - seleccionar la TABLA DE TIENDAS Y MEDIOS (.xlsx),
  - escribir el nº de días de datos del fichero base,
  - ejecutar y obtener el resultado.
- Lectura y validación de ambos ficheros con la estructura observada en los ejemplos: fichero base con doble encabezado (fila 1 = código de tienda, fila 2 = BULTOS / LINEAS / ELECCIÓN) repetido en bloques de 3 columnas desde la columna E; tabla de tiendas con TIENDA, TIPO DE MEDIO, PESO MAX, VOLUMEN MÁX y DENSIDAD.
- Algoritmo de selección por tienda, con reparto de cajas proporcional a las líneas de pedido:
  - máximo de cajas por artículo = ⌈BULTOS / nº de días⌉;
  - nunca selecciona artículos sin salida de bultos en esa tienda;
  - capacidad = 1 medio si es PALET, 2 medios si es CARRO;
  - nunca supera el peso ni el volumen máximos, y la densidad de la selección queda por debajo de la del medio;
  - las cajas se asignan de una en una: cada caja siguiente va al artículo con mayor índice LÍNEAS / (cajas ya asignadas + 1) cuya caja todavía cabe (método de "cocientes" tipo D'Hondt). Así los artículos con más líneas entran antes y reciben más cajas, los de menos líneas reciben menos (o ninguna), y cuando una caja no cabe se prueba la siguiente, aprovechando el hueco con más variedad;
  - el proceso continúa hasta que ninguna caja más cabe o todos los artículos alcanzan su máximo;
  - sólo cajas enteras.
- Motivo del reparto proporcional: con los datos de ejemplo, en 174 de 180 tiendas ni siquiera cabe 1 caja de cada artículo con salida, así que un criterio de "1 caja para todos primero" dejaría casi todo a 1 caja y no respetaría la regla "más líneas → más bultos".
- Fichero de salida **PRUEBAESTANDAR.xlsx**, copia del fichero base con todas las columnas ELECCIÓN rellenas (vacías donde no se elige nada); el fichero original nunca se sobrescribe.
- Resumen final por pantalla (tiendas procesadas, avisos) para que el usuario pueda comprobar el resultado.

## Capabilities

### New Capabilities
- `ficheros-excel`: lectura y validación del fichero base y de la tabla de tiendas y medios, y escritura del fichero de salida PRUEBAESTANDAR.xlsx conservando el formato del fichero base.
- `seleccion-bultos`: reglas de selección de artículos y nº de cajas por tienda (máximos por días, capacidad del medio, peso, volumen, densidad, prioridad por líneas, cajas enteras).
- `interfaz-grafica`: ventana para elegir los dos ficheros, introducir el nº de días, lanzar el proceso y ver el resultado o los errores.

### Modified Capabilities
<!-- Ninguna: el proyecto no tiene especificaciones previas. -->

## Impact

- Código nuevo en el repositorio (proyecto hoy vacío salvo la configuración de OpenSpec/Claude): paquete Python del programa, pruebas automáticas y ficheros de ejemplo para las pruebas.
- Dependencias: Python 3.10+, `openpyxl` para leer/escribir Excel; `tkinter` (incluido con Python) para la ventana; `pytest` sólo para desarrollo.
- Sin impacto en otros sistemas: el programa trabaja sólo con ficheros locales.
