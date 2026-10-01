from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from openpyxl import Workbook

from . import access, fichero_base, lectura, salalm
from .salida import guardar_xlsx


def _es(valor, decimales: int = 0) -> str:
    """Número con formato español: 12.345,50."""
    return f"{valor:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _miles(n) -> str:
    return _es(n)


def _fecha(aaaammdd: int | None) -> str:
    s = str(aaaammdd or "")
    return f"{s[6:8]}/{s[4:6]}/{s[:4]}" if len(s) == 8 else s


@dataclass
class Resumen:
    ruta_salalm: Path
    ruta_base: Path
    filas_salalm: int
    filas_filtradas: int
    excluidas: dict
    sin_maestro: int
    articulos_base: int
    tiendas_base: int
    bultos_base: float
    lineas_base: int
    movimientos: access.MovimientosUsados
    avisos: list[str] = field(default_factory=list)

    def texto(self) -> str:
        m = self.movimientos
        lineas = [
            "Ficheros generados:",
            f"  {self.ruta_salalm}",
            f"  {self.ruta_base}",
            "",
            f"SALALM FILTRADO: {_miles(self.filas_filtradas)} artículos de {_miles(self.filas_salalm)} "
            f"({_miles(self.sin_maestro)} de ellos no están en el MAESTRO).",
            "  Excluidos por: " + ", ".join(f"{k} {_miles(v)}" for k, v in self.excluidas.items()),
            f"FICHERO BASE: {_miles(self.articulos_base)} artículos × {_miles(self.tiendas_base)} tiendas; "
            f"{_es(self.bultos_base, 2)} bultos y {_miles(self.lineas_base)} líneas.",
            "",
            "Totales de control del Access (tabla MOVIMIENTOS):",
            f"  Filas leídas / declaradas: {_miles(m.filas_leidas)} / {_miles(m.filas_declaradas)}",
            f"  Filas PI: {_miles(m.filas_pi)}  ·  PI en rangos de tienda: {_miles(m.filas_en_rango)}  ·  usadas: {_miles(len(m.lineas))}",
            f"  Tiendas: {_miles(len(m.tiendas))}  ·  artículos distintos: {_miles(m.articulos)}",
            f"  Suma de CAJAS: {_es(m.total_cajas, 2)}  ·  LINEAS: {_miles(len(m.lineas))}",
        ]
        if m.fecha_min is not None:
            lineas.append(f"  Fechas (MVFECI): {_fecha(m.fecha_min)} – {_fecha(m.fecha_max)}")
        lineas.append("")
        if self.avisos:
            lineas.append(f"Avisos ({len(self.avisos)}):")
            lineas.extend(f"  - {a}" for a in self.avisos[:200])
            if len(self.avisos) > 200:
                lineas.append(f"  … y {len(self.avisos) - 200} más.")
        else:
            lineas.append("Sin avisos.")
        return "\n".join(lineas)


@dataclass
class Calculo:
    libro_salalm: Workbook
    libro_base: Workbook
    resumen: Resumen

    def guardar(self) -> Resumen:
        guardar_xlsx(self.libro_salalm, self.resumen.ruta_salalm)
        guardar_xlsx(self.libro_base, self.resumen.ruta_base)
        return self.resumen


def rutas_salida(ruta_salalm) -> tuple[Path, Path]:
    return salalm.ruta_salalm_filtrado(ruta_salalm), fichero_base.ruta_fichero_base(ruta_salalm)


def calcular(ruta_salalm, ruta_maestro, ruta_caducidad, ruta_access, n, progreso: Callable[[str], None] = lambda _: None) -> Calculo:
    n = fichero_base.parsear_n(n)
    ruta_salida_salalm, ruta_salida_base = rutas_salida(ruta_salalm)

    progreso("Leyendo SALALM…")
    articulos, avisos = lectura.leer_salalm(Path(ruta_salalm))
    progreso("Leyendo MAESTRO…")
    maestro, avisos_maestro = lectura.leer_maestro(Path(ruta_maestro))
    progreso("Leyendo MAESTRO DE CADUCIDAD…")
    caducidades = lectura.leer_caducidades(Path(ruta_caducidad))
    progreso("Leyendo el Access (puede tardar unos minutos)…")
    usados = access.filtrar(access.leer_movimientos(Path(ruta_access)))

    progreso("Cruzando datos…")
    filas, avisos_cruce = salalm.construir(articulos, maestro, caducidades)
    filtradas, excluidas = salalm.filtrar(filas)

    progreso("Generando FICHERO BASE…")
    elegidos, aviso_n = fichero_base.seleccionar(filtradas, n)
    tiendas, agregado = fichero_base.agregar(elegidos, usados)
    libro_base = fichero_base.construir_libro(elegidos, tiendas, agregado)
    bultos, lineas = fichero_base.verificar_totales(libro_base, elegidos, usados)
    libro_salalm = salalm.construir_libro(filtradas)

    todos_avisos = ([aviso_n] if aviso_n else []) + usados.avisos + avisos + avisos_maestro + avisos_cruce
    resumen = Resumen(
        ruta_salalm=ruta_salida_salalm,
        ruta_base=ruta_salida_base,
        filas_salalm=len(filas),
        filas_filtradas=len(filtradas),
        excluidas=dict(excluidas),
        sin_maestro=sum(1 for f in filtradas if not f.en_maestro),
        articulos_base=len(elegidos),
        tiendas_base=len(tiendas),
        bultos_base=bultos,
        lineas_base=lineas,
        movimientos=usados,
        avisos=todos_avisos,
    )
    return Calculo(libro_salalm=libro_salalm, libro_base=libro_base, resumen=resumen)


def ejecutar(*args, **kwargs) -> Resumen:
    progreso = kwargs.get("progreso")
    calculo = calcular(*args, **kwargs)
    if progreso:
        progreso("Guardando…")
    return calculo.guardar()
