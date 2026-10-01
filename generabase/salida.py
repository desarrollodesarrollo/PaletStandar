from __future__ import annotations

import os
from pathlib import Path

from .modelo import ErrorEscritura


def guardar_xlsx(libro, destino: Path) -> None:
    """Guarda en un temporal de la misma carpeta y lo renombra, para no dejar nunca un fichero a medias."""
    destino = Path(destino)
    temporal = destino.with_name(f".~{destino.stem}.tmp.xlsx")
    try:
        libro.save(str(temporal))
        os.replace(temporal, destino)
    except PermissionError:
        _borrar(temporal)
        raise ErrorEscritura(
            f"No se puede escribir {destino}. Si está abierto en Excel, ciérralo y pulsa Reintentar."
        ) from None
    except OSError as exc:
        _borrar(temporal)
        raise ErrorEscritura(f"No se puede escribir {destino}: {exc}") from None


def _borrar(ruta: Path) -> None:
    try:
        ruta.unlink()
    except OSError:
        pass
