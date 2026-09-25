from __future__ import annotations

import math
from fractions import Fraction

from .modelo import LLENADO_MAXIMO, Articulo, DatosBase, ErrorValidacion, Medio


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
    n_medios = 1 if medio.tipo == "PALET" else 2
    peso_max = LLENADO_MAXIMO * n_medios * Fraction(medio.peso_unitario)
    volumen_max = LLENADO_MAXIMO * n_medios * Fraction(medio.volumen_unitario)
    if peso > peso_max:
        errores.append(f"peso {float(peso):.2f} kg supera el máximo {float(peso_max):.2f} kg (96 %)")
    if volumen > volumen_max:
        errores.append(f"volumen {float(volumen):.2f} L supera el máximo {float(volumen_max):.2f} L (96 %)")
    if volumen > 0 and not peso / volumen < medio.densidad:
        errores.append(
            f"densidad {float(peso / volumen):.4f} kg/L no es menor que la del medio {float(medio.densidad):.4f} kg/L"
        )
    return errores


def verificar_reparto(datos: DatosBase, selecciones: dict, unidades: list) -> None:
    """Comprueba que cada celda del reparto es exactamente ELECCIÓN × UNIxCAJA (o vacía si no hay elección)."""
    fallos = []
    if len(unidades) != len(datos.articulos) or any(len(f) != len(datos.tiendas) for f in unidades):
        fallos.append("el reparto no tiene una fila por artículo y una columna por tienda")
    else:
        for c, demanda in enumerate(datos.tiendas):
            seleccion = selecciones.get(demanda.tienda, {})
            for i, art in enumerate(datos.articulos):
                esperado = seleccion[i] * art.unidades_caja if i in seleccion else None
                if unidades[i][c] != esperado or type(unidades[i][c]) not in (int, type(None)):
                    fallos.append(
                        f"Tienda {demanda.tienda}, artículo {art.codigo}: el reparto tiene {unidades[i][c]!r} "
                        f"unidades y deberían ser {esperado!r}"
                    )
    if fallos:
        raise ErrorValidacion(
            "La comprobación final del reparto en unidades ha fallado; no se ha guardado ningún fichero.\n"
            + "\n".join(fallos[:20])
        )


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
            "no se ha guardado ningún fichero.\n" + "\n".join(fallos)
        )
