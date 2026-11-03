## Why

Hoy el trabajo se hace en dos pasos con dos programas. Primero GENERABASE genera el FICHERO BASE. Después PRUEBAESTANDAR elige los bultos de cada tienda. Pero PRUEBAESTANDAR no acepta el nuevo FICHERO BASE, porque la columna B (TIPO) desplaza UNIxCAJA y las tiendas una columna. Además, PRUEBAESTANDAR pide escribir a mano el nº de días de datos, aunque ese dato ya está en el Access. El usuario quiere un único programa que haga todo, en el que se elija qué palet estándar se calcula (ALTA ROTACIÓN, DROGUERÍA o ALIMENTACIÓN) y en el que el nº de días salga del propio Access.

## What Changes

- **Un solo programa.** PRUEBAESTANDAR (misma ventana, mismo nombre y mismo `PRUEBAESTANDAR.exe`) hace en una sola ejecución lo que antes hacían los dos:
  - Entradas: SALALM, MAESTRO, MAESTRO DE CADUCIDAD, MOVIMIENTOS (Access) y TABLA DE TIENDAS Y MEDIOS.
  - Una caja para el nº de artículos.
  - Un selector de TIPO con cuatro opciones: ALTA ROTACIÓN, DROGUERÍA, ALIMENTACIÓN y TODOS. Con TODOS no se filtra por tipo: el palet se calcula con los N artículos del FICHERO BASE (si pones 1000, con esos 1000).
- **Orden de la selección.** Primero se toman los N artículos con más CAJAS de SALALM FILTRADO, sea cual sea su tipo; así se forma el FICHERO BASE, que no cambia. Después, de esos N artículos, sólo se usan los del TIPO elegido para calcular el palet estándar.
- **Nº de días automático.** El nº de días de datos ya no se escribe a mano. **BREAKING:** desaparece la caja de días. El programa lo calcula como el nº de valores distintos de `MVFECI` en las filas del Access con `MVTMOV = "PI"`.
- **Salidas.** Se generan 4 ficheros en la carpeta del SALALM:
  - SALALM FILTRADO y FICHERO BASE, con el mismo contenido que en GENERABASE.
  - PRUEBAESTANDAR (.xlsx) y REPARTOESTANDAR (.xls), con la misma estructura que ahora:
    - PRUEBAESTANDAR conserva el formato antiguo: CODIGO, PESO, Volumen y UNIxCAJA en A–D, sin la columna TIPO, y las tiendas desde la columna E. Contiene sólo los artículos del TIPO elegido, con ELECCIÓN rellena.
    - REPARTOESTANDAR no cambia de formato. Contiene los artículos del TIPO elegido.
- **Nombres con TIPO y fecha.** Los nombres de los ficheros llevan la fecha de ejecución (`AAAAMMDD`), y los dos del palet llevan además el TIPO abreviado: AR = ALTA ROTACIÓN, DR = DROGUERÍA, AL = ALIMENTACIÓN, TD = TODOS. **BREAKING:** desaparecen los nombres fijos `PRUEBAESTANDAR.xlsx` y `REPARTOESTANDAR.xls`. Por ejemplo, el 03/11/2026 con ALTA ROTACIÓN:
  - `SALALM FILTRADO_20261103.xlsx`
  - `FICHERO BASE_20261103.xlsx`
  - `PRUEBAESTANDAR_AR_20261103.xlsx`
  - `REPARTOESTANDAR_AR_20261103.xls`

  Así, calcular otro TIPO no sobrescribe los ficheros del palet de los demás TIPOS.
- **Confirmación y reintento.** Una única confirmación antes de sobrescribir cualquiera de los 4 ficheros. Si un fichero está abierto, se puede reintentar sin repetir el cálculo.
- **Otro TIPO sin releer el Access.** Si después de una ejecución sólo se cambia el TIPO o la tabla de tiendas, el programa reutiliza lo ya leído y calcula otro TIPO sin volver a leer el Access, que tarda unos 10 minutos.
- **Resumen.** El resumen une:
  - los totales de control de GENERABASE,
  - el nº de días contado,
  - el TIPO y el nº de artículos de ese TIPO,
  - los datos de siempre de PRUEBAESTANDAR: tiendas, cajas, unidades y avisos.
- **GENERABASE.** La aplicación GENERABASE (`GENERABASE.exe`) se mantiene tal cual para quien sólo quiera generar el FICHERO BASE. El algoritmo de selección de bultos no cambia.

## Capabilities

### New Capabilities
- `pruebaestandar-integrado`: el flujo unificado. Cubre:
  - la generación del FICHERO BASE dentro de PRUEBAESTANDAR;
  - la elección del TIPO y el filtro de los artículos de ese TIPO;
  - el recuento de días desde el Access;
  - la formación de la base del TIPO con la estructura antigua;
  - las 4 salidas;
  - la reutilización de la lectura al cambiar sólo de TIPO.

### Modified Capabilities
- `interfaz-grafica`: la ventana pasa a tener:
  - las 5 entradas,
  - el nº de artículos,
  - el selector de TIPO,
  - ninguna caja de días.

  También cambian las validaciones, la confirmación de sobrescritura (4 ficheros), el resultado y el tiempo de respuesta, porque ahora se lee el Access.
- `seleccion-bultos`: el requisito «Nº de días de datos» pasa a obtener los días del Access en lugar de la entrada del usuario.
- `ficheros-excel`: el fichero base que procesa PRUEBAESTANDAR ya no lo aporta el usuario; se forma a partir del FICHERO BASE y del TIPO. PRUEBAESTANDAR y REPARTOESTANDAR se guardan en la carpeta del SALALM, con el TIPO abreviado y la fecha en el nombre.

## Impact

- **Código:**
  - `pruebaestandar/gui.py` se rehace.
  - Nuevo módulo de flujo integrado en `pruebaestandar/`, que reutiliza `generabase` (lectura, filtrado, FICHERO BASE) y el cálculo actual de PRUEBAESTANDAR (`lectura`, `seleccion`, `verificacion`, `reparto`, `escritura`).
  - En `generabase/access.py` se añade, sin cambiar lo que ya hace, el recuento de fechas distintas de todas las filas PI.
- **Dependencias:** `requirements.txt` añade `access-parser==0.0.6`. PRUEBAESTANDAR.exe pasa a incluir el lector de Access.
- **CI:** el workflow `compilar-exe.yml` también se dispara con cambios en `generabase/**`.
- **Pruebas:** se rehacen `tests/test_gui.py` y se añaden pruebas del flujo integrado. Las pruebas actuales del cálculo siguen valiendo.
- **Programa de importación:** el fichero de reparto deja de llamarse `REPARTOESTANDAR.xls`. Si el programa de importación busca ese nombre exacto, habrá que elegir el fichero nuevo o renombrarlo. El formato interno no cambia.
- **GENERABASE.exe:** conserva sus nombres actuales, sin fecha.
- **Uso:** el usuario ya no aporta un FICHERO BASE ni escribe los días. Una ejecución completa tarda lo que tarde la lectura del Access, unos 10 minutos con el Access real en red.
