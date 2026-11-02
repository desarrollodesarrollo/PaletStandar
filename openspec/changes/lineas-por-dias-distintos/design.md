# Design

## Context

- Hoy, `access.filtrar()` produce `MovimientosUsados.lineas`, una lista de tuplas `(artículo, tienda, cajas)`.
  - MVFECI es opcional y solo alimenta `fecha_min` / `fecha_max` del resumen.
  - `fichero_base.agregar()` calcula LINEAS con `len()` de los movimientos de cada `(artículo, tienda)`.
  - `fichero_base.verificar_totales()` recalcula las LINEAS esperadas contando movimientos.
- En el Access, MVFECI es `Double` con formato AAAAMMDD (`20251015.0`). `columnas.entero()` ya lo normaliza a entero.
- Datos observados:
  - La copia de ejemplo tiene un solo día (15/10/2025), así que ahí LINEAS valdrá siempre 1.
  - En el Access real hay 15 días (01/10–15/10/2025): LINEAS irá de 1 a 15.

## Goals / Non-Goals

**Goals:**
- Que LINEAS sea el nº de fechas distintas por artículo y tienda, con la misma garantía que hoy: la comprobación previa al guardado lo recalcula de forma independiente.
- No dejar nunca LINEAS calculada a medias: un movimiento usado sin fecha válida detiene el proceso.

**Non-Goals:**
- Cambiar BULTOS, el filtrado de movimientos, SALALM FILTRADO o la estructura del FICHERO BASE.
- Tocar PRUEBAESTANDAR.
- Mejorar el tiempo de lectura del Access de 10 minutos; si hace falta, será un cambio aparte.

## Decisions

### 1. La fecha viaja con cada movimiento
`MovimientosUsados.lineas` pasa a ser `(artículo, tienda, cajas, fecha)`, con la fecha como entero AAAAMMDD.
- Las propiedades `tiendas`, `articulos` y `total_cajas` se adaptan.
- Se añade `dias` (nº de fechas distintas del conjunto).
- `fecha_min` / `fecha_max` se derivan de los movimientos usados.

Alternativa descartada: guardar aparte un `{(artículo, tienda): set(fechas)}` dentro de `access.py`. Mezclaría la agregación del FICHERO BASE con la lectura, y la comprobación de totales dejaría de ser independiente.

### 2. MVFECI obligatoria y validada solo en filas usadas
- `COLUMNAS` incluye `MVFECI` y desaparece `OPCIONAL_FECHA`.
- En `filtrar()`, solo para las filas que van a usarse (PI, en rango y con MVUNCA > 0): si `entero(MVFECI)` es `None`, se lanza `ErrorValidacion` con el nº de fila, el artículo y la tienda.
- Una fila no usada con fecha vacía no afecta. Es coherente con el criterio de «solo me interesan las filas PI».

### 3. Agregación
En `fichero_base.agregar()` se agrupan por `(artículo, tienda)` las cajas en una lista y las fechas en un `set`:
- BULTOS = `math.fsum(cajas)`.
- LINEAS = `len(fechas)`.

La firma y el formato de salida (`{(a, t): (bultos, lineas)}`) no cambian, así que `construir_libro()` no se toca.

### 4. Comprobación previa al guardado
`verificar_totales()` recalcula las LINEAS esperadas desde `usados.lineas` con un conjunto de `(artículo, tienda, fecha)` de los N artículos: su tamaño es la suma esperada. Se compara con la suma de las celdas LINEAS escritas, que se leen de la hoja como hoy.

### 5. Resumen
- En los totales de control se mantiene «LINEAS: n» (nº de movimientos usados, como hoy), por decisión del usuario, y se añade «Días distintos: d» junto a las fechas, que se muestran siempre.
- La línea del FICHERO BASE sigue diciendo «… bultos y … líneas», con la nueva suma.

## Risks / Trade-offs

- [Un único movimiento usado sin fecha detiene todo el proceso] → En el Access real no ha ocurrido: todos tenían fecha entre 01/10 y 15/10. El mensaje indica la fila exacta. Si en la práctica molestara, se podría cambiar a «avisar y no contar».
- [LINEAS cambia de significado para PRUEBAESTANDAR cuando se encadenen] → Es la intención del usuario; queda anotado en la propuesta y en el README.
