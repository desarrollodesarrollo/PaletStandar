# Tasks

## 1. Preparación (sin tocar PRUEBAESTANDAR)

- [x] 1.1 Crear el paquete `generabase/` (`__init__`, `__main__`, `columnas`, `lectura`, `access`, `salalm`, `fichero_base`, `proceso`, `gui`), `GENERABASE.pyw`, `tests_generabase/` y `requirements-generabase.txt` / `requirements-generabase-dev.txt`; añadir `tests_generabase` a `testpaths` de `pytest.ini` y `*.accdb`/`*.mdb` a `.gitignore`; verificar que `python -c "import generabase"` funciona, que `pytest` ejecuta ambas carpetas y que `git diff` no toca `pruebaestandar/`, `tests/`, `requirements*.txt` ni `compilar-exe.yml`
- [x] 1.2 Crear en `tests_generabase/conftest.py` generadores de SALALM, MAESTRO y MAESTRO DE CADUCIDAD sintéticos, y un sustituto de `AccessParser`; verificar con una prueba que se generan y releen

## 2. Lectura de entradas

- [x] 2.1 Implementar en `columnas.py` la búsqueda de columnas por encabezado (sin distinguir mayúsculas ni espacios) y la normalización `entero()` / `codigo_texto()`; verificar con pruebas de `"000010389"` → 10389, `273137.0` → 273137, `"ABC"` → None y `1` ↔ `"1"`
- [x] 2.2 Implementar la lectura de los 3 Excel con sus validaciones (columnas ausentes, CODIGO duplicado, numéricos en SALALM, C3CADU duplicado, MAARTI duplicado → aviso); verificar con una prueba por caso, incluida una columna extra y un orden de columnas distinto
- [x] 2.3 Implementar `access.leer_movimientos()` con access-parser: tabla MOVIMIENTOS, filas leídas = `number_of_rows`, columnas de igual longitud, columnas necesarias, ausencia de `Id` sin efecto, liberación de columnas no usadas y errores claros (tabla ausente con lista de tablas, fichero no válido); verificar con el sustituto de AccessParser
- [x] 2.4 Implementar el filtro de movimientos (PI, rangos 10081–10349 y 10399–10999, −10000, CAJAS = |MVCANM| ÷ MVUNCA, MVUNCA ≤ 0 y códigos no válidos fuera y contados) y los totales de control; verificar con pruebas de extremos 10080/10081/10349/10350/10398/10399/10999/11000 y un movimiento SI

## 3. SALALM FILTRADO

- [x] 3.1 Construir las 14 columnas (PESO ÷ 1000, VOLUMEN ÷ 1000, cruces con el MAESTRO y las caducidades, UBICACIÓN de 3 cifras, TIPO DE UBICACIÓN con «ALTA ROTACIÓN»); verificar con pruebas de 8000/12648 → 8/12,648, cruce `N` → 182 y los tramos 219/220/290/291/399/400/599/600
- [x] 3.2 Aplicar las exclusiones en el orden de la spec con recuento por regla, mantener caducidades vacías (MACADU N y ausentes del MAESTRO) y ordenar por CAJAS desc. y CODIGO asc.; verificar con pruebas de 85 fuera y 92 dentro, `"   00000"` fuera, secciones y bajas sin distinguir mayúsculas, y un empate de CAJAS
- [x] 3.3 Exportar `SALALM FILTRADO.xlsx` (encabezados, tipos numéricos, celdas vacías, guardado por fichero temporal); verificar releyendo el fichero en una prueba

## 4. FICHERO BASE

- [x] 4.1 Implementar el nº de artículos (entero ≥ 1; aviso si supera las filas disponibles) y la selección del top N; verificar con pruebas de `mil`, `0`, `2,5` y N mayor que el total
- [x] 4.2 Agregar BULTOS (suma, int si es entero) y LINEAS por artículo y tienda, con tiendas ascendentes de todos los movimientos usados; verificar con la prueba «16 y 8 unidades con MVUNCA 16 → 1,5 bultos y 2 líneas» y con una tienda sin movimientos de los N artículos
- [x] 4.3 Escribir la hoja `TODOS` con la estructura y los anchos de la plantilla y la comprobación de totales antes de guardar; verificar releyendo filas 1–3, último bloque, anchos y que una agregación manipulada no se guarda

## 5. Proceso e interfaz

- [x] 5.1 Implementar `proceso.py` (lectura → SALALM FILTRADO → FICHERO BASE → guardado reintentable sin releer) y el resumen (rutas, recuentos por regla, artículos y tiendas, totales de control, avisos); verificar con una prueba de extremo a extremo con datos sintéticos y otra de reintento ante `PermissionError`
- [x] 5.2 Implementar la ventana `GENERABASE` (4 selectores, el del Access con `*.accdb *.mdb`; nº de artículos; Ejecutar; fase del proceso; confirmación única de sobrescritura; Reintentar; resumen); verificar con pruebas de interfaz bajo Xvfb y una captura

## 6. Ejecutable, aceptación y documentación

- [x] 6.1 Añadir `.github/workflows/compilar-generabase-exe.yml` (pruebas de GENERABASE, PyInstaller `GENERABASE.exe`, comprobación de la ventana, artefacto `GENERABASE-windows`) sin modificar `compilar-exe.yml`; verificar que la compilación en GitHub pasa y que no se lanza la de PRUEBAESTANDAR
- [x] 6.2 Aceptación con los ficheros de ejemplo (fuera del repo) y N = 1000: 7.808 filas en SALALM FILTRADO con las exclusiones de la spec, 124 tiendas, totales de control, lectura del Access idéntica a mdbtools y BULTOS/LINEAS de 5 artículos comprobados contra el CSV de mdbtools; verificar que todo cuadra y que tarda menos de 60 s
- [x] 6.3 Añadir al `README.md` una sección GENERABASE (entradas, salidas, reglas, totales de control, incompatibilidad actual con PRUEBAESTANDAR); verificar que las secciones de PRUEBAESTANDAR no cambian
- [x] 6.4 Ejecutar todas las pruebas (las de PRUEBAESTANDAR incluidas, que deben seguir en verde) y `graphify update .`; verificar que pasan
- [ ] 6.5 Pedir al usuario que ejecute GENERABASE con el Access real (417 MB) y comunique el tiempo, si la memoria aguanta y si los totales de control coinciden con una consulta de totales en Access; verificar con su confirmación
