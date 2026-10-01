"""Generadores de ficheros sintéticos y fixtures de las pruebas de GENERABASE."""

from __future__ import annotations

import json
from pathlib import Path

import openpyxl
import pytest

from generabase import access

ENC_SALALM = ["FECHAI", "ALMACEN", "CODIGO", "CAJAS", "DESCRIPC", "DESSEC", "BAJA", "UNIXCAJA", "RADUBICA", "PESO", "VOLUMEN", "OTRA"]


def crear_excel(ruta: Path, encabezados, filas, hoja="Hoja1") -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = hoja
    ws.append(list(encabezados))
    for f in filas:
        ws.append(list(f))
    wb.save(ruta)
    return ruta


def art(codigo, cajas=10, seccion="BEBIDAS", baja="", unixcaja=6, radubica="10012345", peso=8000, volumen=12648):
    """Fila de SALALM con valores por defecto válidos (ubicación 100 → ALIMENTACIÓN)."""
    return dict(CODIGO=codigo, CAJAS=cajas, DESCRIPC=seccion, DESSEC=seccion, BAJA=baja, UNIXCAJA=unixcaja,
                RADUBICA=radubica, PESO=peso, VOLUMEN=volumen)


def crear_salalm(ruta: Path, articulos: list[dict]) -> Path:
    return crear_excel(ruta, ENC_SALALM, [[925, 1] + [a.get(c) for c in ENC_SALALM[2:-1]] + ["x"] for a in articulos])


def crear_maestro(ruta: Path, filas: list[tuple]) -> Path:
    """filas: [(MAARTI, MACADU, MACLCA)]."""
    return crear_excel(ruta, ["MAALMA", "MAARTI", "MADENO", "MACADU", "MACLCA"], [[1, a, "x", b, c] for a, b, c in filas], "MSG001")


def crear_caducidades(ruta: Path, filas: list[tuple]) -> Path:
    """filas: [(C3CADU, C3UTIL, C3COME)]."""
    return crear_excel(ruta, ["C3ALMA", "C3CADU", "C3UTIL", "C3COME"], [[1, *f] for f in filas], "MVG003")


CADUCIDADES = [("K", 92, "ARTICULOS DE 3 MESES"), ("J02", 85, "ARTICULOS DE 80 DIAS"), ("N", 182, "ARTICULOS DE 6 MESES"), ("1", 14, "FRUTA 1")]


def mov(arti, tienda, cantidad, unidades, tipo="PI", fecha=20251015):
    return dict(MVARTI=str(arti), MVTMOV=tipo, MVDESM=f"{tienda:09d}" if isinstance(tienda, int) else tienda,
                MVCANM=float(-cantidad), MVUNCA=None if unidades is None else float(unidades), MVFECI=float(fecha))


def crear_access(ruta: Path, movimientos: list[dict], declaradas=None, tabla="MOVIMIENTOS", con_id=True, quitar=()) -> Path:
    """Fichero que el FalsoAccessParser interpreta como una base de Access con una tabla."""
    columnas = ["Id"] * con_id + ["MVALMA", "MVTMOV", "MVARTI", "MVDESM", "MVCANM", "MVFECI", "MVUNCA"]
    columnas = [c for c in columnas if c not in quitar]
    datos = {c: [] for c in columnas}
    for i, m in enumerate(movimientos, start=1):
        for c in columnas:
            datos[c].append(i if c == "Id" else 1.0 if c == "MVALMA" else m.get(c))
    contenido = {"tablas": {tabla: datos}, "declaradas": len(movimientos) if declaradas is None else declaradas}
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    return ruta


class FalsoAccessParser:
    """Sustituye a access_parser.AccessParser leyendo el JSON de crear_access()."""

    def __init__(self, ruta):
        texto = Path(ruta).read_text(encoding="utf-8")
        if not texto.startswith("{"):
            raise ValueError("Not a valid Access database")
        self._datos = json.loads(texto)
        self.catalog = {**{t: 1 for t in self._datos["tablas"]}, "MSysObjects": 2, "f_ABC_Data": 3}

    def parse_table(self, nombre):
        return {c: list(v) for c, v in self._datos["tablas"][nombre].items()}

    def get_table(self, nombre):
        tabla = type("Tabla", (), {})()
        tabla.table_header = {"number_of_rows": self._datos["declaradas"]}
        return tabla


@pytest.fixture
def falso_access(monkeypatch):
    monkeypatch.setattr(access, "AccessParser", FalsoAccessParser)


@pytest.fixture
def entradas(tmp_path, falso_access):
    """Juego completo y pequeño de los 4 ficheros de entrada."""
    salalm = crear_salalm(tmp_path / "salalm.xlsx", [
        art(101, cajas=50), art(102, cajas=80, radubica="25000101"), art(103, cajas=30, radubica="70000101"),
        art(104, cajas=99, baja="B"), art(105, cajas=70, seccion="SUMINISTROS Y SERVICIOS"),
        art(106, cajas=60, radubica="   00000"), art(107, cajas=40, radubica="30000101"), art(108, cajas=20),
    ])
    maestro = crear_maestro(tmp_path / "maestro.xlsx", [(101, "S", "N"), (102, "N", ""), (103, "S", "K"), (108, "S", "J02")])
    caducidad = crear_caducidades(tmp_path / "caducidad.xlsx", CADUCIDADES)
    movimientos = crear_access(tmp_path / "movimientos.accdb", [
        mov(101, 10081, 12, 6), mov(101, 10081, 6, 6), mov(101, 10400, 9, 6), mov(102, 10349, 6, 6),
        mov(103, 10999, 6, 6), mov(101, 10350, 6, 6), mov(101, 10081, 6, 6, tipo="SI"), mov(999, 10500, 6, 6),
    ])
    return salalm, maestro, caducidad, movimientos
