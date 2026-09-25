# Tasks

## 1. Llenado máximo del 96 %

- [ ] 1.1 Añadir `LLENADO_MAXIMO = Fraction(96, 100)` en `modelo.py` y aplicarlo en `Medio.peso_max` y `Medio.volumen_max`; verificar con pruebas que PALET 875/1300 da 840 kg / 1248 L y CARRO 475/600 da 912 kg / 1152 L, y que la densidad no cambia
- [ ] 1.2 Hacer que `verificacion.py` recalcule los límites del 96 % a partir de `peso_unitario`, `volumen_unitario`, `n_medios` y la constante, sin usar `peso_max`/`volumen_max`; verificar con una prueba que rechaza 1290 L en un PALET y acepta 800 kg / 1240 L
- [ ] 1.3 Ajustar las pruebas de selección y de proceso existentes a la nueva capacidad y añadir un caso que cabía al 100 % y ya no cabe; verificar que `pytest` pasa completo

## 2. Columna UNIxCAJA en el fichero base

- [ ] 2.1 Añadir `unidades_caja` a `Articulo` y leerlo de la columna D en `lectura.py`, exigiendo D2 = `UNIxCAJA` y valores enteros ≥ 1 (se admite `18.0` o `"18"`); verificar con pruebas que el error de encabezado cita la celda D2 y los de valor citan fila y columna D (vacío, 0, -2, 2,5, abc)
- [ ] 2.2 Actualizar el generador `tests/conftest.py` para que escriba `UNIxCAJA` en la columna D y adaptar las pruebas de lectura existentes; verificar que todas pasan

## 3. Fichero REPARTOESTANDAR.xls

- [ ] 3.1 Añadir `xlwt>=1.3` a `requirements.txt` y `xlrd>=2` a `requirements-dev.txt`, y crear `pruebaestandar/reparto.py` con los estilos de la plantilla (A1, códigos de tienda, códigos de artículo, datos, anchos 2304/1024, alto 315, hojas Hoja1–Hoja3); verificar con `pip install -r requirements-dev.txt` que se instalan
- [ ] 3.2 Implementar `construir_reparto()`: `Código` en A1, tiendas en la fila 1 como números en el orden del fichero base, un artículo por fila (también los no elegidos) y ELECCIÓN × UNIxCAJA o celda vacía; verificar releyendo con xlrd que la tienda 82 con 3 cajas del artículo 2101538 (UNIxCAJA 18) da 54 y que las no elegidas están vacías
- [ ] 3.3 Añadir la prueba de formato que compara, con xlrd, BIFF8, las hojas, y la fuente, tamaño, negrita, bordes, relleno y formato numérico de A1, B1, A2 y B2, además de anchos y alto de fila, con los valores medidos en la plantilla; verificar que pasa
- [ ] 3.4 Rechazar antes de calcular un fichero base con más de 255 tiendas, con un mensaje que lo explique; verificar con una prueba de 300 tiendas que no se genera ningún fichero

## 4. Proceso, verificación y guardado

- [ ] 4.1 Extender la comprobación final para que verifique que cada valor del reparto es ELECCIÓN × UNIxCAJA y que no se guarda ningún fichero si algo falla; verificar con una prueba que manipula el reparto y otra con exceso sobre el 96 %
- [ ] 4.2 Hacer que `proceso.calcular()` construya los dos libros y `Calculo.guardar()` escriba PRUEBAESTANDAR.xlsx y REPARTOESTANDAR.xls, reintentando los dos si falla uno; añadir `ruta_reparto` y `total_unidades` al `Resumen`; verificar con pruebas de extremo a extremo y de reintento con REPARTOESTANDAR.xls bloqueado
- [ ] 4.3 Ampliar la prueba de rendimiento 650 × 180 para que incluya el `.xls`; verificar que tarda menos de 60 s

## 5. Interfaz

- [ ] 5.1 Pedir una única confirmación de sobrescritura cuando exista cualquiera de los dos ficheros, nombrando los que existen, y mostrar al terminar las dos rutas y el total de unidades; verificar con las pruebas de interfaz bajo Xvfb (incluido "sólo existe REPARTOESTANDAR.xls → No → no se genera nada") y con una captura de la ventana

## 6. Aceptación y documentación

- [ ] 6.1 Ejecutar con `FICHERO_BASE_NUEVO.xlsx` y una tabla de tiendas con los códigos nuevos para 1, 5 y 20 días; verificar que las 180 tiendas pasan la comprobación, que el llenado máximo es ≤ 96 % y que REPARTOESTANDAR.xls = PRUEBAESTANDAR × UNIxCAJA en todas las celdas
- [ ] 6.2 Actualizar `README.md` (columna UNIxCAJA, margen del 96 %, REPARTOESTANDAR.xls, códigos de tienda que deben coincidir en los dos ficheros) y el `Purpose` de la spec principal `ficheros-excel` para mencionar REPARTOESTANDAR.xls; verificar leyendo ambos
- [ ] 6.3 Ejecutar `pytest` completo, `graphify update .` y la compilación del `.exe` en GitHub Actions; verificar que todo pasa y entregar el enlace del nuevo zip
- [ ] 6.4 Pedir al usuario que importe un REPARTOESTANDAR.xls real en su programa y confirme que lo acepta; verificar con su confirmación
