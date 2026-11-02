# Proposal

## Why

Hoy el FICHERO BASE con el que trabaja PRUEBAESTANDAR se monta a mano: se cruzan las salidas del almacén (SALALM), el maestro de artículos y su glosario de caducidades, y los movimientos por tienda de un Access de cientos de MB. Es un proceso lento y fácil de equivocar. **GENERABASE** es una aplicación nueva e independiente que hace ese montaje automáticamente y deja además un SALALM depurado para consultarlo.

## What Changes

- Nueva aplicación de escritorio **GENERABASE**, independiente de PRUEBAESTANDAR: carpeta, ejecutable, pruebas y compilación propios. PRUEBAESTANDAR no se modifica.
- **Entradas** (en la ventana):
  - SALALM (.xlsx);
  - MAESTRO (.xlsx);
  - MAESTRO DE CADUCIDAD (.xlsx);
  - MOVIMIENTOS (Access .accdb/.mdb, tabla `MOVIMIENTOS`);
  - el nº de artículos que se quieren en el FICHERO BASE.
- **Lectura del Access sin controladores de Microsoft**, con comprobaciones en cada ejecución: nº de registros leídos frente al declarado por la tabla, columnas y tipos, y totales de control en pantalla. Con la copia de ejemplo (52.150 filas) la lectura coincide al 100 % con una segunda herramienta independiente.
- **Salida 1, `SALALM FILTRADO.xlsx`**:
  - Parte de SALALM y le añade la caducidad del MAESTRO y del MAESTRO DE CADUCIDAD. PESO va en kg (÷ 1000) y VOLUMEN en litros (÷ 1000). UBICACIÓN son las 3 primeras cifras de RADUBICA, como número, y TIPO DE UBICACIÓN se calcula con los tramos acordados.
  - Excluye las secciones «SUMINISTROS Y SERVICIOS» y «CAMPAÑA FIDELIDAD», las bajas («B»), las caducidades conocidas menores de 92 días, los artículos sin ubicación y los de «PASILLO ESTRECHO» y «BAZAR ABAJO».
  - Se ordena por CAJAS de mayor a menor.
- **Salida 2, `FICHERO BASE.xlsx`**:
  - Contiene los N artículos con más CAJAS de SALALM FILTRADO, con CODIGO, TIPO, PESO (Kg), Volumen (L) y UNIxCAJA.
  - Lleva un bloque BULTOS / LINEAS / ELECCIÓN por cada tienda de los movimientos «PI» de las tiendas 10081–10349 y 10399–10999 (código − 10000).
  - BULTOS = suma de |MVCANM| ÷ MVUNCA y LINEAS = nº de movimientos, por tienda y artículo; ELECCIÓN queda vacía.
  - El formato es el de la plantilla aportada.
- **Compatibilidad:** el FICHERO BASE sigue la plantilla, que lleva TIPO en la columna B. PRUEBAESTANDAR, tal como está hoy, **no lo acepta**: espera UNIxCAJA en la D. Adaptar PRUEBAESTANDAR será un cambio aparte y posterior, decidido por el usuario.

## Capabilities

### New Capabilities
- `generabase-lectura`: lectura y validación de los 3 Excel y del Access, con normalización de códigos y comprobaciones de la lectura del Access.
- `generabase-salalm-filtrado`: construcción, filtrado, ordenación y exportación de SALALM FILTRADO.xlsx.
- `generabase-fichero-base`: selección de los N artículos, agregación de los movimientos por tienda y exportación de FICHERO BASE.xlsx con el formato de la plantilla.
- `generabase-interfaz`: ventana para elegir los 4 ficheros y el nº de artículos, ejecutar y ver el resumen y los totales de control.

### Modified Capabilities
<!-- Ninguna: no cambia ninguna capacidad de PRUEBAESTANDAR. -->

## Impact

- **Código nuevo**:
  - paquete `generabase/` y arranque `GENERABASE.pyw`;
  - pruebas en `tests_generabase/`;
  - workflow `.github/workflows/compilar-generabase-exe.yml`;
  - `requirements-generabase.txt` con `openpyxl` y `access-parser` (Python puro, licencia Apache 2.0).
- **Ficheros compartidos que solo se amplían**: `pytest.ini` (nueva carpeta de pruebas), `README.md` (nueva sección) y `.gitignore` (formatos `.accdb`/`.mdb`). Los ficheros de dependencias y el workflow de PRUEBAESTANDAR no cambian, así que su `.exe` no se recompila.
- **Rendimiento**: con la copia de ejemplo la lectura del Access tarda 6 s y usa unos 150 MB. Para el Access real (417 MB) se estiman 2 minutos y unos 2 GB de memoria; se medirá en la aceptación.
