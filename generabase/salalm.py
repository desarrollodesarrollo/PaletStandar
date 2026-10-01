"""SALALM FILTRADO: SALALM + caducidades, ubicación, filtros y orden por cajas."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, fields
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from .columnas import entero, normalizar
from .lectura import ArticuloSalalm
from .modelo import NOMBRE_SALALM_FILTRADO

SECCIONES_EXCLUIDAS = {"SUMINISTROS Y SERVICIOS", "CAMPAÑA FIDELIDAD"}
TIPOS_EXCLUIDOS = {"PASILLO ESTRECHO", "BAZAR ABAJO"}
CADUCIDAD_MINIMA = 92
MOTIVOS = ("sección", "baja", "ubicación", "tipo de ubicación", "caducidad")


@dataclass(frozen=True)
class FilaSalalm:
    codigo: int
    descripcion: str
    cajas: float
    unixcaja: float
    peso: float
    volumen: float
    seccion: str
    caduca: str
    caducidad_codigo: str
    caducidad: float | None
    descripcion_caducidad: str
    bajas: str
    ubicacion: int | None
    tipo_ubicacion: str
    en_maestro: bool


ENCABEZADOS = (
    "CODIGO", "DESCRIPCIÓN", "CAJAS", "UNIXCAJA", "PESO", "VOLUMEN", "SECCIÓN", "CADUCA",
    "CADUCIDAD CODIGO", "CADUCIDAD", "DESCRIPCIÓN CADUCIDAD", "BAJAS", "UBICACIÓN", "TIPO DE UBICACIÓN",
)
ANCHOS = (12, 28, 10, 10, 9, 10, 28, 9, 11, 11, 32, 8, 11, 20)


def tipo_ubicacion(ubicacion: int | None) -> str:
    if ubicacion is None:
        return ""
    if ubicacion < 220:
        return "ALIMENTACIÓN"
    if ubicacion <= 290:
        return "ALTA ROTACIÓN"
    if ubicacion <= 399:
        return "PASILLO ESTRECHO"
    if ubicacion <= 599:
        return "BAZAR ABAJO"
    return "DROGUERÍA"


def ubicacion(radubica) -> int | None:
    """Las 3 primeras posiciones de RADUBICA como número ('24012404' → 240, '   00000' → None)."""
    if radubica is None:
        return None
    if isinstance(radubica, (int, float)) and not isinstance(radubica, bool):
        radubica = str(int(radubica)).zfill(8)
    return entero(str(radubica)[:3])


def construir(salalm: list[ArticuloSalalm], maestro: dict, caducidades: dict) -> tuple[list[FilaSalalm], list[str]]:
    filas, avisos = [], []
    for a in salalm:
        datos_maestro = maestro.get(a.codigo)
        caduca, codigo_cad = datos_maestro if datos_maestro else ("", "")
        dias, desc = None, ""
        if codigo_cad:
            if codigo_cad in caducidades:
                dias, desc = caducidades[codigo_cad]
            else:
                avisos.append(f"Artículo {a.codigo}: el código de caducidad '{codigo_cad}' no está en el MAESTRO DE CADUCIDAD.")
        elif caduca == "S":
            avisos.append(f"Artículo {a.codigo}: MACADU = S pero no tiene código de caducidad (MACLCA).")
        ubic = ubicacion(a.radubica)
        filas.append(
            FilaSalalm(
                codigo=a.codigo,
                descripcion=a.descripcion,
                cajas=a.cajas,
                unixcaja=a.unixcaja,
                peso=a.peso / 1000,
                volumen=a.volumen / 1000,
                seccion=a.seccion,
                caduca=caduca,
                caducidad_codigo=codigo_cad,
                caducidad=dias,
                descripcion_caducidad=desc,
                bajas=a.baja,
                ubicacion=ubic,
                tipo_ubicacion=tipo_ubicacion(ubic),
                en_maestro=datos_maestro is not None,
            )
        )
    return filas, avisos


def motivo_exclusion(f: FilaSalalm) -> str | None:
    """Primera regla que excluye la fila, en el orden de MOTIVOS; None si se mantiene."""
    if normalizar(f.seccion) in SECCIONES_EXCLUIDAS:
        return "sección"
    if normalizar(f.bajas) == "B":
        return "baja"
    if not f.ubicacion:
        return "ubicación"
    if f.tipo_ubicacion in TIPOS_EXCLUIDOS:
        return "tipo de ubicación"
    if f.caducidad is not None and f.caducidad < CADUCIDAD_MINIMA:
        return "caducidad"
    return None


def filtrar(filas: list[FilaSalalm]) -> tuple[list[FilaSalalm], Counter]:
    excluidas = Counter({m: 0 for m in MOTIVOS})
    quedan = []
    for f in filas:
        motivo = motivo_exclusion(f)
        if motivo:
            excluidas[motivo] += 1
        else:
            quedan.append(f)
    quedan.sort(key=lambda f: (-f.cajas, f.codigo))
    return quedan, excluidas


def _valor(v):
    if v == "" or v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def construir_libro(filas: list[FilaSalalm]) -> Workbook:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "SALALM FILTRADO"
    hoja.append(ENCABEZADOS)
    for celda in hoja[1]:
        celda.font = Font(bold=True)
    campos = [f.name for f in fields(FilaSalalm) if f.name != "en_maestro"]
    for f in filas:
        hoja.append([_valor(getattr(f, c)) for c in campos])
    for i, ancho in enumerate(ANCHOS, start=1):
        hoja.column_dimensions[hoja.cell(1, i).column_letter].width = ancho
    hoja.freeze_panes = "A2"
    return libro


def ruta_salalm_filtrado(ruta_salalm: Path) -> Path:
    return Path(ruta_salalm).parent / NOMBRE_SALALM_FILTRADO
