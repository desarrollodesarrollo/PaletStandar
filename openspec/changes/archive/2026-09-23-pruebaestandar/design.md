# Design

## Context

- El repositorio está vacío salvo la configuración de OpenSpec y Claude: no hay código previo que respetar.
- Datos observados en los ficheros de ejemplo (`FICHERO_BASE_AR.xlsx`, `TABLA_DE_TIENDAS_Y_MEDIOS.xlsx`):
  - Fichero base: hoja `Hoja1`, rango A1:TX132 → 130 artículos × 180 tiendas (544 columnas), sin fórmulas ni celdas combinadas; ELECCIÓN vacía; BULTOS/LINEAS vacíos cuando no hay salida. Otro ejemplo previo tenía 977 artículos, así que el nº de filas no puede fijarse.
  - Tabla de tiendas: hoja `Hoja1`, 2467 tiendas, sólo dos combinaciones de medio: PALET 875 kg / 1300 L / 0,673 kg/L y CARRO 475 kg / 600 L / 0,792 kg/L. Las 180 tiendas del fichero base están en la tabla (114 PALET, 66 CARRO).
  - Densidad de artículos entre 0,008 y 0,972 kg/L (mediana 0,656, muy cerca del límite del palet): la restricción de densidad será activa a menudo en tiendas PALET.
  - En 174 de 180 tiendas no cabe ni 1 caja de cada artículo con salida (volumen mediano ≈170 % del medio). El volumen es la restricción dominante; por eso el reparto es proporcional a líneas (ver proposal.md).
- Usuarios de oficina en Windows, sin conocimientos de consola.

## Goals / Non-Goals

**Goals:**
- Núcleo de cálculo puro (sin Excel ni ventana) para poder probarlo con datos pequeños y deterministas.
- Conservar intacto el fichero base: sólo se escriben celdas ELECCIÓN en una copia.
- Menos de 60 s para 650 × 180 en Python puro.

**Non-Goals:**
- Asignar las cajas a cada carro concreto (carro 1 / carro 2) ni optimizar la estiba física.
- Generar un ejecutable `.exe` o instalador (se puede añadir después con PyInstaller).
- Optimización matemática exacta (MILP); se usa una heurística transparente acordada con el usuario.
- Soportar `.xls` antiguo o `.csv`.

## Decisions

### 1. Lenguaje y librerías: Python 3.10+, openpyxl, tkinter
- `openpyxl` lee y escribe `.xlsx` conservando formatos, anchos y hojas; se abre el fichero base en modo normal (no `read_only`) y se escribe sólo en las celdas ELECCIÓN antes de `save()` con el nombre nuevo.
- `tkinter` viene con Python en Windows: ventana sin dependencias extra.
- Alternativas: `pandas` (descartado: el doble encabezado y la escritura sin perder formato son incómodos, y añade una dependencia pesada); PySide/Qt (descartado: instalación mayor para una ventana de 4 controles).

### 2. Estructura del código
Paquete `pruebaestandar/`:
- `modelo.py` – dataclasses `Articulo` (código, fila, peso, volumen), `Medio` (tipo, n_medios, peso_max, vol_max, densidad), `DemandaTienda` (tienda, columna ELECCIÓN, bultos y líneas por artículo), `Resultado` (cajas por artículo y tienda, avisos).
- `lectura.py` – lee y valida fichero base y tabla; devuelve el modelo o lanza `ErrorValidacion` con mensaje en español.
- `seleccion.py` – función pura `seleccionar(articulos, demanda, medio, dias) -> dict[fila, cajas]`.
- `verificacion.py` – comprobación independiente de todas las restricciones sobre el resultado.
- `escritura.py` – escribe ELECCIÓN en el libro abierto y guarda `PRUEBAESTANDAR.xlsx`.
- `proceso.py` – orquesta lectura → selección por tienda → verificación → escritura y construye el resumen.
- `gui.py` – ventana tkinter; `__main__.py` lanza la ventana (`python -m pruebaestandar`), y `PRUEBAESTANDAR.pyw` en la raíz permite doble clic en Windows sin consola.

Alternativa: un único script. Descartado porque impide probar el algoritmo sin Excel ni ventana.

### 3. Algoritmo de selección por tienda (cocientes tipo D'Hondt con cola de prioridad)
Por cada tienda:
1. Elegibles = artículos con BULTOS > 0 y peso/volumen válidos. `max_i = ceil(BULTOS_i / días)` con aritmética entera/`Fraction` (evita que 10/5 dé 2.0000001 → 3).
2. Cola de prioridad (`heapq`) con clave `(-L_i/(q_i+1), q_i>0, -L_i, -BULTOS_i, volumen_i, código_i)`; el índice se compara como `Fraction(L_i, q_i+1)` para que los empates sean exactos. El desempate por BULTOS (petición del usuario tras la revisión) decide sobre todo entre artículos de 1–2 líneas, que empatan con frecuencia.
3. Se extrae el mejor candidato y se prueba su caja siguiente:
   - Si cabe (P+p ≤ Pmax, V+v ≤ Vmax y (P+p) < d·(V+v)), se asigna, se incrementa `q_i` y, si `q_i < max_i`, se reinserta con su nuevo índice.
   - Si no cabe por **peso o volumen**, el artículo se descarta definitivamente (los totales sólo crecen, nunca volverá a caber).
   - Si no cabe **sólo por densidad**, se aparca en una lista de espera; cada vez que se asigna una caja se reintroducen los aparcados en la cola (una caja ligera puede bajar la densidad y hacerlos caber).
4. Termina cuando la cola está vacía. Coste ≈ O((n + cajas) · log n) por tienda, más reintentos de aparcados; holgado para 650 × 180.

La densidad se comprueba como `P < d·V − ε` (ε = 1e-9) en lugar de dividir, para evitar la división por 0 y cumplir el "estrictamente menor".

Alternativas consideradas: "1 caja para todos por líneas y luego extras" (descartada con el usuario: en 174/180 tiendas deja todo a 1 caja); "máxima variedad" (favorece artículos pequeños con pocas líneas); MILP con PuLP/CBC (mejor aprovechamiento pero menos explicable y dependencia extra).

### 4. Dos carros como una capacidad conjunta
Para CARRO se usan 2 × peso y 2 × volumen con la misma densidad límite, como pidió el usuario ("no superar las dimensiones de 2 carros"). No se reparte explícitamente entre carro 1 y 2: las cajas (≈ 5–30 L) son pequeñas frente a 600 L por carro, así que cualquier selección que cumpla la capacidad conjunta se puede repartir en dos carros en la práctica.

### 5. Verificación independiente antes de guardar
`verificacion.py` recalcula desde el resultado y los datos de entrada (sin reutilizar estado del algoritmo): enteros ≥ 1, `q ≤ max`, sólo elegibles, P ≤ Pmax, V ≤ Vmax, P < d·V. Cualquier fallo aborta el guardado. Es una red de seguridad barata frente a errores futuros en el algoritmo.

### 6. Lectura de encabezados y valores
- Encabezados comparados en mayúsculas y sin espacios extremos; se acepta `ELECCION` sin tilde además de `ELECCIÓN`.
- Códigos de tienda y artículo se normalizan a entero si vienen como `10081.0` o `"10081"`, para que cuadren entre ambos ficheros.
- BULTOS/LINEAS vacíos → 0; se aceptan decimales (se redondea hacia arriba en el máximo), negativos o texto → error de validación.

### 7. Interfaz: cálculo en hilo secundario
El proceso se ejecuta en un `threading.Thread` y la ventana consulta el resultado con `after()`; así la ventana no se congela y el botón queda desactivado mientras dura. Errores de escritura (`PermissionError` por Excel abierto) muestran un diálogo "Reintentar / Cancelar" que reintenta sólo el guardado.

### 8. Pruebas
- `pytest` con libros sintéticos pequeños generados en las propias pruebas (openpyxl) para lectura, validación y escritura.
- Pruebas unitarias del algoritmo con casos de los escenarios de las specs (más líneas → más cajas, caja que no cabe, densidad compensada, todo cabe, tienda vacía, determinismo).
- Prueba de propiedades: datos aleatorios con semilla fija → la verificación nunca falla.
- Prueba de rendimiento con datos sintéticos 650 × 180 (< 60 s).
- Los ficheros reales de ejemplo no se suben al repositorio; se usan en una ejecución de aceptación manual.

## Risks / Trade-offs

- [Heurística, no óptimo global] → Puede dejar algún hueco pequeño que un optimizador exacto aprovecharía. Mitigación: el hueco final se rellena con cajas de artículos pequeños al descartar las que no caben; la hoja `RESUMEN` propuesta en Open Questions permitiría revisar la ocupación por tienda.
- [Artículos con muy pocas líneas pueden quedar fuera] → Es consecuencia directa de priorizar líneas con capacidad escasa, aceptada por el usuario. Mitigación: las pruebas de aceptación con los ficheros reales revisan unas cuantas tiendas a mano con el usuario.
- [Densidad muy ajustada en palets (mediana artículos 0,656 vs 0,673)] → Artículos densos con muchas líneas pueden entrar tarde o no entrar. Mitigación: la lista de espera por densidad los reintenta tras cada caja ligera.
- [Cambios de formato del Excel de origen] → Validación estricta de encabezados con mensajes que dicen qué columna revisar.
- [Tiempo de guardado con openpyxl en ficheros grandes] → 650 × 544 celdas ≈ 350 k celdas, del orden de segundos; cubierto por la prueba de rendimiento.

## Migration Plan

No aplica (programa nuevo). Distribución: copiar la carpeta del proyecto, instalar Python 3.10+ y `pip install -r requirements.txt`; se ejecuta con doble clic en `PRUEBAESTANDAR.pyw`.

## Open Questions

- ¿Conviene más adelante añadir una hoja `RESUMEN` en el Excel de salida con kg, L, densidad y % de ocupación por tienda? No cambia las reglas; se puede añadir sin tocar el algoritmo.
- ¿Se quiere empaquetar como `.exe` con PyInstaller para equipos sin Python?
