from __future__ import annotations

import math
from fractions import Fraction

from .modelo import Articulo, DatosBase, ErrorValidacion, Medio


def errores_tienda(
    articulos: list[Articulo],
    bultos: list[Fraction],
    medio: Medio,
    dias: int,
    seleccion: dict[int, int],
) -> list[str]:
    """Recalcula desde cero todas las restricciones, sin usar el estado del algoritmo."""
    errores = []
    peso = volumen = Fraction(0)
    for i, cajas in seleccion.items():
        if not 0 <= i < len(articulos):
            errores.append(f"índice de artículo inexistente {i}")
            continue
        art = articulos[i]
        if type(cajas) is not int or cajas < 1:
            errores.append(f"artículo {art.codigo}: nº de cajas no entero ≥ 1 ({cajas!r})")
            continue
        if not art.valido:
            errores.append(f"artículo {art.codigo}: sin peso o volumen válido")
        if not bultos[i] > 0:
            errores.append(f"artículo {art.codigo}: sin salida de bultos")
            continue
        maximo = math.ceil(Fraction(bultos[i]) / dias)
        if cajas > maximo:
            errores.append(f"artículo {art.codigo}: {cajas} cajas superan el máximo {maximo}")
        peso += cajas * Fraction(art.peso)
        volumen += cajas * Fraction(art.volumen)
    if peso > medio.peso_max:
        errores.append(f"peso {float(peso):.2f} kg supera el máximo {float(medio.peso_max):.2f} kg")
    if volumen > medio.volumen_max:
        errores.append(f"volumen {float(volumen):.2f} L supera el máximo {float(medio.volumen_max):.2f} L")
    if volumen > 0 and not peso / volumen < medio.densidad:
        errores.append(
            f"densidad {float(peso / volumen):.4f} kg/L no es menor que la del medio {float(medio.densidad):.4f} kg/L"
        )
    return errores


def verificar(datos: DatosBase, medios: dict, dias: int, selecciones: dict) -> None:
    """Lanza ErrorValidacion si alguna tienda incumple las restricciones."""
    fallos = []
    for demanda in datos.tiendas:
        errores = errores_tienda(
            datos.articulos, demanda.bultos, medios[demanda.tienda], dias, selecciones.get(demanda.tienda, {})
        )
        if errores:
            fallos.append(f"Tienda {demanda.tienda}: " + "; ".join(errores))
    if fallos:
        raise ErrorValidacion(
            "La comprobación final ha detectado selecciones que incumplen las restricciones; "
            "no se ha guardado el fichero.\n" + "\n".join(fallos)
        )
