from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

NOMBRE_SALIDA = "PRUEBAESTANDAR.xlsx"
NOMBRE_REPARTO = "REPARTOESTANDAR.xls"
LLENADO_MAXIMO = Fraction(96, 100)


class ErrorValidacion(Exception):
    """Datos de entrada no válidos; el mensaje se muestra tal cual al usuario."""


class ErrorEscritura(Exception):
    """No se pudo guardar la salida; se puede reintentar sin recalcular."""


@dataclass(frozen=True)
class Articulo:
    fila: int
    codigo: object
    peso: Fraction
    volumen: Fraction
    valido: bool
    unidades_caja: int


@dataclass(frozen=True)
class Medio:
    tipo: str
    peso_unitario: Fraction
    volumen_unitario: Fraction
    densidad: Fraction

    @property
    def n_medios(self) -> int:
        return 1 if self.tipo == "PALET" else 2

    @property
    def peso_max(self) -> Fraction:
        return LLENADO_MAXIMO * self.n_medios * self.peso_unitario

    @property
    def volumen_max(self) -> Fraction:
        return LLENADO_MAXIMO * self.n_medios * self.volumen_unitario


@dataclass
class DemandaTienda:
    tienda: object
    col_eleccion: int
    bultos: list[Fraction]
    lineas: list[Fraction]


@dataclass
class DatosBase:
    articulos: list[Articulo]
    tiendas: list[DemandaTienda]
    avisos: list[str] = field(default_factory=list)


@dataclass
class Resumen:
    ruta_salida: Path
    ruta_reparto: Path
    tiendas_procesadas: int
    tiendas_sin_seleccion: int
    total_cajas: int
    total_unidades: int
    avisos: list[str]

    def texto(self) -> str:
        lineas = [
            "Ficheros generados:",
            f"  {self.ruta_salida}",
            f"  {self.ruta_reparto}",
            f"Tiendas procesadas: {self.tiendas_procesadas}",
            f"Tiendas sin selección: {self.tiendas_sin_seleccion}",
            f"Total de cajas seleccionadas: {self.total_cajas}",
            f"Total de unidades: {self.total_unidades}",
        ]
        if self.avisos:
            lineas.append(f"Avisos ({len(self.avisos)}):")
            lineas.extend(f"  - {a}" for a in self.avisos)
        else:
            lineas.append("Sin avisos.")
        return "\n".join(lineas)
