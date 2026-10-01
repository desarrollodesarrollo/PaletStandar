from __future__ import annotations

NOMBRE_SALALM_FILTRADO = "SALALM FILTRADO.xlsx"
NOMBRE_FICHERO_BASE = "FICHERO BASE.xlsx"


class ErrorValidacion(Exception):
    """Datos de entrada no válidos; el mensaje se muestra tal cual al usuario."""


class ErrorEscritura(Exception):
    """No se pudo guardar una salida; se puede reintentar sin volver a leer."""
