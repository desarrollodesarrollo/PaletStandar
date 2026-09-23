from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl.workbook import Workbook

from . import escritura
from .lectura import leer_fichero_base, leer_tabla_medios
from .modelo import Resumen
from .seleccion import parsear_dias, seleccionar
from .verificacion import verificar


@dataclass
class Calculo:
    """Resultado calculado y verificado, listo para guardar (o reintentar el guardado)."""

    libro: Workbook
    resumen: Resumen

    def guardar(self) -> Resumen:
        escritura.guardar(self.libro, self.resumen.ruta_salida)
        return self.resumen


def calcular(ruta_base, ruta_tabla, dias) -> Calculo:
    dias = parsear_dias(dias)
    destino = escritura.ruta_salida(Path(ruta_base))
    libro, datos = leer_fichero_base(Path(ruta_base))
    medios = leer_tabla_medios(Path(ruta_tabla), [d.tienda for d in datos.tiendas])

    selecciones = {
        d.tienda: seleccionar(datos.articulos, d.bultos, d.lineas, medios[d.tienda], dias) for d in datos.tiendas
    }
    verificar(datos, medios, dias, selecciones)
    escritura.escribir_elecciones(libro, datos, selecciones)

    resumen = Resumen(
        ruta_salida=destino,
        tiendas_procesadas=len(datos.tiendas),
        tiendas_sin_seleccion=sum(1 for s in selecciones.values() if not s),
        total_cajas=sum(sum(s.values()) for s in selecciones.values()),
        avisos=list(datos.avisos),
    )
    return Calculo(libro=libro, resumen=resumen)


def ejecutar(ruta_base, ruta_tabla, dias) -> Resumen:
    return calcular(ruta_base, ruta_tabla, dias).guardar()
