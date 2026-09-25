from __future__ import annotations

from pathlib import Path

from openpyxl.workbook import Workbook

from .modelo import NOMBRE_SALIDA, DatosBase, ErrorEscritura, ErrorValidacion


def ruta_salida(ruta_base: Path) -> Path:
    ruta_base = Path(ruta_base)
    salida = ruta_base.parent / NOMBRE_SALIDA
    if ruta_base.name.lower() == NOMBRE_SALIDA.lower():
        raise ErrorValidacion(
            f"El fichero base no puede llamarse {NOMBRE_SALIDA}, porque la salida lo sobrescribiría. "
            "Cámbiale el nombre y vuelve a intentarlo."
        )
    return salida


def escribir_elecciones(wb: Workbook, datos: DatosBase, selecciones: dict) -> None:
    ws = wb.worksheets[0]
    for demanda in datos.tiendas:
        seleccion = selecciones.get(demanda.tienda, {})
        for i, art in enumerate(datos.articulos):
            ws.cell(row=art.fila, column=demanda.col_eleccion).value = seleccion.get(i)


def guardar(libro, destino: Path) -> None:
    """Guarda un libro de openpyxl o de xlwt (ambos tienen save(ruta))."""
    try:
        libro.save(str(destino))
    except PermissionError:
        raise ErrorEscritura(
            f"No se puede escribir {destino}. Si está abierto en Excel, ciérralo y pulsa Reintentar."
        ) from None
    except OSError as exc:
        raise ErrorEscritura(f"No se puede escribir {destino}: {exc}") from None
