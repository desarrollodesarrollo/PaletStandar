# Design

## Context

- El programa actual (ver `openspec/specs/`) calcula con `Medio.peso_max` / `Medio.volumen_max`, que usan tanto `seleccion.py` como `verificacion.py`. La columna D del fichero base nunca se ha leído: la densidad del artículo se deduce de peso ÷ volumen.
- `FICHERO_BASE_NUEVO.xlsx` (ejemplo): misma estructura que el anterior, con 130 artículos × 180 tiendas (A1:TX132). D2 = `UNIxCAJA`, con valores enteros entre 1 y 36 en los 130 artículos. Los códigos de tienda van de 81 a 949 y los de artículo son enteros. La lectura actual ya lo procesa sin errores.
- `PLANTILLA.xls` (ejemplo), analizada con xlrd:
  - Formato BIFF8 (Excel 97-2003), hojas `Hoja1`, `Hoja2` y `Hoja3` (estas dos vacías).
  - A1 = texto `Código`. B1:P1 = 15 códigos de tienda de ejemplo (81…947), guardados como números. El resto son celdas vacías con formato.
  - Estilos principales:
    - A1: Arial 12 negrita, borde fino en los 4 lados, relleno sólido de color índice 44, centrado.
    - Códigos de tienda: Arial 10 negrita, color de fuente índice 12, borde fino.
    - Columna A de datos (filas 2–188): formato numérico `0`, Arial 10, borde fino.
    - Celdas de datos (filas 2–188): Arial 12 negrita, borde fino.
  - Anchos: A = 2304 y el resto = 1024 (en 1/256 de carácter). Alto de fila: 315 (15,75 pt).
  - A partir de la fila 189 hay formatos sueltos de usos anteriores (columna A como texto `@`, rellenos en columnas concretas). Se consideran restos y no se replican.
- Con los datos nuevos, la tabla de tiendas que tenemos (códigos 10081…) no casa: las 180 tiendas sólo coinciden sumando 10000. El usuario tiene que usar la tabla nueva.

## Goals / Non-Goals

**Goals:**
- Aplicar el margen del 96 % en un único sitio, para que selección y verificación no puedan divergir.
- Generar `REPARTOESTANDAR.xls` sin depender de la plantilla en tiempo de ejecución: el programa lleva los estilos incorporados.
- Mantener PRUEBAESTANDAR.xlsx exactamente como hasta ahora, salvo por el efecto del 96 % en las cantidades.

**Non-Goals:**
- Hacer configurable el 96 % desde la ventana (el usuario prefirió un valor fijo).
- Reproducir los formatos sueltos de la plantilla de la fila 189 en adelante, o el relleno aislado de la columna C.
- Leer o escribir `.xls` en la entrada: los ficheros de entrada siguen siendo `.xlsx`.

## Decisions

### 1. Margen del 96 % dentro de `Medio`
Constante `LLENADO_MAXIMO = Fraction(96, 100)` en `modelo.py`. `Medio.peso_max` y `Medio.volumen_max` pasan a devolver `LLENADO_MAXIMO × n_medios × valor_de_la_tabla`, con aritmética exacta, sin coma flotante. La densidad no cambia.
- `seleccion.py` no se toca: ya usa esas propiedades.
- Para que la verificación siga siendo independiente, `verificacion.py` recalcula el límite a partir de `peso_unitario`, `volumen_unitario`, `n_medios` y la constante, en lugar de leer `peso_max`/`volumen_max`.
- Alternativa descartada: pasar el factor como parámetro de `seleccionar()`. Obliga a propagarlo por todo el código y hace posible olvidarlo en la verificación.

### 2. UNIxCAJA en el modelo y en la lectura
`Articulo` gana el campo `unidades_caja: int`.
- `lectura.py` exige D2 = `UNIXCAJA`, normalizado igual que el resto de encabezados.
- Cada valor debe ser entero ≥ 1: se admiten `18`, `18.0` y `"18"`; se rechazan vacío, `0`, negativos, `2,5` y texto. Un fallo en un solo artículo aborta el proceso y el mensaje indica la fila y la columna.
- Se aborta en lugar de avisar y excluir el artículo porque el valor sólo afecta al reparto en unidades. Excluirlo cambiaría la selección de cajas por un problema de datos que el usuario debe corregir.

### 3. Escritura del `.xls` con `xlwt`, generando desde cero
Nuevo módulo `reparto.py` con `construir_reparto(datos, selecciones) -> xlwt.Workbook` y `guardar_reparto(libro, destino)`.
- Estilos definidos con `xlwt.easyxf`, copiando los atributos medidos en la plantilla (sección Context). Las celdas sin elección se escriben como BLANK con el estilo de dato, igual que la plantilla, y se leen como vacías.
- Anchos de columna, alto de fila 315 y hojas `Hoja1`, `Hoja2` y `Hoja3`.
- Números como números: códigos de tienda y de artículo con formato `0`, unidades como enteros.
- Límite de BIFF8: 256 columnas. Se valida al principio que haya como máximo 255 tiendas.
- Alternativas descartadas:
  - `xlutils.copy` sobre la plantilla: arrastraría los restos de formato y obligaría a distribuir la plantilla, que además tiene metadatos de autor.
  - `pyexcel-xls`: usa xlwt por debajo y no da control de estilos.
  - LibreOffice en modo headless: no está en los equipos del usuario.

### 4. Guardado de los dos ficheros
`proceso.calcular()` construye en memoria los dos libros (openpyxl y xlwt) y verifica todo antes de escribir nada. `Calculo.guardar()` escribe PRUEBAESTANDAR.xlsx y después REPARTOESTANDAR.xls.
- Si falla cualquiera de las dos escrituras, se lanza `ErrorEscritura`, que nombra el fichero. Al reintentar se reescriben los dos (es idempotente) sin recalcular.
- `Resumen` gana `ruta_reparto` y `total_unidades`.

### 5. Ventana
- `gui.py` comprueba si existe cualquiera de las dos salidas y pide una única confirmación con los nombres de los ficheros que ya existen.
- El resumen muestra las dos rutas y las unidades totales. No hay cambios de disposición.

### 6. Dependencias y ejecutable
- `requirements.txt` añade `xlwt>=1.3` y `requirements-dev.txt` añade `xlrd>=2` para las pruebas.
- El workflow del `.exe` ya instala `requirements-dev.txt`. PyInstaller detecta `xlwt` por el import, así que el workflow no cambia.
- Comprobado en el entorno de desarrollo: `xlwt 1.3.0` en Python 3.12 escribe BIFF8 y `xlrd` lo relee con el texto `Código`, las hojas y los tipos numéricos correctos.

### 7. Pruebas
- **Selección:** los límites del 96 % (840 kg / 1248 L para PALET, 912 kg / 1152 L para CARRO) y un caso que cabía al 100 % y ya no cabe.
- **Verificación:** detecta el exceso sobre el 96 % y los valores de reparto incoherentes.
- **Lectura:** D2 distinto de UNIxCAJA y valores de UNIxCAJA no válidos.
- **Reparto:** se relee el `.xls` con xlrd y se comprueba lo siguiente.
  - Contenido y orden: `Código`, tiendas y artículos como números, unidades igual a cajas × UNIxCAJA, celdas vacías, filas de artículos no elegidos.
  - Formato: hojas, BIFF8, y para A1, B1, A2 y B2 la fuente, tamaño, negrita, bordes, relleno y formato numérico esperados; también anchos y alto de fila. Los atributos esperados van escritos en la prueba; la plantilla del usuario no se sube al repositorio.
- **Extremo a extremo y reintento:** con los dos ficheros; y la prueba de rendimiento de 650 × 180 incluye el `.xls`.

## Risks / Trade-offs

- [El programa de importación podría exigir algo de la plantilla que no se ve con xlrd, como el color del relleno de alguna columna o metadatos] → Mitigación: prueba de aceptación en la que el usuario importa un REPARTOESTANDAR.xls real. Si falla, se ajusta el estilo concreto.
- [`xlwt` no recibe mantenimiento desde 2017] → Es código Python puro y estable para BIFF8, y queda cubierto por las pruebas y por la compilación en Windows. Si algún día deja de funcionar, la escritura está aislada en `reparto.py`.
- [Menos carga por medio (−2,9 % de cajas con los datos de ejemplo)] → Es el objetivo del margen pedido.
- [Ficheros base antiguos (densidad en D) dejan de valer] → Error claro que indica que la columna D debe ser UNIxCAJA.

## Migration Plan

1. Actualizar a la nueva versión: nuevo zip del `.exe` desde GitHub Actions.
2. Usar el fichero base nuevo (UNIxCAJA en D) y la tabla de tiendas con los códigos nuevos.
3. Importar REPARTOESTANDAR.xls en el otro programa como prueba.

Vuelta atrás: el zip de la versión anterior sigue disponible en la ejecución de Actions anterior hasta que caduque.
