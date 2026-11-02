# Proposal

## Why

En el FICHERO BASE que genera GENERABASE, la columna LINEAS de cada tienda cuenta hoy los movimientos (filas del Access) de cada artículo. El usuario quiere que mida en **cuántos días distintos** ha pedido la tienda ese artículo, que es el dato útil para estimar la frecuencia de pedido.

## What Changes

- **LINEAS = nº de valores distintos de MVFECI** de los movimientos usados (PI y en los rangos de tienda), por artículo y tienda. Varios movimientos del mismo artículo y tienda en el mismo día cuentan como 1.
- **BULTOS no cambia:** sigue siendo la suma de |MVCANM| ÷ MVUNCA de todos los movimientos.
- **MVFECI pasa a ser columna obligatoria** del Access. Si falta, el proceso se detiene indicándolo. Si un movimiento usado tiene MVFECI vacío o no numérico, también se detiene, con la fila del Access, para no calcular LINEAS a medias.
- **Comprobación previa al guardado:** la suma de LINEAS se recalcula como la suma, por artículo y tienda, de sus días distintos.
- **Totales de control:** se mantiene el nombre «LINEAS», que sigue mostrando el nº de movimientos usados (filas del Access), como hasta ahora. Se añade el nº de días distintos del periodo para compararlo con Access, y la fecha mínima y máxima se muestran siempre.
- PRUEBAESTANDAR no cambia. Cuando se adapte para leer este FICHERO BASE, recibirá LINEAS con el nuevo significado (días con pedido).

## Capabilities

### New Capabilities
<!-- Ninguna. -->

### Modified Capabilities
- `generabase-fichero-base`: LINEAS cuenta días distintos (MVFECI) por artículo y tienda, y la comprobación de totales usa ese criterio.
- `generabase-lectura`: MVFECI pasa a ser columna obligatoria del Access y se valida en los movimientos usados. Los totales de control añaden los días distintos (LINEAS conserva su nombre).

## Impact

- Código: `generabase/access.py` (MVFECI obligatoria; la fecha viaja con cada movimiento), `generabase/fichero_base.py` (agregación y comprobación de LINEAS) y `generabase/proceso.py` (texto del resumen).
- Pruebas de `tests_generabase/` (agregación, comprobación, lectura y resumen).
- `README.md`, sección GENERABASE.
- Nada de PRUEBAESTANDAR. El `.exe` de GENERABASE se recompila solo al subir el cambio.
