"""PRUEBAESTANDAR unificado: genera SALALM FILTRADO y FICHERO BASE (GENERABASE) y calcula el palet estándar de un TIPO.

Flujo:
1. ``preparar``: parte GENERABASE (lectura de los 3 Excel y del Access, top N, FICHERO BASE). Es lo que tarda
   (la lectura del Access); su resultado (``Datos``) se puede reutilizar para calcular otro TIPO.
2. ``calcular_tipo``: filtra los N artículos por TIPO, forma la base del TIPO con la estructura antigua de
   PRUEBAESTANDAR (sin la columna TIPO), cuenta los días (MVFECI distintos de las filas PI) y ejecuta el
   cálculo de siempre. Devuelve un ``CalculoIntegrado`` listo para guardar los 4 ficheros.
"""

from __future__ import annotations

import os
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, NamedTuple

from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from generabase import fichero_base
from generabase import modelo as modelo_gb
from generabase import proceso as proceso_gb
from generabase.proceso import _fecha, _miles
from generabase.salida import guardar_xlsx

from . import proceso
from .modelo import ErrorEscritura, ErrorValidacion

TIPOS = ("ALTA ROTACIÓN", "DROGUERÍA", "ALIMENTACIÓN")
ABREVIATURAS = {"ALTA ROTACIÓN": "AR", "DROGUERÍA": "DR", "ALIMENTACIÓN": "AL"}

# Los dos paquetes tienen sus propias excepciones; la ventana trata ambas igual.
ERRORES_VALIDACION = (ErrorValidacion, modelo_gb.ErrorValidacion)
ERRORES_ESCRITURA = (ErrorEscritura, modelo_gb.ErrorEscritura)

# Columnas de la base del TIPO (estructura antigua): A CODIGO, B PESO, C Volumen, D UNIxCAJA, tiendas desde E.
COLUMNAS_ARTICULO_TIPO = 4
ANCHOS_TIPO = {
    "A": fichero_base.ANCHOS["A"],
    "B": fichero_base.ANCHOS["C"],
    "C": fichero_base.ANCHOS["D"],
    "D": fichero_base.ANCHOS["E"],
}

Progreso = Callable[[str], None]


def _sin_progreso(_: str) -> None:
    pass


def normalizar_tipo(valor) -> str:
    """Mayúsculas, sin tildes y con los espacios reducidos a uno: «Alta  rotacion» → «ALTA ROTACION»."""
    texto = "" if valor is None else " ".join(str(valor).split()).upper()
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def tipo_canonico(tipo) -> str:
    buscado = normalizar_tipo(tipo)
    for t in TIPOS:
        if normalizar_tipo(t) == buscado:
            return t
    raise ErrorValidacion("Elige el TIPO de palet estándar: ALTA ROTACIÓN, DROGUERÍA o ALIMENTACIÓN.")


def filtrar_tipo(elegidos: list, tipo: str, n_pedido: int | None = None) -> list:
    """Artículos del FICHERO BASE de ese TIPO, en el mismo orden."""
    tipo = tipo_canonico(tipo)
    buscado = normalizar_tipo(tipo)
    del_tipo = [a for a in elegidos if normalizar_tipo(a.tipo_ubicacion) == buscado]
    if not del_tipo:
        n = len(elegidos) if n_pedido is None else n_pedido
        raise ErrorValidacion(
            f"No hay artículos de {tipo} entre los {_miles(len(elegidos))} artículos del FICHERO BASE "
            f"(nº de artículos pedido: {_miles(n)}). Prueba con un nº de artículos mayor. "
            "No se ha generado ningún fichero."
        )
    return del_tipo


# --- Base del TIPO ------------------------------------------------------------------------------------------


def construir_base_tipo(elegidos_tipo: list, tiendas: list[int], agregado: dict, tipo: str = "") -> Workbook:
    """FICHERO BASE de los artículos del TIPO sin la columna B (TIPO): la estructura de siempre de PRUEBAESTANDAR."""
    libro = fichero_base.construir_libro(elegidos_tipo, tiendas, agregado)
    hoja = libro.active
    hoja.delete_cols(2)
    if tipo:
        hoja.title = tipo
    # delete_cols no mueve los anchos: se vuelven a poner todos.
    for letra in list(hoja.column_dimensions):
        del hoja.column_dimensions[letra]
    for letra, ancho in ANCHOS_TIPO.items():
        hoja.column_dimensions[letra].width = ancho
    for c in range(COLUMNAS_ARTICULO_TIPO + 1, COLUMNAS_ARTICULO_TIPO + 1 + 3 * len(tiendas)):
        hoja.column_dimensions[get_column_letter(c)].width = fichero_base.ANCHO_TIENDA
    return libro


def _es_eleccion(col: int, primera_tienda: int) -> bool:
    return col >= primera_tienda and (col - primera_tienda) % 3 == 2


def verificar_base_tipo(libro_tipo: Workbook, libro_base: Workbook, tipo: str) -> int:
    """Compara celda a celda la base del TIPO con las filas de ese TIPO de la hoja TODOS (quitando la columna B).

    No compara las columnas ELECCIÓN. Devuelve el nº de artículos comprobados.
    """
    buscado = normalizar_tipo(tipo)
    base = list(libro_base[fichero_base.HOJA].iter_rows(values_only=True))
    esperadas = base[:2] + [f for f in base[2:] if normalizar_tipo(f[1]) == buscado]
    esperadas = [tuple(f[:1]) + tuple(f[2:]) for f in esperadas]
    escritas = list(libro_tipo.worksheets[0].iter_rows(values_only=True))

    def fallo(detalle: str):
        raise ErrorValidacion(
            f"La comprobación de la base del TIPO {tipo} frente al FICHERO BASE ha fallado: {detalle}. "
            "No se ha guardado ningún fichero."
        )

    if len(escritas) != len(esperadas):
        fallo(f"tiene {len(escritas) - 2} artículos y el FICHERO BASE tiene {len(esperadas) - 2} de ese TIPO")
    primera_tienda = COLUMNAS_ARTICULO_TIPO + 1
    for n_fila, (esperada, escrita) in enumerate(zip(esperadas, escritas), start=1):
        if len(escrita) != len(esperada):
            fallo(f"la fila {n_fila} tiene {len(escrita)} columnas en lugar de {len(esperada)}")
        for col, (a, b) in enumerate(zip(esperada, escrita), start=1):
            if n_fila > 2 and _es_eleccion(col, primera_tienda):
                continue
            if a != b:
                fallo(f"fila {n_fila}, columna {get_column_letter(col)}: '{b}' en lugar de '{a}'")
    return len(esperadas) - 2


# --- Nombres de los ficheros --------------------------------------------------------------------------------


class RutasSalida(NamedTuple):
    salalm: Path
    base: Path
    prueba: Path
    reparto: Path


def rutas_salida(ruta_salalm, tipo, fecha: date) -> RutasSalida:
    """Los 4 ficheros en la carpeta del SALALM, con la fecha de ejecución y, los del palet, con el TIPO abreviado."""
    carpeta = Path(ruta_salalm).parent
    f = fecha.strftime("%Y%m%d")
    ab = ABREVIATURAS[tipo_canonico(tipo)]
    return RutasSalida(
        salalm=carpeta / f"SALALM FILTRADO_{f}.xlsx",
        base=carpeta / f"FICHERO BASE_{f}.xlsx",
        prueba=carpeta / f"PRUEBAESTANDAR_{ab}_{f}.xlsx",
        reparto=carpeta / f"REPARTOESTANDAR_{ab}_{f}.xls",
    )


# --- Parte GENERABASE reutilizable --------------------------------------------------------------------------


def clave_entradas(rutas_entrada, n) -> tuple | None:
    """Identifica los 4 ficheros de GENERABASE (ruta, fecha de modificación y tamaño) y N; None si no se puede."""
    try:
        n = fichero_base.parsear_n(n)
        partes = []
        for ruta in rutas_entrada:
            ruta = Path(ruta).resolve()
            st = os.stat(ruta)
            partes.append((str(ruta), st.st_mtime_ns, st.st_size))
    except (OSError, modelo_gb.ErrorValidacion):
        return None
    return (*partes, n)


@dataclass
class Datos:
    """Resultado de la parte GENERABASE; no se modifica al calcular un TIPO, así que se puede reutilizar."""

    generados: proceso_gb.DatosGenerados
    ruta_salalm: Path
    clave: tuple | None

    @property
    def libro_salalm(self) -> Workbook:
        return self.generados.calculo.libro_salalm

    @property
    def libro_base(self) -> Workbook:
        return self.generados.calculo.libro_base

    @property
    def usados(self):
        return self.generados.usados


def preparar(ruta_salalm, ruta_maestro, ruta_caducidad, ruta_access, n, progreso: Progreso = _sin_progreso) -> Datos:
    rutas = (ruta_salalm, ruta_maestro, ruta_caducidad, ruta_access)
    clave = clave_entradas(rutas, n)
    # Las rutas de salida de GENERABASE no se usan: los nombres con fecha y TIPO los pone rutas_salida().
    destino_salalm, destino_base = proceso_gb.rutas_salida(ruta_salalm)
    generados = proceso_gb.calcular_datos(*rutas, n, destino_salalm, destino_base, progreso)
    return Datos(generados=generados, ruta_salalm=Path(ruta_salalm), clave=clave)


# --- Cálculo de un TIPO -------------------------------------------------------------------------------------


@dataclass
class ResumenIntegrado:
    rutas: RutasSalida
    tipo: str
    fecha: date
    articulos_tipo: int
    articulos_base: int
    reutilizado: bool
    generabase: proceso_gb.Resumen
    movimientos: object
    palet: object  # pruebaestandar.modelo.Resumen
    avisos: list[str]

    @property
    def dias(self) -> int:
        return self.movimientos.dias_pi

    def texto(self) -> str:
        m = self.movimientos
        lineas = ["Ficheros generados:", *(f"  {r}" for r in self.rutas), ""]
        if self.reutilizado:
            lineas += [
                "Se han reutilizado el FICHERO BASE y los días de la ejecución anterior "
                "(no se ha vuelto a leer el Access).",
                "",
            ]
        lineas += self.generabase.lineas_totales()
        lineas += [
            f"  Nº de días de datos (MVFECI distintos con MVTMOV = PI): {_miles(m.dias_pi)}  ·  fechas: "
            + (f"{_fecha(m.fecha_pi_min)} – {_fecha(m.fecha_pi_max)}" if m.fecha_pi_min is not None else "—"),
            "",
            f"PALET ESTÁNDAR — TIPO {self.tipo}",
            f"  {self.tipo}: {_miles(self.articulos_tipo)} artículos de los {_miles(self.articulos_base)} del FICHERO BASE.",
            f"  Tiendas procesadas: {_miles(self.palet.tiendas_procesadas)}",
            f"  Tiendas sin selección: {_miles(self.palet.tiendas_sin_seleccion)}",
            f"  Total de cajas seleccionadas: {_miles(self.palet.total_cajas)}",
            f"  Total de unidades: {_miles(self.palet.total_unidades)}",
            "",
        ]
        if self.avisos:
            lineas.append(f"Avisos ({len(self.avisos)}):")
            lineas.extend(f"  - {a}" for a in self.avisos[:200])
            if len(self.avisos) > 200:
                lineas.append(f"  … y {len(self.avisos) - 200} más.")
        else:
            lineas.append("Sin avisos.")
        return "\n".join(lineas)


@dataclass
class CalculoIntegrado:
    datos: Datos
    palet: proceso.Calculo
    resumen: ResumenIntegrado

    def guardar(self) -> ResumenIntegrado:
        """Guarda los 4 ficheros; si uno falla (abierto en Excel), se puede volver a llamar sin recalcular."""
        rutas = self.resumen.rutas
        guardar_xlsx(self.datos.libro_salalm, rutas.salalm)
        guardar_xlsx(self.datos.libro_base, rutas.base)
        self.palet.guardar()
        return self.resumen


def calcular_tipo(
    datos: Datos,
    tipo,
    ruta_tabla,
    fecha: date,
    progreso: Progreso = _sin_progreso,
    reutilizado: bool = False,
) -> CalculoIntegrado:
    tipo = tipo_canonico(tipo)
    generados = datos.generados
    usados = generados.usados
    if usados.dias_pi < 1:
        raise ErrorValidacion(
            "No se ha podido contar el nº de días de datos: el Access no tiene ninguna fila PI con fecha (MVFECI). "
            "No se ha generado ningún fichero."
        )
    progreso(f"Calculando el palet estándar de {tipo}…")
    elegidos_tipo = filtrar_tipo(generados.elegidos, tipo, generados.n)
    libro_tipo = construir_base_tipo(elegidos_tipo, generados.tiendas, generados.agregado, tipo)
    verificar_base_tipo(libro_tipo, datos.libro_base, tipo)

    rutas = rutas_salida(datos.ruta_salalm, tipo, fecha)
    palet = proceso.calcular_desde_libro(libro_tipo, Path(ruta_tabla), usados.dias_pi, rutas.prueba, rutas.reparto)

    resumen_gb = generados.calculo.resumen
    avisos = list(resumen_gb.avisos)
    if usados.aviso_pi_sin_fecha:
        avisos.append(usados.aviso_pi_sin_fecha)
    avisos += palet.resumen.avisos
    resumen = ResumenIntegrado(
        rutas=rutas,
        tipo=tipo,
        fecha=fecha,
        articulos_tipo=len(elegidos_tipo),
        articulos_base=len(generados.elegidos),
        reutilizado=reutilizado,
        generabase=resumen_gb,
        movimientos=usados,
        palet=palet.resumen,
        avisos=avisos,
    )
    return CalculoIntegrado(datos=datos, palet=palet, resumen=resumen)

