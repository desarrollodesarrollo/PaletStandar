## Context

Hay dos paquetes que ya funcionan y están probados:

- **`generabase/`**:
  - `access.leer_movimientos` / `filtrar` producen `MovimientosUsados`.
  - `lectura`, `salalm.construir` / `filtrar` producen SALALM FILTRADO.
  - `fichero_base.seleccionar` / `agregar` / `construir_libro` / `verificar_totales` producen el FICHERO BASE. Es la hoja `TODOS`: TIPO va en la columna B, UNIxCAJA en la E y las tiendas empiezan en la F.
  - `proceso.calcular` encadena todo y devuelve `Calculo(libro_salalm, libro_base, resumen)`.
- **`pruebaestandar/`**:
  - `lectura.extraer_datos_base(ws)` lee el formato antiguo: UNIxCAJA en la columna D y las tiendas desde la E.
  - `seleccion.seleccionar`, `verificacion.verificar` / `verificar_reparto`, `escritura.escribir_elecciones`, `reparto.construir_reparto`.
  - `proceso.calcular(ruta_base, ruta_tabla, dias)` encadena todo leyendo el fichero base desde disco.

Las reglas del algoritmo (96 %, D'Hondt, densidad, desempates) están cerradas y verificadas por el usuario, así que no se tocan. Leer el Access real tarda unos 10 minutos, y esto condiciona la experiencia al cambiar de TIPO.

## Goals / Non-Goals

**Goals:**
- Reutilizar sin cambios de comportamiento el cálculo de GENERABASE y el de PRUEBAESTANDAR. El código nuevo se limita a unirlos: filtrar por TIPO, quitar la columna B, contar los días y montar la ventana.
- Que una segunda ejecución con otro TIPO no vuelva a leer el Access.
- Mantener GENERABASE.exe y su ventana tal cual.

**Non-Goals:**
- Calcular varios TIPOS en una sola ejecución.
- Cambiar los nombres de salida de GENERABASE.exe, que sigue con `SALALM FILTRADO.xlsx` y `FICHERO BASE.xlsx`.
- Aceptar como entrada un FICHERO BASE ya generado.
- Cambiar el algoritmo de selección o el formato de REPARTOESTANDAR.xls.
- Mejorar la velocidad de lectura del Access.

## Decisions

### 1. El programa unificado es PRUEBAESTANDAR; GENERABASE sigue aparte
La ventana PRUEBAESTANDAR (`pruebaestandar/gui.py`, `PRUEBAESTANDAR.pyw`, `PRUEBAESTANDAR.exe`) pasa a tener las 5 entradas, N y TIPO. El usuario pidió «adaptar PRUEBAESTANDAR» y «juntar los 2 programas en uno». Mantener el nombre conserva el exe que ya conoce. GENERABASE no se borra porque el usuario pidió no tocarlo, y sirve para generar sólo el FICHERO BASE.
- *Alternativa descartada:* un tercer programa con otro nombre. Añade otro exe sin necesidad.

### 2. Primero los N artículos, después el TIPO
El FICHERO BASE se genera exactamente igual que en GENERABASE: los N artículos con más CAJAS de cualquier tipo. Después se filtra por TIPO. Así se lee al pie de la letra «la selección antes de la elección del TIPO», y el FICHERO BASE sigue siendo el mismo para los tres TIPOS, lo que permite reutilizarlo (decisión 6).
- *Alternativa descartada:* filtrar por TIPO antes de tomar los N. Daría un FICHERO BASE distinto por TIPO e iría contra el orden que pidió el usuario.
- El resumen indica cuántos artículos del TIPO hay entre los N, para que el usuario ajuste N si quiere más.

### 3. Base del TIPO en memoria con el formato antiguo y el código de PRUEBAESTANDAR sin cambios
La base del TIPO se crea en el nuevo módulo `pruebaestandar/integrado.py`:
1. `fichero_base.construir_libro(elegidos_del_tipo, tiendas, agregado)` crea un libro que reutiliza el formato de GENERABASE.
2. `ws.delete_cols(2)` quita TIPO.
3. Se recolocan los anchos de columna: A, después C→B, D→C, E→D, y 13 desde la E.

El libro resultante ya tiene el formato antiguo: UNIxCAJA en D y tiendas desde la E. Sobre él se ejecutan sin cambios `extraer_datos_base`, `comprobar_limites`, `leer_tabla_medios`, `seleccionar`, `verificar`, `calcular_unidades`, `verificar_reparto`, `escribir_elecciones` y `construir_reparto`. Ese libro, con ELECCIÓN rellena, es PRUEBAESTANDAR.xlsx.

Para no duplicar código, `pruebaestandar/proceso.py` se divide:
- `calcular_desde_libro(libro, ruta_tabla, dias, destino, destino_reparto) -> Calculo` hace el trabajo.
- `calcular(ruta_base, ruta_tabla, dias)` sigue existiendo: lee el fichero y llama a `calcular_desde_libro`. Así las pruebas actuales siguen valiendo.

- *Alternativa descartada:* que `extraer_datos_base` detecte y acepte también el formato con TIPO. Mezcla dos formatos en el lector, y además PRUEBAESTANDAR.xlsx debe mantener el formato antiguo.
- Hay una comprobación cruzada independiente, `verificar_base_tipo(libro_tipo, libro_base, tipo)`. Recorre la hoja TODOS del FICHERO BASE y, para cada fila del TIPO, compara sus celdas con las de la base del TIPO quitando la columna B. Así se detecta cualquier desplazamiento de columnas.

### 4. Días: recuento literal sobre todas las filas PI
En `generabase/access.filtrar` se añade, sin cambiar nada de lo existente, el campo `fechas_pi: set[int]` con las MVFECI no vacías de todas las filas PI. Se rellena en el mismo bucle, antes del filtro de tienda. También se añade `pi_sin_fecha: int`, y las propiedades `dias_pi`, `fecha_pi_min` y `fecha_pi_max`.
- La propiedad `dias` existente (fechas de los movimientos usados) se mantiene para los totales de GENERABASE.
- El resumen de PRUEBAESTANDAR muestra `dias_pi` como «Nº de días de datos».
- Una MVFECI no numérica en una fila PI no usada se ignora como vacía, con aviso. No se convierte en error, igual que ya ocurre en GENERABASE con las filas no usadas.
- *Alternativa descartada:* reutilizar `dias`, que sólo cuenta las tiendas en rango. El usuario definió el criterio literalmente («MVFECI distintos con MVTMOV = PI»).

### 5. Flujo y objeto de cálculo
`integrado.py` define:
- `Datos`: el resultado reutilizable de la parte GENERABASE. Contiene `libro_salalm`, `libro_base`, `elegidos`, `tiendas`, `agregado`, `usados`, el resumen de GENERABASE y la `clave`.
- `preparar(rutas, n, progreso) -> Datos`: llama a la nueva función `generabase.proceso.calcular_datos`, que devuelve también los datos intermedios. `generabase.proceso.calcular` pasa a llamarla internamente, con el mismo resultado observable.
- `calcular_tipo(datos, tipo, ruta_tabla, progreso) -> CalculoIntegrado`, que hace lo siguiente:
  1. Filtra por TIPO, normalizado sin tildes.
  2. Comprueba `dias_pi >= 1`.
  3. Construye la base del TIPO y la verifica.
  4. Llama a `calcular_desde_libro`.
- `CalculoIntegrado.guardar()`:
  - Guarda los 4 ficheros en orden: SALALM FILTRADO, FICHERO BASE, PRUEBAESTANDAR, REPARTOESTANDAR.
  - Cada guardado ya es reintentable (`ErrorEscritura`).
  - Al reintentar, vuelve a guardar los 4. Es idempotente y cada uno se escribe con un fichero temporal más `os.replace` o con `escritura.guardar`.
- `TIPOS = ("ALTA ROTACIÓN", "DROGUERÍA", "ALIMENTACIÓN")`, con los mismos textos que `salalm.tipo_ubicacion`.

### 6. Reutilización entre ejecuciones (caché en la ventana)
La ventana guarda el último `Datos` junto con su `clave`. La clave se forma con:
- la ruta resuelta, `st_mtime_ns` y `st_size` de SALALM, MAESTRO, CADUCIDAD y Access;
- N.

Al ejecutar, si la clave coincide, se salta `preparar` y se pasa directamente a `calcular_tipo`. Si no coincide, se descarta y se recalcula. La tabla de tiendas no forma parte de la clave, porque se lee siempre en `calcular_tipo`.
- `Datos` no se modifica en `calcular_tipo`, ya que `construir_libro` crea un libro nuevo cada vez.
- `libro_salalm` y `libro_base` se guardan tal cual otra vez. Son objetos openpyxl que se pueden guardar varias veces.
- *Alternativa descartada:* releer siempre. Son 10 minutos por cada TIPO.

### 7. Ventana
- `ENTRADAS` tiene 5 tuplas `(clave, nombre, tipos)`, igual que en GENERABASE. La del Access filtra `*.accdb *.mdb`.
- N es un `ttk.Entry`, validado con `fichero_base.parsear_n`.
- TIPO es un `ttk.Combobox(state="readonly")` con `TIPOS` y vacío al abrir.
- La confirmación de sobrescritura es única para los 4 nombres, calculados con `rutas_salida(carpeta del SALALM, tipo, fecha)` (decisión 8).
- El hilo de trabajo usa una cola y `after`. La etiqueta de fase llega por el callback `progreso`.
- Si hay un error de escritura, `askretrycancel` llama a `calculo.guardar()` sin recalcular.
- El resumen une los dos textos: primero los datos de GENERABASE, luego el bloque «PALET ESTÁNDAR — TIPO …».
- La validación mira, por orden, los ficheros en el orden de la ventana, después N y después TIPO.

### 8. Nombres con TIPO y fecha
- `integrado.ABREVIATURAS = {"ALTA ROTACIÓN": "AR", "DROGUERÍA": "DR", "ALIMENTACIÓN": "AL"}`.
- `integrado.rutas_salida(ruta_salalm, tipo, fecha: date) -> RutasSalida(salalm, base, prueba, reparto)` devuelve:
  - `SALALM FILTRADO_{f}.xlsx`
  - `FICHERO BASE_{f}.xlsx`
  - `PRUEBAESTANDAR_{ab}_{f}.xlsx`
  - `REPARTOESTANDAR_{ab}_{f}.xls`

  Aquí `f = fecha.strftime("%Y%m%d")` y todos van en la carpeta del SALALM.
- **La fecha se fija una sola vez.** La ventana llama a `date.today()` al pulsar Ejecutar, antes de la confirmación. Esa fecha se pasa a `calcular_tipo` y queda guardada en el `CalculoIntegrado`. Así coinciden la confirmación, el guardado, el reintento y el resumen, aunque el proceso cruce la medianoche. Las pruebas pasan una fecha fija.
- **Las rutas se reciben, no se calculan.** `generabase.proceso.calcular_datos` y `pruebaestandar.proceso.calcular_desde_libro` reciben las rutas de destino como parámetros. Las funciones `rutas_salida` actuales de cada paquete no cambian, así que GENERABASE.exe y el `calcular(ruta_base, …)` antiguo siguen con sus nombres.
- `escritura.ruta_salida` rechaza un fichero base llamado PRUEBAESTANDAR.xlsx. Esto no afecta al flujo integrado, porque la base del TIPO está en memoria.
- *Alternativa descartada:* poner la fecha de los datos (última MVFECI). El usuario eligió la fecha de ejecución.

### 9. Empaquetado
- `requirements.txt` añade `access-parser==0.0.6`.
- `compilar-exe.yml` añade `generabase/**` a los `paths`.
- PyInstaller encuentra `generabase` y `access_parser` por import.
- Las pruebas del workflow siguen siendo `tests`. Las de `tests_generabase` ya tienen su propio workflow.

## Risks / Trade-offs

- [El FICHERO BASE de 1000 artículos puede tener pocos de un TIPO] → El resumen muestra «TIPO: k artículos de los N». Si k = 0, hay un error claro que sugiere aumentar N.
- [El programa de importación podría buscar el nombre fijo `REPARTOESTANDAR.xls`] → Se ha cambiado el nombre porque lo pidió el usuario, y el formato interno no cambia. Lo comprobará el usuario en la tarea 5.4. Si su programa exige el nombre fijo, basta con renombrar el fichero o seleccionarlo.
- [Con otro N el mismo día, SALALM FILTRADO y FICHERO BASE de ese día se sobrescriben] → La confirmación única los nombra. Los ficheros del palet de otros TIPOS no se tocan.
- [Los ficheros con fecha se acumulan en la carpeta] → Es lo deseado, porque sirven de histórico. El programa no borra nada.
- [La caché retiene en memoria los libros y los movimientos usados, unos cientos de MB con el Access real] → Sólo se guarda un `Datos`. Las columnas crudas del Access ya se liberan en `filtrar`.
- [`delete_cols` de openpyxl no mueve los anchos de columna] → Los anchos se reasignan explícitamente y una prueba comprueba la estructura y los anchos.
- [`dias_pi` puede incluir días con PI sólo de tiendas fuera de rango] → Es la definición pedida por el usuario. El resumen muestra también los días de los movimientos usados para poder comparar.
- [GENERABASE se ve afectado por los cambios en `generabase/`] → Los cambios son aditivos (nuevos campos y `calcular_datos`), y las pruebas de `tests_generabase` deben seguir pasando sin modificarse.

## Migration Plan

- Se publica un nuevo `PRUEBAESTANDAR.exe` desde el artefacto `PRUEBAESTANDAR-windows` de GitHub Actions. GENERABASE.exe sigue igual.
- El usuario deja de aportar FICHERO BASE y días.
- Los ficheros pasan a llamarse con fecha, y los del palet también con TIPO. Los ficheros antiguos sin fecha no se tocan.
- Para volver atrás basta con usar el exe anterior.
