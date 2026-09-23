from __future__ import annotations

import random
from fractions import Fraction
from pathlib import Path

import openpyxl
import pytest

from pruebaestandar.modelo import Articulo, Medio

PALET = ("PALET", 875, 1300)
CARRO = ("CARRO", 475, 600)


def crear_base(ruta: Path, articulos, tiendas) -> Path:
    """articulos: [(codigo, peso, volumen)]; tiendas: [(codigo, {indice_articulo: (bultos, lineas)})]."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hoja1"
    for c, h in enumerate(["CODIGO", "PESO (Kg)", "Volumen (L)", "Densidad (kg/l)"], start=1):
        ws.cell(2, c, h)
    for i, (codigo, peso, volumen) in enumerate(articulos):
        ws.cell(3 + i, 1, codigo)
        ws.cell(3 + i, 2, peso)
        ws.cell(3 + i, 3, volumen)
        if isinstance(peso, (int, float)) and isinstance(volumen, (int, float)) and volumen:
            ws.cell(3 + i, 4, peso / volumen)
    for t, (codigo, salidas) in enumerate(tiendas):
        col = 5 + 3 * t
        for k, h in enumerate(["BULTOS", "LINEAS", "ELECCIÓN"]):
            ws.cell(1, col + k, codigo)
            ws.cell(2, col + k, h)
        for i, (bultos, lineas) in salidas.items():
            ws.cell(3 + i, col, bultos)
            ws.cell(3 + i, col + 1, lineas)
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["G"].width = 11
    wb.save(ruta)
    return ruta


def crear_tabla(ruta: Path, filas) -> Path:
    """filas: [(tienda, tipo, peso_max, volumen_max)]; la densidad se calcula como peso/volumen."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hoja1"
    ws.append(["TIENDA", "TIPO DE MEDIO", "PESO MAX (Kg)", "VOLUMEN MÁX (L)", "DENSIDAD"])
    for tienda, tipo, peso, volumen in filas:
        ws.append([tienda, tipo, peso, volumen, peso / volumen])
    wb.save(ruta)
    return ruta


def datos_aleatorios(n_articulos: int, n_tiendas: int, semilla: int):
    """Datos parecidos a los reales: densidades 0,05–0,97 kg/L, 5–40 L por caja, ~85 % de artículos con salida."""
    rnd = random.Random(semilla)
    articulos = []
    for i in range(n_articulos):
        volumen = round(rnd.uniform(4, 40), 3)
        peso = round(volumen * rnd.uniform(0.05, 0.97), 2)
        articulos.append((2_000_000 + i, peso, volumen))
    tiendas, tabla = [], []
    for t in range(n_tiendas):
        codigo = 10_000 + t
        salidas = {}
        for i in range(n_articulos):
            if rnd.random() < 0.85:
                lineas = rnd.randint(1, 12)
                salidas[i] = (lineas * rnd.randint(1, 4), lineas)
        tiendas.append((codigo, salidas))
        tipo = PALET if rnd.random() < 0.63 else CARRO
        tabla.append((codigo, *tipo))
    return articulos, tiendas, tabla


def articulo(indice: int, peso, volumen, codigo=None) -> Articulo:
    peso, volumen = Fraction(str(peso)), Fraction(str(volumen))
    return Articulo(
        fila=3 + indice,
        codigo=codigo if codigo is not None else 1000 + indice,
        peso=peso,
        volumen=volumen,
        valido=peso > 0 and volumen > 0,
    )


def medio(tipo="PALET", peso=875, volumen=1300, densidad=None) -> Medio:
    densidad = Fraction(peso, volumen) if densidad is None else Fraction(str(densidad))
    return Medio(tipo, Fraction(peso), Fraction(volumen), densidad)


def fr(valores):
    return [Fraction(str(v)) for v in valores]


@pytest.fixture
def ficheros_pequenos(tmp_path):
    """3 artículos × 2 tiendas (una PALET y una CARRO)."""
    articulos = [(111, 5.0, 10.0), (222, 2.5, 8.0), (333, 7.2, 9.0)]
    tiendas = [(10081, {0: (7, 3), 1: (2, 1)}), (10082, {0: (4, 2), 2: (9, 4)})]
    base = crear_base(tmp_path / "FICHERO_BASE.xlsx", articulos, tiendas)
    tabla = crear_tabla(tmp_path / "TABLA.xlsx", [(10081, *PALET), (10082, *CARRO), (99999, *PALET)])
    return base, tabla
