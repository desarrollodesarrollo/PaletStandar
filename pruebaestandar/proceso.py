from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import xlwt
from openpyxl.workbook import Workbook

from . import escritura, reparto
from .lectura import leer_fichero_base, leer_tabla_medios
from .modelo import Resumen
from .seleccion import parsear_dias, seleccionar
from .verificacion import verificar, verificar_reparto


@dataclass
class Calculo:
    """Resultado calculado y verificado, listo para guardar (o reintentar el guardado)."""

    libro: Workbook
    libro_reparto: xlwt.Workbook
    resumen: Resumen

    def guardar(self) -> Resumen:
        escritura.guardar(self.libro, self.resumen.ruta_salida)
        escritura.guardar(self.libro_reparto, self.resumen.ruta_reparto)
        return self.resumen


def rutas_salida(ruta_base) -> tuple[Path, Path]:
    return escritura.ruta_salida(Path(ruta_base)), reparto.ruta_reparto(Path(ruta_base))


def calcular(ruta_base, ruta_tabla, dias) -> Calculo:
    dias = parsear_dias(dias)
    destino, destino_reparto = rutas_salida(ruta_base)
    libro, datos = leer_fichero_base(Path(ruta_base))
    reparto.comprobar_limites(datos)
    medios = leer_tabla_medios(Path(ruta_tabla), [d.tienda for d in datos.tiendas])

    selecciones = {
        d.tienda: seleccionar(datos.articulos, d.bultos, d.lineas, medios[d.tienda], dias) for d in datos.tiendas
    }
    verificar(datos, medios, dias, selecciones)
    unidades = reparto.calcular_unidades(datos, selecciones)
    verificar_reparto(datos, selecciones, unidades)

    escritura.escribir_elecciones(libro, datos, selecciones)
    libro_reparto = reparto.construir_reparto(datos, unidades)

    resumen = Resumen(
        ruta_salida=destino,
        ruta_reparto=destino_reparto,
        tiendas_procesadas=len(datos.tiendas),
        tiendas_sin_seleccion=sum(1 for s in selecciones.values() if not s),
        total_cajas=sum(sum(s.values()) for s in selecciones.values()),
        total_unidades=sum(v for fila in unidades for v in fila if v is not None),
        avisos=list(datos.avisos),
    )
    return Calculo(libro=libro, libro_reparto=libro_reparto, resumen=resumen)


def ejecutar(ruta_base, ruta_tabla, dias) -> Resumen:
    return calcular(ruta_base, ruta_tabla, dias).guardar()
