"""Lectura de la tabla MOVIMIENTOS de un Access (.accdb/.mdb) sin controladores, y filtro de movimientos."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from access_parser import AccessParser

from .columnas import entero, normalizar, numero, texto
from .modelo import ErrorValidacion

TABLA = "MOVIMIENTOS"
COLUMNAS = ("MVARTI", "MVTMOV", "MVDESM", "MVCANM", "MVUNCA")
OPCIONAL_FECHA = "MVFECI"
RANGOS_TIENDA = ((10081, 10349), (10399, 10999))
DESPLAZAMIENTO_TIENDA = 10000


@dataclass
class Movimientos:
    columnas: dict[str, list]
    filas_leidas: int
    filas_declaradas: int


@dataclass
class MovimientosUsados:
    lineas: list[tuple[int, int, float]]  # (artículo, tienda sin 10000, cajas)
    filas_leidas: int
    filas_declaradas: int
    filas_pi: int = 0
    filas_en_rango: int = 0
    sin_unidades_caja: int = 0
    articulo_no_valido: int = 0
    tienda_no_valida: int = 0
    fecha_min: int | None = None
    fecha_max: int | None = None
    avisos: list[str] = field(default_factory=list)

    @property
    def tiendas(self) -> list[int]:
        return sorted({t for _, t, _ in self.lineas})

    @property
    def articulos(self) -> int:
        return len({a for a, _, _ in self.lineas})

    @property
    def total_cajas(self) -> float:
        return math.fsum(c for _, _, c in self.lineas)


def _tablas_de_usuario(db) -> list[str]:
    return sorted(t for t in db.catalog if not t.startswith(("MSys", "f_")))


def leer_movimientos(ruta: Path) -> Movimientos:
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorValidacion(f"No se encuentra el fichero de MOVIMIENTOS: {ruta}")
    try:
        db = AccessParser(str(ruta))
    except PermissionError:
        raise ErrorValidacion(f"No se puede abrir el Access (¿está abierto en otro programa?): {ruta}") from None
    except Exception as exc:
        raise ErrorValidacion(
            f"No se puede leer el fichero de MOVIMIENTOS como base de Access (.accdb/.mdb). "
            f"Puede estar dañado, protegido con contraseña o no ser un Access: {ruta} ({exc})"
        ) from None

    tablas = _tablas_de_usuario(db)
    nombre = next((t for t in tablas if normalizar(t) == TABLA), None)
    if nombre is None:
        raise ErrorValidacion(
            f"El Access no contiene la tabla {TABLA}. Tablas encontradas: {', '.join(tablas) or '(ninguna)'}."
        )
    try:
        datos = db.parse_table(nombre)
        declaradas = int(db.get_table(nombre).table_header["number_of_rows"])
    except Exception as exc:
        raise ErrorValidacion(f"No se ha podido leer la tabla {TABLA} del Access: {exc}") from None

    por_nombre = {normalizar(c): c for c in datos}
    faltan = [c for c in COLUMNAS if c not in por_nombre]
    if faltan:
        raise ErrorValidacion(f"Falta la columna {', '.join(faltan)} en la tabla {TABLA} del Access.")
    longitudes = {c: len(v) for c, v in datos.items()}
    if len(set(longitudes.values())) > 1:
        detalle = ", ".join(f"{c}: {n}" for c, n in sorted(longitudes.items(), key=lambda x: x[1])[:5])
        raise ErrorValidacion(f"La lectura de la tabla {TABLA} está incompleta: las columnas tienen distinto nº de valores ({detalle}…).")
    leidas = next(iter(longitudes.values()), 0)
    if leidas != declaradas:
        raise ErrorValidacion(
            f"La lectura de la tabla {TABLA} está incompleta: leídas {leidas:,} filas de {declaradas:,} declaradas "
            "por el Access. No se ha generado ningún fichero.".replace(",", ".")
        )

    conservar = list(COLUMNAS) + ([OPCIONAL_FECHA] if OPCIONAL_FECHA in por_nombre else [])
    columnas = {c: datos[por_nombre[c]] for c in conservar}
    datos.clear()
    return Movimientos(columnas=columnas, filas_leidas=leidas, filas_declaradas=declaradas)


def _en_rango(tienda: int) -> bool:
    return any(a <= tienda <= b for a, b in RANGOS_TIENDA)


def filtrar(movimientos: Movimientos) -> MovimientosUsados:
    """Sólo PI de las tiendas en rango; CAJAS = |MVCANM| / MVUNCA."""
    c = movimientos.columnas
    usados = MovimientosUsados(lineas=[], filas_leidas=movimientos.filas_leidas, filas_declaradas=movimientos.filas_declaradas)
    fechas = c.get(OPCIONAL_FECHA)
    for i in range(movimientos.filas_leidas):
        if normalizar(c["MVTMOV"][i]) != "PI":
            continue
        usados.filas_pi += 1
        tienda = entero(c["MVDESM"][i])
        if tienda is None:
            usados.tienda_no_valida += 1
            continue
        if not _en_rango(tienda):
            continue
        usados.filas_en_rango += 1
        articulo = entero(c["MVARTI"][i])
        if articulo is None:
            usados.articulo_no_valido += 1
            continue
        cantidad, unidades = c["MVCANM"][i], c["MVUNCA"][i]
        if numero(cantidad) is None:
            raise ErrorValidacion(
                f"Tabla {TABLA}, fila {i + 1}: MVCANM '{texto(cantidad)}' no es un número (artículo {articulo}, tienda {tienda})."
            )
        if unidades is not None and numero(unidades) is None:
            raise ErrorValidacion(
                f"Tabla {TABLA}, fila {i + 1}: MVUNCA '{texto(unidades)}' no es un número (artículo {articulo}, tienda {tienda})."
            )
        if unidades is None or numero(unidades) <= 0:
            usados.sin_unidades_caja += 1
            continue
        usados.lineas.append((articulo, tienda - DESPLAZAMIENTO_TIENDA, abs(numero(cantidad)) / numero(unidades)))
        if fechas is not None:
            fecha = entero(fechas[i])
            if fecha is not None:
                usados.fecha_min = fecha if usados.fecha_min is None else min(usados.fecha_min, fecha)
                usados.fecha_max = fecha if usados.fecha_max is None else max(usados.fecha_max, fecha)

    for n, motivo in (
        (usados.tienda_no_valida, "con código de tienda (MVDESM) no numérico"),
        (usados.articulo_no_valido, "con código de artículo (MVARTI) no numérico"),
        (usados.sin_unidades_caja, "sin unidades por caja (MVUNCA vacío o ≤ 0)"),
    ):
        if n:
            usados.avisos.append(f"Access: {n} movimientos PI {motivo}; no se usan.")
    return usados
