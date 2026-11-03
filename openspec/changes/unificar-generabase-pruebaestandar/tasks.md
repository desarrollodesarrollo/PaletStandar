# Tasks

## 1. Recuento de días en el Access (generabase, aditivo)

- [x] 1.1 En `generabase/access.filtrar`, rellenar estos campos en el mismo bucle, sobre todas las filas PI y antes del filtro de tienda: `fechas_pi` (MVFECI distintas no vacías), `pi_sin_fecha` y el aviso correspondiente. Añadir las propiedades `dias_pi`, `fecha_pi_min` y `fecha_pi_max`. Verificar con una prueba nueva en `tests_generabase/test_access.py` que:
  - las fechas PI 20251001, 20251001, 20251002, 20251006 y una PS con 20251003 dan 3;
  - una PI de la tienda 10350 cuenta;
  - una PI sin fecha no cuenta y genera aviso.
- [x] 1.2 Extraer `generabase.proceso.calcular_datos`, que devuelve también `elegidos`, `tiendas`, `agregado` y `usados`. `calcular` debe seguir dando el mismo resultado. Verificar que `pytest tests_generabase` pasa sin modificar ninguna prueba existente.

## 2. Cálculo de PRUEBAESTANDAR desde un libro en memoria

- [x] 2.1 Dividir `pruebaestandar/proceso.calcular` en `calcular_desde_libro(libro, ruta_tabla, dias, destino, destino_reparto)` y la envoltura actual. Verificar que `pytest tests` pasa sin cambios en las pruebas existentes.

## 3. Flujo integrado (`pruebaestandar/integrado.py`)

- [x] 3.1 Definir `TIPOS` y `filtrar_tipo(elegidos, tipo)`, que compara sin distinguir mayúsculas, tildes ni espacios y mantiene el orden. Si no hay ningún artículo del TIPO, lanza un error que nombra el TIPO y N. Verificar con pruebas que comprueben:
  - el filtrado y el orden;
  - «Alta rotacion» es equivalente a ALTA ROTACIÓN;
  - el error sin artículos.
- [x] 3.2 Implementar `construir_base_tipo(elegidos_tipo, tiendas, agregado)`: `construir_libro`, después `delete_cols(2)` y después la reasignación de anchos. Verificar con una prueba que:
  - la fila 2 es `CODIGO, PESO (Kg), Volumen (L), UNIxCAJA, BULTOS, LINEAS, ELECCIÓN…`;
  - las tiendas empiezan en la columna E y los valores están desplazados una columna respecto al FICHERO BASE;
  - `pruebaestandar.lectura.extraer_datos_base` la lee sin error, con BULTOS decimales (1,5).
- [x] 3.3 Implementar `verificar_base_tipo(libro_tipo, libro_base, tipo)`, comprobación cruzada celda a celda contra la hoja TODOS. Verificar con una prueba que pasa con una base correcta y que falla si se altera un BULTOS o se desplaza una columna.
- [x] 3.4 Implementar `ABREVIATURAS` (AR / DR / AL) y `rutas_salida(ruta_salalm, tipo, fecha)`. Verificar con una prueba que, para el 03/11/2026, la carpeta `C:\datos` y ALTA ROTACIÓN, devuelve `SALALM FILTRADO_20261103.xlsx`, `FICHERO BASE_20261103.xlsx`, `PRUEBAESTANDAR_AR_20261103.xlsx` y `REPARTOESTANDAR_AR_20261103.xls`. Con DROGUERÍA debe dar `_DR_` y con ALIMENTACIÓN `_AL_`. Verificar también que `generabase.proceso.rutas_salida` y `pruebaestandar.proceso.rutas_salida` siguen devolviendo los nombres sin fecha.
- [x] 3.5 Implementar `Datos`, `clave_entradas(rutas, n)` (ruta resuelta, `mtime_ns`, tamaño y N) y `preparar(...)`. Verificar con una prueba que la clave cambia al modificar un fichero o N y no cambia si nada cambia.
- [x] 3.6 Implementar `calcular_tipo(datos, tipo, ruta_tabla, fecha, progreso)`: filtro, comprobación de `dias_pi ≥ 1`, base del TIPO, verificación cruzada y `calcular_desde_libro` con `dias_pi`. Debe devolver un `CalculoIntegrado`, cuyo método `guardar()` guarda los 4 ficheros en la carpeta del SALALM con los nombres de `rutas_salida`, y un resumen combinado. Verificar con una prueba de extremo a extremo con los ficheros sintéticos de `tests_generabase/apoyo.py` y una tabla de medios. La prueba debe comprobar:
  - que existen exactamente los 4 ficheros con TIPO y fecha en el nombre, con una fecha fija en la prueba;
  - que el FICHERO BASE es igual al que genera `generabase.proceso.ejecutar`;
  - que PRUEBAESTANDAR tiene el formato antiguo, sólo los artículos del TIPO y las ELECCIÓN verificadas;
  - que REPARTOESTANDAR (leído con xlrd) es igual a ELECCIÓN × UNIxCAJA;
  - que se usan los días contados.
- [x] 3.7 Verificar con pruebas que:
  - con días = 0, el error no deja ningún fichero;
  - con una tienda que falta en la tabla, no se guarda ninguno de los 4;
  - un `PermissionError` en PRUEBAESTANDAR permite reintentar sin volver a llamar a `access.leer_movimientos` y con los mismos nombres;
  - cambiar el TIPO con el mismo `Datos` y la misma fecha no relee nada, da un FICHERO BASE idéntico y no toca los ficheros del palet del TIPO anterior.
- [x] 3.8 Implementar `ResumenIntegrado.texto()`, que muestra:
  - las 4 rutas;
  - si se han reutilizado los datos;
  - el bloque de GENERABASE;
  - «Nº de días de datos (MVFECI distintos con MVTMOV = PI): d · fechas: …»;
  - «TIPO: k artículos de los N del FICHERO BASE»;
  - tiendas procesadas, tiendas sin selección, cajas y unidades;
  - los avisos.

  Verificar los textos con una prueba.

## 4. Ventana PRUEBAESTANDAR unificada

- [x] 4.1 Rehacer `pruebaestandar/gui.py`:
  - 5 selectores (`ENTRADAS`); el del Access filtra `*.accdb *.mdb`;
  - la caja del nº de artículos;
  - el Combobox de TIPO en solo lectura y vacío;
  - sin caja de días;
  - el botón Ejecutar, la barra de progreso, la etiqueta de fase y el texto del resumen.

  Verificar con `xvfb-run pytest tests/test_gui.py` que la ventana se abre con esos controles.
- [x] 4.2 Validar en este orden: los ficheros, después N y después TIPO. Pedir una única confirmación con los nombres de los ficheros existentes entre los 4. Verificar con pruebas de GUI estos casos:
  - falta la tabla;
  - N = «mil»;
  - falta el TIPO;
  - de los 4 ficheros sólo existe `REPARTOESTANDAR_AR_<hoy>.xls`, la confirmación nombra sólo ese, se responde No y no se genera nada;
  - existen los ficheros del palet de DR del mismo día y se ejecuta AR: no se pregunta por ellos.
- [x] 4.3 Implementar la ejecución en un hilo con caché de `Datos` por clave. La fecha (`date.today()`) se fija al pulsar Ejecutar y es la que se usa en la confirmación y el guardado. Implementar también el reintento de guardado y la presentación del resumen y de los errores sin traza. Verificar con pruebas de GUI que:
  - una ejecución correcta genera los 4 ficheros;
  - una segunda ejecución con otro TIPO no llama a `access.leer_movimientos` y el resumen indica que se han reutilizado los datos;
  - el reintento tras un `PermissionError` funciona;
  - un Access inválido muestra el error y deja la ventana lista.

## 5. Empaquetado, documentación y comprobación final

- [x] 5.1 Añadir `access-parser==0.0.6` a `requirements.txt` y `generabase/**` a los `paths` de `.github/workflows/compilar-exe.yml`. Verificar que en un entorno nuevo `pip install -r requirements-dev.txt` instala todo y que `python -m pytest -q` pasa (`tests` y `tests_generabase`).
- [x] 5.2 Actualizar la sección PRUEBAESTANDAR del `README.md`: entradas, TIPO, días automáticos, 4 salidas con TIPO (AR/DR/AL) y fecha en el nombre y reutilización al cambiar de TIPO. La sección de GENERABASE se mantiene. Verificar releyendo que no queda ninguna mención a escribir los días a mano.
- [x] 5.3 Hacer push y comprobar que el workflow «Compilar PRUEBAESTANDAR.exe» termina en verde, con la ventana PRUEBAESTANDAR abierta en el smoke check y el artefacto `PRUEBAESTANDAR-windows` disponible. Ejecutar `graphify update .`.
- [x] 5.4 Prueba del usuario con sus ficheros reales. Verificar con el usuario que:
  - una ejecución con ALTA ROTACIÓN genera los 4 ficheros;
  - una segunda con DROGUERÍA no relee el Access;
  - el nº de días coincide con su consulta en Access (valores distintos de MVFECI con MVTMOV = "PI");
  - los nombres llevan el TIPO (AR/DR/AL) y la fecha del día;
  - `REPARTOESTANDAR_<TIPO>_<fecha>.xls` se importa bien en su programa, aunque ya no se llame `REPARTOESTANDAR.xls`.

## 6. TIPO «TODOS»

- [x] 6.1 En `pruebaestandar/integrado.py`, añadir `TODOS` a `TIPOS` (al final) y `TD` a `ABREVIATURAS`. Con TODOS, `filtrar_tipo` devuelve todos los artículos y `verificar_base_tipo` compara todas las filas. El mensaje de «Elige el TIPO» debe listar los cuatro. Verificar con pruebas en `tests/test_integrado.py` que:
  - `filtrar_tipo(…, "todos")` devuelve todos en orden;
  - TODOS con el FICHERO BASE vacío da error;
  - `verificar_base_tipo` con TODOS pasa y detecta una alteración;
  - `rutas_salida(…, "TODOS", 03/11/2026)` da `PRUEBAESTANDAR_TD_20261103.xlsx` y `REPARTOESTANDAR_TD_20261103.xls`;
  - de extremo a extremo con TODOS y N = 3, PRUEBAESTANDAR y REPARTOESTANDAR tienen los 3 artículos del FICHERO BASE en su orden y el resumen dice `TODOS: 3 artículos de los 3 del FICHERO BASE`.
- [x] 6.2 Añadir TODOS al Combobox de la ventana (cuarta opción). Verificar con `xvfb-run pytest tests/test_gui.py` que:
  - las opciones son las cuatro en orden;
  - una ejecución con TODOS genera `PRUEBAESTANDAR_TD_<fecha>.xlsx` y `REPARTOESTANDAR_TD_<fecha>.xls`;
  - cambiar de un TIPO a TODOS no relee el Access.
- [x] 6.3 Actualizar el README (selector con TODOS, abreviatura TD). Verificar releyendo la sección PRUEBAESTANDAR.
- [ ] 6.4 Pasar todas las pruebas (`xvfb-run python -m pytest`), ejecutar `graphify update .`, hacer push y comprobar que «Compilar PRUEBAESTANDAR.exe» termina en verde con el artefacto disponible.
- [ ] 6.5 Prueba del usuario con TODOS y N = 1000. Verificar con el usuario que PRUEBAESTANDAR_TD y REPARTOESTANDAR_TD tienen los 1000 artículos y que el reparto se importa bien.
