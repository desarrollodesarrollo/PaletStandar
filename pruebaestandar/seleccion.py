from __future__ import annotations

import heapq
import math
import re
from fractions import Fraction

from .modelo import Articulo, ErrorValidacion, Medio

_ENTERO = re.compile(r"^\+?\d+$")


def parsear_dias(texto) -> int:
    texto = "" if texto is None else str(texto).strip()
    if not _ENTERO.match(texto) or int(texto) < 1:
        raise ErrorValidacion("El nº de días debe ser un número entero mayor que 0.")
    return int(texto)


def maximo_cajas(bultos: Fraction, dias: int) -> int:
    return math.ceil(Fraction(bultos) / dias)


def _clave_codigo(codigo):
    return (0, codigo, "") if isinstance(codigo, int) else (1, 0, str(codigo))


def _clave(art: Articulo, idx: int, lineas: Fraction, bultos: Fraction, cajas: int):
    # Mayor índice LÍNEAS/(cajas+1); empates: sin cajas, más líneas, más bultos, menor volumen, menor código.
    return (
        -Fraction(lineas) / (cajas + 1),
        cajas > 0,
        -lineas,
        -bultos,
        art.volumen,
        _clave_codigo(art.codigo),
        idx,
    )


def seleccionar(
    articulos: list[Articulo],
    bultos: list[Fraction],
    lineas: list[Fraction],
    medio: Medio,
    dias: int,
) -> dict[int, int]:
    """Devuelve {índice de artículo: nº de cajas} para una tienda."""
    peso_max, vol_max, densidad = medio.peso_max, medio.volumen_max, medio.densidad
    maximos = {}
    cola = []
    for i, art in enumerate(articulos):
        if art.valido and bultos[i] > 0:
            maximos[i] = maximo_cajas(bultos[i], dias)
            heapq.heappush(cola, _clave(art, i, lineas[i], bultos[i], 0))

    cajas: dict[int, int] = {}
    peso = vol = Fraction(0)
    # Aparcados por densidad, ordenados por la holgura que necesitan: holgura = d·V − P.
    aparcados: list = []
    while cola:
        clave = heapq.heappop(cola)
        i = clave[-1]
        art = articulos[i]
        nuevo_peso, nuevo_vol = peso + art.peso, vol + art.volumen
        if nuevo_peso > peso_max or nuevo_vol > vol_max:
            continue  # los totales sólo crecen: esta caja ya nunca cabrá
        if not nuevo_peso < densidad * nuevo_vol:
            heapq.heappush(aparcados, (art.peso - densidad * art.volumen, clave))
            continue
        peso, vol = nuevo_peso, nuevo_vol
        q = cajas[i] = cajas.get(i, 0) + 1
        if q < maximos[i]:
            heapq.heappush(cola, _clave(art, i, lineas[i], bultos[i], q))
        holgura = densidad * vol - peso
        while aparcados and aparcados[0][0] < holgura:
            heapq.heappush(cola, heapq.heappop(aparcados)[1])
    return cajas
