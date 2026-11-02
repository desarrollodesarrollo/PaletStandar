# Spec Delta

## MODIFIED Requirements

### Requirement: BULTOS, LINEAS y ELECCIÓN
Para cada artículo y tienda:
- BULTOS SHALL ser la suma de CAJAS de sus movimientos usados, sin redondear. Si el resultado es entero se escribe como entero.
- LINEAS SHALL ser el nº de valores distintos de MVFECI (fecha del movimiento) entre sus movimientos usados. Varios movimientos del mismo artículo y tienda con la misma fecha cuentan como 1.
- Si no hay ningún movimiento, BULTOS y LINEAS MUST quedar vacías.
- ELECCIÓN MUST quedar siempre vacía.

Un artículo de los N sin ningún movimiento en ninguna tienda SHALL aparecer igualmente, con todas las celdas de tienda vacías.

#### Scenario: Suma y recuento
- **WHEN** el artículo 2465665 tiene en la tienda 389 dos movimientos de 16 y 8 unidades con MVUNCA 16, de fechas distintas
- **THEN** en el bloque de la tienda 389 su BULTOS es 1,5 y su LINEAS es 2

#### Scenario: Varios movimientos el mismo día
- **WHEN** el artículo 2465665 tiene en la tienda 389 tres movimientos de 16 unidades con MVUNCA 16, dos del 01/10/2025 y uno del 03/10/2025
- **THEN** su BULTOS es 3 y su LINEAS es 2

#### Scenario: Sin movimientos en una tienda
- **WHEN** un artículo no tiene movimientos en la tienda 82
- **THEN** sus celdas BULTOS y LINEAS de la tienda 82 están vacías

### Requirement: Formato y guardado
El FICHERO BASE SHALL guardarse como `FICHERO BASE.xlsx` en la carpeta del fichero SALALM, con los anchos de columna de la plantilla: A 22,43; B 15,14; C y D 13; E 15,14; resto 13. Antes de guardar, el sistema MUST comprobar, recalculándolo desde los movimientos usados de esos N artículos, que la suma de todos los BULTOS del fichero coincide con la suma de sus CAJAS, y que la suma de todas las LINEAS coincide con la suma, por artículo y tienda, de su nº de fechas distintas. Si no coincide, MUST NOT guardar.

#### Scenario: Comprobación de totales
- **WHEN** los movimientos usados de los N artículos suman 12.345,5 cajas y, sumando por artículo y tienda sus fechas distintas, 4.321 líneas
- **THEN** el fichero sólo se guarda si sus BULTOS suman 12.345,5 y sus LINEAS 4.321
