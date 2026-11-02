# Tasks

## 1. Lectura: MVFECI obligatoria y fecha en cada movimiento

- [x] 1.1 En `generabase/access.py`, añadir `MVFECI` a `COLUMNAS` (quitar `OPCIONAL_FECHA`), guardar los movimientos usados como `(artículo, tienda, cajas, fecha)`, detenerse si un movimiento usado tiene MVFECI vacío o no numérico (indicando fila, artículo y tienda), y añadir la propiedad `dias`; verificar con pruebas de Access sin MVFECI, movimiento PI en rango sin fecha (error), movimiento SI o fuera de rango sin fecha (continúa) y `dias`/`fecha_min`/`fecha_max`
- [x] 1.2 Adaptar las pruebas existentes de `tests_generabase/test_lectura.py` a la tupla con fecha; verificar que pasan

## 2. FICHERO BASE: LINEAS por días distintos

- [x] 2.1 En `generabase/fichero_base.py`, calcular LINEAS como nº de fechas distintas por artículo y tienda en `agregar()` y recalcular las LINEAS esperadas con el conjunto `(artículo, tienda, fecha)` en `verificar_totales()`; verificar con las pruebas «dos movimientos en fechas distintas → LINEAS 2», «tres movimientos, dos el mismo día → BULTOS 3, LINEAS 2» y que una agregación manipulada no pasa la comprobación
- [x] 2.2 Adaptar el resto de pruebas de `test_fichero_base.py` y la de extremo a extremo de `test_proceso.py` (los datos sintéticos con dos movimientos el mismo día en la tienda 81 pasan de LINEAS 2 a 1); verificar que pasan

## 3. Resumen, documentación y aceptación

- [x] 3.1 En `generabase/proceso.py`, mantener la etiqueta «LINEAS» en los totales de control y añadir «Días distintos» junto a las fechas (siempre visibles); verificar con la prueba de extremo a extremo y la de la ventana
- [x] 3.2 Actualizar la sección GENERABASE del `README.md` (LINEAS = días distintos por artículo y tienda, MVFECI obligatoria); verificar que la parte de PRUEBAESTANDAR no cambia
- [ ] 3.3 Ejecutar todas las pruebas (PRUEBAESTANDAR incluidas), `graphify update .` y la compilación del `.exe` de GENERABASE; verificar que pasan y que no se compila PRUEBAESTANDAR
- [ ] 3.4 Pedir al usuario que ejecute el nuevo `.exe` con su Access real y compruebe con una consulta en Access que el nº de días distintos y las LINEAS de un par de artículos y tiendas coinciden; verificar con su confirmación
