"""REPARTOESTANDAR.xls: elección de cada tienda en unidades, con el formato de la plantilla del importador."""

from __future__ import annotations

from pathlib import Path

import xlwt

from .modelo import NOMBRE_REPARTO, DatosBase, ErrorValidacion

MAX_TIENDAS = 255  # BIFF8 admite 256 columnas y la A es el código de artículo
MAX_ARTICULOS = 65535  # BIFF8 admite 65536 filas y la 1 es el encabezado

_BORDE = "borders: left thin, right thin, top thin, bottom thin"
# Atributos medidos en PLANTILLA.xls (xf62, xf64, xf79 y xf80).
ESTILO_CABECERA_CODIGO = xlwt.easyxf(
    f"font: name Arial, height 240, bold on, colour black; {_BORDE}; "
    "pattern: pattern solid, fore_colour pale_blue; align: horiz center, vert bottom"
)
ESTILO_CABECERA_TIENDA = xlwt.easyxf(f"font: name Arial, height 200, bold on, colour blue; {_BORDE}")
ESTILO_CODIGO_ARTICULO = xlwt.easyxf(f"font: name Arial, height 200; {_BORDE}", num_format_str="0")
ESTILO_DATO = xlwt.easyxf(f"font: name Arial, height 240, bold on; {_BORDE}")
ANCHO_COLUMNA_A = 2304
ANCHO_COLUMNA_TIENDA = 1024
ALTO_FILA = 315


def ruta_reparto(ruta_base: Path) -> Path:
    return Path(ruta_base).parent / NOMBRE_REPARTO


def comprobar_limites(datos: DatosBase) -> None:
    if len(datos.tiendas) > MAX_TIENDAS:
        raise ErrorValidacion(
            f"El fichero base tiene {len(datos.tiendas)} tiendas y {NOMBRE_REPARTO} (formato .xls) admite "
            f"como máximo {MAX_TIENDAS}. Divide el fichero base en varios."
        )
    if len(datos.articulos) > MAX_ARTICULOS:
        raise ErrorValidacion(
            f"El fichero base tiene {len(datos.articulos)} artículos y {NOMBRE_REPARTO} (formato .xls) admite "
            f"como máximo {MAX_ARTICULOS}."
        )


def calcular_unidades(datos: DatosBase, selecciones: dict) -> list[list[int | None]]:
    """Matriz artículo × tienda con ELECCIÓN × UNIxCAJA, o None si no se elige."""
    matriz = []
    for i, art in enumerate(datos.articulos):
        fila = []
        for demanda in datos.tiendas:
            cajas = selecciones.get(demanda.tienda, {}).get(i)
            fila.append(None if cajas is None else cajas * art.unidades_caja)
        matriz.append(fila)
    return matriz


def construir_reparto(datos: DatosBase, unidades: list[list[int | None]]) -> xlwt.Workbook:
    libro = xlwt.Workbook(encoding="utf-8")
    hoja = libro.add_sheet("Hoja1")
    libro.add_sheet("Hoja2")
    libro.add_sheet("Hoja3")

    hoja.col(0).width = ANCHO_COLUMNA_A
    for c in range(1, len(datos.tiendas) + 1):
        hoja.col(c).width = ANCHO_COLUMNA_TIENDA
    for r in range(len(datos.articulos) + 1):
        fila = hoja.row(r)
        fila.height_mismatch = True
        fila.height = ALTO_FILA

    hoja.write(0, 0, "Código", ESTILO_CABECERA_CODIGO)
    for c, demanda in enumerate(datos.tiendas, start=1):
        hoja.write(0, c, demanda.tienda, ESTILO_CABECERA_TIENDA)
    for r, (art, valores) in enumerate(zip(datos.articulos, unidades), start=1):
        hoja.write(r, 0, art.codigo, ESTILO_CODIGO_ARTICULO)
        for c, valor in enumerate(valores, start=1):
            hoja.write(r, c, valor, ESTILO_DATO)
    return libro
