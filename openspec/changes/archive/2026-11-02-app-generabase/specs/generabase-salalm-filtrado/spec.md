# Spec Delta

## Purpose

Construir SALALM FILTRADO: el SALALM completado con la caducidad del MAESTRO y del MAESTRO DE CADUCIDAD, con peso y volumen en kg y litros, ubicación y tipo de ubicación, filtrado según las reglas del almacén y ordenado por cajas de salida.

## ADDED Requirements

### Requirement: Columnas de SALALM FILTRADO
Cada fila de SALALM SHALL producir una fila con estas columnas, en este orden y con estos encabezados:

| Encabezado | Valor |
|---|---|
| `CODIGO` | CODIGO de SALALM, como número |
| `DESCRIPCIÓN` | DESCRIPC de SALALM, tal cual |
| `CAJAS` | CAJAS de SALALM, como número (puede tener decimales) |
| `UNIXCAJA` | UNIXCAJA de SALALM, como número |
| `PESO` | PESO de SALALM ÷ 1000 (kg por caja) |
| `VOLUMEN` | VOLUMEN de SALALM ÷ 1000 (litros por caja) |
| `SECCIÓN` | DESSEC de SALALM |
| `CADUCA` | MACADU del MAESTRO para ese código (`MAARTI` = `CODIGO`); vacío si no está en el MAESTRO |
| `CADUCIDAD CODIGO` | MACLCA del MAESTRO; vacío si no tiene |
| `CADUCIDAD` | C3UTIL del MAESTRO DE CADUCIDAD cuyo C3CADU = MACLCA, como número; vacío si no hay código |
| `DESCRIPCIÓN CADUCIDAD` | C3COME de esa misma fila |
| `BAJAS` | BAJA de SALALM |
| `UBICACIÓN` | Las 3 primeras posiciones de RADUBICA convertidas a número (`"24012404"` → 240, `"08004901"` → 80); vacío si son espacios |
| `TIPO DE UBICACIÓN` | Según UBICACIÓN: < 220 `ALIMENTACIÓN`; 220–290 `ALTA ROTACIÓN`; 291–399 `PASILLO ESTRECHO`; 400–599 `BAZAR ABAJO`; ≥ 600 `DROGUERÍA` |

Si un MACLCA no existe en el MAESTRO DE CADUCIDAD, o un artículo tiene MACADU = `S` sin MACLCA, CADUCIDAD SHALL quedar vacía y el caso MUST aparecer en los avisos.

#### Scenario: Peso y volumen
- **WHEN** el artículo 273137 tiene PESO 8000 y VOLUMEN 12648 en SALALM
- **THEN** en SALALM FILTRADO tiene PESO 8 y VOLUMEN 12,648

#### Scenario: Caducidad cruzada
- **WHEN** un artículo tiene en el MAESTRO MACADU `S` y MACLCA `N`, y el MAESTRO DE CADUCIDAD tiene `N` = 182 días «ARTICULOS DE 6 MESES»
- **THEN** su fila tiene CADUCA `S`, CADUCIDAD CODIGO `N`, CADUCIDAD 182 y DESCRIPCIÓN CADUCIDAD «ARTICULOS DE 6 MESES»

#### Scenario: Tramos de ubicación
- **WHEN** las ubicaciones son 219, 220, 290, 291, 399, 400, 599 y 600
- **THEN** sus tipos son ALIMENTACIÓN, ALTA ROTACIÓN, ALTA ROTACIÓN, PASILLO ESTRECHO, PASILLO ESTRECHO, BAZAR ABAJO, BAZAR ABAJO y DROGUERÍA

### Requirement: Filas excluidas
SALALM FILTRADO MUST NOT incluir las filas en las que:
- SECCIÓN sea `SUMINISTROS Y SERVICIOS` o `CAMPAÑA FIDELIDAD`;
- BAJAS sea `B`;
- CADUCIDAD sea un número menor que 92;
- UBICACIÓN esté vacía, sea 0 o no sea numérica (por ejemplo RADUBICA `"   00000"` o `"00012345"`);
- TIPO DE UBICACIÓN sea `PASILLO ESTRECHO` o `BAZAR ABAJO`.

Las comparaciones de texto MUST hacerse sin distinguir mayúsculas ni espacios extremos. Los artículos con CADUCIDAD vacía, porque no caducan (MACADU `N`) o porque no están en el MAESTRO, MUST mantenerse. El resumen SHALL indicar cuántas filas se excluyen por cada regla y cuántas de las que quedan no estaban en el MAESTRO. Cada fila excluida se cuenta sólo en la primera regla que cumple, en este orden: sección, baja, ubicación, tipo de ubicación, caducidad.

#### Scenario: Caducidad corta
- **WHEN** un artículo tiene CADUCIDAD 85
- **THEN** no aparece en SALALM FILTRADO

#### Scenario: Caducidad justo en el límite
- **WHEN** un artículo tiene CADUCIDAD 92
- **THEN** aparece en SALALM FILTRADO

#### Scenario: Artículo que no caduca o no está en el MAESTRO
- **WHEN** un artículo tiene MACADU `N`, u otro no aparece en el MAESTRO, y cumple el resto de reglas
- **THEN** los dos aparecen en SALALM FILTRADO con CADUCIDAD vacía

#### Scenario: Sin ubicación
- **WHEN** RADUBICA es `"   00000"`
- **THEN** el artículo no aparece en SALALM FILTRADO

#### Scenario: Recuento con los datos de ejemplo
- **WHEN** se procesan los ficheros de ejemplo
- **THEN** se excluyen 752 filas por sección, 2.817 por baja, 654 por ubicación, 2.518 por tipo de ubicación y 97 por caducidad, y quedan 7.808 filas, de las cuales 1.812 no estaban en el MAESTRO

### Requirement: Orden y exportación
SALALM FILTRADO SHALL ordenarse por CAJAS de mayor a menor, y a igualdad de CAJAS por CODIGO de menor a mayor. Se SHALL guardar como `SALALM FILTRADO.xlsx` en la carpeta del fichero SALALM: una hoja con los encabezados en la fila 1 y un artículo por fila desde la fila 2, con números como números y celdas vacías donde no hay dato.

#### Scenario: Primeras filas
- **WHEN** se genera SALALM FILTRADO
- **THEN** la fila 2 es el artículo con más CAJAS de los que quedan tras el filtro, y ninguna fila tiene más CAJAS que la anterior
