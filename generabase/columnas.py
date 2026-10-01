"""Búsqueda de columnas por encabezado y normalización de valores de celda."""

from __future__ import annotations

from .modelo import ErrorValidacion


def normalizar(texto) -> str:
    return "" if texto is None else str(texto).strip().upper()


def indice(encabezados, necesarias, fichero: str) -> dict[str, int]:
    """Posición de cada columna necesaria, buscada por nombre sin distinguir mayúsculas ni espacios."""
    posiciones = {}
    for i, h in enumerate(encabezados):
        posiciones.setdefault(normalizar(h), i)
    faltan = [c for c in necesarias if normalizar(c) not in posiciones]
    if faltan:
        raise ErrorValidacion(
            f"Falta la columna {', '.join(faltan)} en el fichero {fichero}."
            if len(faltan) == 1
            else f"Faltan las columnas {', '.join(faltan)} en el fichero {fichero}."
        )
    return {c: posiciones[normalizar(c)] for c in necesarias}


def entero(valor) -> int | None:
    """Código como entero: admite 273137, 273137.0 y '000010389'; cualquier otra cosa devuelve None."""
    if isinstance(valor, bool) or valor is None:
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        return int(valor) if valor.is_integer() else None
    texto = str(valor).strip()
    if texto.isdigit():
        return int(texto)
    try:
        numero = float(texto)
    except ValueError:
        return None
    return int(numero) if numero.is_integer() else None


def numero(valor) -> float | int | None:
    """Valor numérico de una celda; admite texto con coma decimal. None si no es numérico."""
    if isinstance(valor, bool) or valor is None:
        return None
    if isinstance(valor, (int, float)):
        return valor
    texto = str(valor).strip().replace(",", ".")
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def codigo_texto(valor) -> str:
    """Código de caducidad comparable: 1, 1.0 y ' 1 ' dan '1'."""
    if valor is None:
        return ""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return str(valor).strip()


def texto(valor) -> str:
    return "" if valor is None else str(valor).strip()
