# Tasks

## 1. Preparación del proyecto

- [x] 1.1 Crear el paquete `pruebaestandar/` (`__init__.py`, `__main__.py`, `modelo.py`, `lectura.py`, `seleccion.py`, `verificacion.py`, `escritura.py`, `proceso.py`, `gui.py`), `tests/`, `requirements.txt` (`openpyxl`) y `requirements-dev.txt` (`pytest`); verificar que `python -c "import pruebaestandar"` funciona y `pytest` arranca sin errores
- [x] 1.2 Añadir `.gitignore` (entornos virtuales, `__pycache__`, `*.xlsx` fuera de `tests/`, `graphify-out/`) para no subir los ficheros reales de ejemplo; verificar con `git status` que un `.xlsx` en la raíz queda ignorado
- [x] 1.3 Crear en `tests/conftest.py` un generador de libros sintéticos (fichero base con N artículos y M tiendas, y tabla de tiendas) reutilizable por todas las pruebas; verificar con una prueba que genera 3 artículos × 2 tiendas y lo relee

## 2. Modelo y lectura de ficheros

- [x] 2.1 Implementar en `modelo.py` las dataclasses `Articulo`, `Medio`, `DemandaTienda` y `Resultado`, y la excepción `ErrorValidacion`; verificar con una prueba que `Medio` de CARRO expone 2 × peso y 2 × volumen
- [x] 2.2 Implementar la lectura del fichero base (fila 1 tiendas, fila 2 encabezados, bloques de 3 columnas desde E, vacíos = 0, normalización de códigos) y verificar con pruebas de 130 × 180 y 977 × 3 sintéticos
- [x] 2.3 Implementar las validaciones del fichero base (encabezados de bloque, código de tienda distinto dentro del bloque, tienda repetida, columnas no múltiplo de 3, BULTOS/LINEAS negativos o texto) con mensajes que citen columna/fila; verificar con una prueba por cada caso
- [x] 2.4 Marcar como no seleccionables los artículos con peso o volumen vacío, no numérico o ≤ 0 y registrarlos como avisos; verificar con una prueba de artículo con volumen 0
- [x] 2.5 Implementar la lectura y validación de la tabla de tiendas y medios (PALET/CARRO sin distinguir mayúsculas, valores > 0, tiendas del base que faltan listadas todas, tiendas sobrantes ignoradas); verificar con pruebas de tabla con más tiendas, tiendas que faltan y tipo `CAMION`

## 3. Algoritmo de selección

- [x] 3.1 Implementar el cálculo de días (entero ≥ 1, rechazar `0`, `-3`, `2,5`, `abc`, vacío) y del máximo `ceil(BULTOS/días)` con aritmética exacta; verificar con pruebas 10/5 → 2, 7/5 → 2, 1/20 → 1
- [x] 3.2 Implementar `seleccionar()` con cola de prioridad por índice LÍNEAS/(cajas+1), desempates (sin cajas, más líneas, menor volumen, menor código), descarte definitivo por peso/volumen y lista de espera por densidad; verificar con la prueba "A 10 líneas, B 4 líneas, caben 3 cajas → A=2, B=1"
- [x] 3.3 Añadir pruebas de los escenarios de la spec `seleccion-bultos`: caja que no cabe no bloquea al resto, artículo denso compensado por ligeros, selección demasiado densa rechazada, todo cabe → todos al máximo, tienda sin elegibles vacía, artículo sin salida nunca elegido; verificar que todas pasan
- [x] 3.4 Añadir prueba de determinismo (dos ejecuciones idénticas) y prueba de propiedades con 200 tiendas aleatorias con semilla fija que compruebe enteros, máximos, peso, volumen y densidad; verificar que pasan
- [x] 3.5 Añadir el desempate por más BULTOS de salida en la tienda (tras "más líneas" y antes de "menor volumen"); verificar con la prueba "tres artículos de 1 línea con 12, 3 y 7 bultos y sitio para 1 caja → el de 12"

## 4. Verificación y escritura de la salida

- [x] 4.1 Implementar `verificacion.py`, independiente del algoritmo, que compruebe enteros ≥ 1, cajas ≤ máximo, sólo elegibles, peso, volumen y densidad estricta por tienda; verificar con pruebas que detecten una selección que supera el volumen en la tienda 10082 y otra demasiado densa
- [x] 4.2 Implementar `escritura.py`: escribir ELECCIÓN como número entero en la copia (vaciar las no seleccionadas aunque tuvieran valor) y guardar `PRUEBAESTANDAR.xlsx` en la carpeta del fichero base sin tocar el original; verificar con una prueba que compara todas las celdas no ELECCIÓN, anchos de columna y el hash del fichero original antes/después
- [x] 4.3 Implementar `proceso.py` (lectura → selección por tienda → verificación → escritura) y el resumen (tiendas procesadas, tiendas sin selección, total de cajas, avisos); verificar con una prueba de extremo a extremo sobre un libro sintético de 20 × 5
- [x] 4.4 Gestionar el error de escritura por fichero abierto (`PermissionError`) devolviendo un error reintentable sin repetir el cálculo; verificar con una prueba que simula el fallo en el primer guardado y el éxito en el segundo
- [x] 4.5 Prueba de rendimiento con datos sintéticos de 650 artículos × 180 tiendas; verificar que el proceso completo tarda menos de 60 s

## 5. Interfaz gráfica

- [x] 5.1 Implementar la ventana `PRUEBAESTANDAR` en `gui.py` (dos selectores `.xlsx` con el nombre elegido, caja de días, botón Ejecutar, textos en español) y `PRUEBAESTANDAR.pyw` en la raíz; verificar abriéndola con `python -m pruebaestandar`
- [x] 5.2 Añadir validaciones previas (falta algún fichero, días no válidos) con mensajes claros; verificar a mano los casos "falta la tabla" y "días = cinco"
- [x] 5.3 Ejecutar el proceso en un hilo secundario con botón desactivado e indicador de progreso, confirmación antes de sobrescribir `PRUEBAESTANDAR.xlsx` y diálogo Reintentar/Cancelar si el fichero está abierto; verificar a mano que la ventana responde durante el cálculo y que responder `No` deja el fichero existente intacto
- [x] 5.4 Mostrar al terminar la ruta del fichero generado y el resumen, y los errores de validación sin trazas técnicas dejando la ventana lista para reintentar; verificar a mano con una tabla a la que le faltan tiendas y luego con la correcta

## 6. Aceptación y documentación

- [x] 6.1 Ejecutar con los ficheros reales de ejemplo (`FICHERO_BASE_AR.xlsx` y `TABLA_DE_TIENDAS_Y_MEDIOS.xlsx`) y varios nº de días (1, 5, 20); verificar que la verificación pasa en las 180 tiendas y revisar a mano con el usuario 2 tiendas PALET y 2 CARRO (kg, L, densidad y reparto por líneas)
- [x] 6.2 Escribir `README.md` en español con requisitos, instalación (`pip install -r requirements.txt`), uso (doble clic en `PRUEBAESTANDAR.pyw`), formato esperado de los ficheros y reglas de selección; verificar que una persona puede seguirlo desde cero
- [x] 6.3 Ejecutar `pytest` completo y `graphify update .`; verificar que todas las pruebas pasan
