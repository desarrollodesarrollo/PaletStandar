"""Flujo unificado: GENERABASE + palet estándar de un TIPO (pruebaestandar.integrado)."""

from __future__ import annotations

import os
from datetime import date
from types import SimpleNamespace

import openpyxl
import pytest

pytest.importorskip("access_parser")
xlrd = pytest.importorskip("xlrd")

from generabase import access  # noqa: E402
from generabase import proceso as proceso_gb  # noqa: E402
from pruebaestandar import integrado, proceso  # noqa: E402
from pruebaestandar.lectura import extraer_datos_base  # noqa: E402
from pruebaestandar.modelo import ErrorValidacion  # noqa: E402
from tests_generabase.apoyo import crear_access, entradas, falso_access, mov  # noqa: E402,F401

from .conftest import crear_tabla  # noqa: E402

FECHA = date(2026, 11, 3)
TIENDAS = [81, 349, 400, 500, 999]


def fila(codigo, tipo, peso=6.8, volumen=8.232, unixcaja=6):
    return SimpleNamespace(codigo=codigo, tipo_ubicacion=tipo, peso=peso, volumen=volumen, unixcaja=unixcaja)


@pytest.fixture
def tabla(tmp_path):
    return crear_tabla(tmp_path / "tabla.xlsx", [(t, "PALET", 875, 1300) for t in TIENDAS])


def contenido(ruta):
    return [list(f) for f in openpyxl.load_workbook(ruta).worksheets[0].iter_rows(values_only=True)]


# 3.1
def test_filtrar_tipo_mantiene_el_orden_y_no_distingue_tildes():
    elegidos = [fila(1, "DROGUERÍA"), fila(2, "ALTA ROTACIÓN"), fila(3, "ALIMENTACIÓN"), fila(4, "ALTA ROTACIÓN")]
    assert [a.codigo for a in integrado.filtrar_tipo(elegidos, "ALTA ROTACIÓN")] == [2, 4]
    assert [a.codigo for a in integrado.filtrar_tipo(elegidos, "  Alta  rotacion ")] == [2, 4]
    assert [a.codigo for a in integrado.filtrar_tipo(elegidos, "drogueria")] == [1]


def test_filtrar_tipo_sin_articulos_y_tipo_no_valido():
    with pytest.raises(ErrorValidacion, match=r"No hay artículos de DROGUERÍA entre los 2 artículos .*pedido: 1\.000"):
        integrado.filtrar_tipo([fila(1, "ALIMENTACIÓN"), fila(2, "ALTA ROTACIÓN")], "DROGUERÍA", 1000)
    for malo in ("", None, "BAZAR ABAJO"):
        with pytest.raises(ErrorValidacion, match="Elige el TIPO de palet estándar"):
            integrado.tipo_canonico(malo)


# 3.2
def test_base_tipo_tiene_la_estructura_antigua():
    elegidos = [fila(2465665, "ALTA ROTACIÓN"), fila(7, "ALTA ROTACIÓN", unixcaja=12)]
    agregado = {(2465665, 81): (1.5, 2), (2465665, 400): (3.0, 1), (7, 82): (2.0, 1)}
    libro = integrado.construir_base_tipo(elegidos, [81, 82, 400], agregado, "ALTA ROTACIÓN")
    ws = libro.active
    filas = [list(f) for f in ws.iter_rows(values_only=True)]
    assert ws.title == "ALTA ROTACIÓN"
    assert filas[0] == [None] * 4 + [81] * 3 + [82] * 3 + [400] * 3
    assert filas[1] == ["CODIGO", "PESO (Kg)", "Volumen (L)", "UNIxCAJA"] + ["BULTOS", "LINEAS", "ELECCIÓN"] * 3
    assert filas[2] == [2465665, 6.8, 8.232, 6, 1.5, 2, None, None, None, None, 3, 1, None]
    assert filas[3][3:10] == [12, None, None, None, 2, 1, None]
    anchos = {k: v.width for k, v in ws.column_dimensions.items()}
    assert anchos["A"] == 22.42578125 and anchos["B"] == anchos["C"] == 13 and anchos["D"] == 15.140625
    assert all(anchos[c] == 13 for c in ("E", "M")) and "N" not in anchos

    datos = extraer_datos_base(ws)
    assert [a.codigo for a in datos.articulos] == [2465665, 7] and [a.unidades_caja for a in datos.articulos] == [6, 12]
    assert [d.tienda for d in datos.tiendas] == [81, 82, 400]
    assert datos.tiendas[0].bultos[0] == 1.5 and datos.tiendas[0].col_eleccion == 7


# 3.3
def test_verificar_base_tipo():
    elegidos = [fila(1, "ALTA ROTACIÓN"), fila(2, "DROGUERÍA"), fila(3, "ALTA ROTACIÓN")]
    agregado = {(1, 81): (1.5, 1), (2, 81): (4.0, 2), (3, 82): (2.0, 1)}
    base = integrado.fichero_base.construir_libro(elegidos, [81, 82], agregado)
    del_tipo = integrado.filtrar_tipo(elegidos, "ALTA ROTACIÓN")
    libro = integrado.construir_base_tipo(del_tipo, [81, 82], agregado)
    assert integrado.verificar_base_tipo(libro, base, "ALTA ROTACIÓN") == 2

    libro.active["E3"] = 1.4  # BULTOS alterado
    with pytest.raises(ErrorValidacion, match=r"fila 3, columna E: '1.4' en lugar de '1.5'"):
        integrado.verificar_base_tipo(libro, base, "ALTA ROTACIÓN")

    desplazado = integrado.construir_base_tipo(del_tipo, [81, 82], agregado)
    desplazado.active.insert_cols(5)
    with pytest.raises(ErrorValidacion, match="columnas en lugar de"):
        integrado.verificar_base_tipo(desplazado, base, "ALTA ROTACIÓN")

    otro = integrado.construir_base_tipo(integrado.filtrar_tipo(elegidos, "DROGUERÍA"), [81, 82], agregado)
    with pytest.raises(ErrorValidacion, match="tiene 1 artículos y el FICHERO BASE tiene 2"):
        integrado.verificar_base_tipo(otro, base, "ALTA ROTACIÓN")


# 3.4
def test_nombres_con_tipo_y_fecha(tmp_path):
    rutas = integrado.rutas_salida(tmp_path / "salalm.xlsx", "ALTA ROTACIÓN", FECHA)
    assert [r.name for r in rutas] == [
        "SALALM FILTRADO_20261103.xlsx", "FICHERO BASE_20261103.xlsx",
        "PRUEBAESTANDAR_AR_20261103.xlsx", "REPARTOESTANDAR_AR_20261103.xls",
    ]
    assert all(r.parent == tmp_path for r in rutas)
    assert integrado.rutas_salida(tmp_path / "s.xlsx", "DROGUERÍA", FECHA).prueba.name == "PRUEBAESTANDAR_DR_20261103.xlsx"
    assert integrado.rutas_salida(tmp_path / "s.xlsx", "alimentacion", FECHA).reparto.name == "REPARTOESTANDAR_AL_20261103.xls"


def test_los_programas_sueltos_conservan_sus_nombres(tmp_path):
    assert [r.name for r in proceso_gb.rutas_salida(tmp_path / "s.xlsx")] == ["SALALM FILTRADO.xlsx", "FICHERO BASE.xlsx"]
    assert [r.name for r in proceso.rutas_salida(tmp_path / "b.xlsx")] == ["PRUEBAESTANDAR.xlsx", "REPARTOESTANDAR.xls"]


# 3.5
def test_clave_de_las_entradas(entradas):
    clave = integrado.clave_entradas(entradas, "3")
    assert clave == integrado.clave_entradas(entradas, " 3 ")
    assert clave != integrado.clave_entradas(entradas, "4")
    st = os.stat(entradas[3])
    os.utime(entradas[3], ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    assert clave != integrado.clave_entradas(entradas, "3")
    assert integrado.clave_entradas(entradas, "mil") is None
    assert integrado.clave_entradas([*entradas[:3], entradas[0].parent / "no.accdb"], "3") is None


# 3.6
def test_extremo_a_extremo(entradas, tabla):
    fases = []
    datos = integrado.preparar(*entradas, "3", progreso=fases.append)
    calculo = integrado.calcular_tipo(datos, "ALIMENTACIÓN", tabla, FECHA, progreso=fases.append)
    resumen = calculo.guardar()
    carpeta = entradas[0].parent
    assert fases[0] == "Leyendo SALALM…" and fases[-1] == "Calculando el palet estándar de ALIMENTACIÓN…"
    assert sorted(p.name for p in carpeta.iterdir() if p.suffix in (".xlsx", ".xls") and "_" in p.name) == [
        "FICHERO BASE_20261103.xlsx", "PRUEBAESTANDAR_AL_20261103.xlsx",
        "REPARTOESTANDAR_AL_20261103.xls", "SALALM FILTRADO_20261103.xlsx",
    ]
    assert not list(carpeta.glob(".~*"))

    # SALALM FILTRADO y FICHERO BASE iguales que los de GENERABASE
    proceso_gb.ejecutar(*entradas, "3")
    assert contenido(resumen.rutas.base) == contenido(carpeta / "FICHERO BASE.xlsx")
    assert contenido(resumen.rutas.salalm) == contenido(carpeta / "SALALM FILTRADO.xlsx")

    # PRUEBAESTANDAR: estructura antigua, sólo el 101 (ALIMENTACIÓN), 1 día de datos
    prueba = contenido(resumen.rutas.prueba)
    assert prueba[1][:4] == ["CODIGO", "PESO (Kg)", "Volumen (L)", "UNIxCAJA"]
    assert prueba[0][4::3] == TIENDAS and len(prueba) == 3
    assert prueba[2][:4] == [101, 8, 12.648, 6]
    assert prueba[2][4:7] == [3, 1, 3]  # tienda 81: 3 bultos en 1 día → hasta 3 cajas
    assert prueba[2][10:13] == [1.5, 1, 2]  # tienda 400: 1,5 bultos → hasta 2 cajas
    assert [prueba[2][c] for c in (9, 15, 18)] == [None, None, None]

    hoja = xlrd.open_workbook(str(resumen.rutas.reparto)).sheet_by_name("Hoja1")
    assert hoja.row_values(0) == ["Código", *map(float, TIENDAS)]
    assert hoja.row_values(1) == [101.0, 18.0, "", 12.0, "", ""]
    assert resumen.dias == 1 and resumen.articulos_tipo == 1 and resumen.articulos_base == 3


def test_dias_contados_limitan_las_cajas(tmp_path, falso_access, entradas, tabla):
    # Mismos datos, pero con PI en 3 fechas distintas (una de una tienda fuera de rango) → 3 días.
    movs = [mov(101, 10081, 12, 6), mov(101, 10081, 6, 6), mov(101, 10400, 9, 6), mov(102, 10349, 6, 6),
            mov(103, 10999, 6, 6), mov(101, 10350, 6, 6, fecha=20251016), mov(5, 10081, 6, 6, tipo="SI", fecha=20251018),
            mov(999, 10500, 6, 6, fecha=20251017)]
    crear_access(entradas[3], movs)
    calculo = integrado.calcular_tipo(integrado.preparar(*entradas, "3"), "ALIMENTACIÓN", tabla, FECHA)
    assert calculo.resumen.dias == 3
    prueba = contenido(calculo.guardar().rutas.prueba)
    assert prueba[2][4:7] == [3, 1, 1] and prueba[2][10:13] == [1.5, 1, 1]  # ⌈3/3⌉ = 1, ⌈1,5/3⌉ = 1


# 3.7
def test_sin_dias_no_genera_nada(entradas, tabla):
    crear_access(entradas[3], [mov(101, 10081, 6, 6, tipo="SI")])
    datos = integrado.preparar(*entradas, "3")
    with pytest.raises(ErrorValidacion, match="No se ha podido contar el nº de días de datos"):
        integrado.calcular_tipo(datos, "ALIMENTACIÓN", tabla, FECHA)
    assert not [p for p in entradas[0].parent.iterdir() if "_" in p.name]


def test_tienda_que_falta_en_la_tabla_no_genera_nada(entradas, tmp_path):
    corta = crear_tabla(tmp_path / "corta.xlsx", [(t, "PALET", 875, 1300) for t in TIENDAS[:-1]])
    datos = integrado.preparar(*entradas, "3")
    with pytest.raises(ErrorValidacion, match="Faltan 1 tiendas .*: 999"):
        integrado.calcular_tipo(datos, "ALIMENTACIÓN", corta, FECHA)
    assert not [p for p in entradas[0].parent.iterdir() if "_" in p.name]


def test_reintento_sin_releer_y_con_los_mismos_nombres(entradas, tabla, monkeypatch):
    calculo = integrado.calcular_tipo(integrado.preparar(*entradas, "3"), "ALTA ROTACIÓN", tabla, FECHA)
    original = calculo.palet.libro.save
    intentos = []

    def falla_una_vez(destino):
        intentos.append(destino)
        if len(intentos) == 1:
            raise PermissionError("abierto en Excel")
        original(destino)

    monkeypatch.setattr(calculo.palet.libro, "save", falla_una_vez)
    monkeypatch.setattr(access, "leer_movimientos", lambda *a: pytest.fail("no debe releer el Access"))
    with pytest.raises(integrado.ERRORES_ESCRITURA, match="PRUEBAESTANDAR_AR_20261103.xlsx.*Reintentar"):
        calculo.guardar()
    resumen = calculo.guardar()
    assert intentos == [str(resumen.rutas.prueba)] * 2 and all(r.exists() for r in resumen.rutas)


def test_otro_tipo_con_los_mismos_datos(entradas, tabla, monkeypatch):
    datos = integrado.preparar(*entradas, "3")
    primero = integrado.calcular_tipo(datos, "ALTA ROTACIÓN", tabla, FECHA).guardar()
    base_ar, prueba_ar = contenido(primero.rutas.base), primero.rutas.prueba.read_bytes()
    reparto_ar = primero.rutas.reparto.read_bytes()

    monkeypatch.setattr(access, "leer_movimientos", lambda *a: pytest.fail("no debe releer el Access"))
    segundo = integrado.calcular_tipo(datos, "DROGUERÍA", tabla, FECHA, reutilizado=True).guardar()
    assert segundo.rutas.base == primero.rutas.base and contenido(segundo.rutas.base) == base_ar
    assert segundo.rutas.prueba.name == "PRUEBAESTANDAR_DR_20261103.xlsx"
    assert [f[0] for f in contenido(segundo.rutas.prueba)[2:]] == [103]
    assert primero.rutas.prueba.read_bytes() == prueba_ar and primero.rutas.reparto.read_bytes() == reparto_ar


# 3.8
def test_texto_del_resumen(entradas, tabla):
    crear_access(entradas[3], [mov(101, 10081, 12, 6), mov(102, 10349, 6, 6, fecha=20251020), mov(1, 10350, 6, 6, fecha=None)])
    calculo = integrado.calcular_tipo(integrado.preparar(*entradas, "50"), "ALTA ROTACIÓN", tabla, FECHA, reutilizado=True)
    texto = calculo.resumen.texto()
    for esperado in (
        "PRUEBAESTANDAR_AR_20261103.xlsx", "REPARTOESTANDAR_AR_20261103.xls",
        "SALALM FILTRADO_20261103.xlsx", "FICHERO BASE_20261103.xlsx",
        "Se han reutilizado el FICHERO BASE y los días",
        "FICHERO BASE: 3 artículos × 2 tiendas", "Filas leídas / declaradas: 3 / 3",
        "Nº de días de datos (MVFECI distintos con MVTMOV = PI): 2  ·  fechas: 15/10/2025 – 20/10/2025",
        "PALET ESTÁNDAR — TIPO ALTA ROTACIÓN", "ALTA ROTACIÓN: 1 artículos de los 3 del FICHERO BASE.",
        "Tiendas procesadas: 2", "Tiendas sin selección: 1", "Total de cajas seleccionadas: 1", "Total de unidades: 6",
        "Se pidieron 50 artículos", "1 filas PI sin fecha",
    ):
        assert esperado in texto, esperado
    sin = integrado.calcular_tipo(integrado.preparar(*entradas, "3"), "ALTA ROTACIÓN", tabla, FECHA).resumen.texto()
    assert "reutilizado" not in sin



# 6.1 TIPO TODOS
def test_filtrar_todos_devuelve_todos_en_orden():
    elegidos = [fila(1, "DROGUERÍA"), fila(2, "ALTA ROTACIÓN"), fila(3, "ALIMENTACIÓN")]
    assert integrado.tipo_canonico(" todos ") == "TODOS" and integrado.TIPOS[-1] == "TODOS"
    assert [a.codigo for a in integrado.filtrar_tipo(elegidos, "todos")] == [1, 2, 3]
    with pytest.raises(ErrorValidacion, match=r"El FICHERO BASE no tiene artículos .*pedido: 5"):
        integrado.filtrar_tipo([], "TODOS", 5)
    with pytest.raises(ErrorValidacion, match="ALTA ROTACIÓN, DROGUERÍA, ALIMENTACIÓN o TODOS"):
        integrado.tipo_canonico("")


def test_verificar_base_con_todos():
    elegidos = [fila(1, "ALTA ROTACIÓN"), fila(2, "DROGUERÍA"), fila(3, "ALIMENTACIÓN")]
    agregado = {(1, 81): (1.5, 1), (2, 81): (4.0, 2), (3, 82): (2.0, 1)}
    base = integrado.fichero_base.construir_libro(elegidos, [81, 82], agregado)
    libro = integrado.construir_base_tipo(integrado.filtrar_tipo(elegidos, "TODOS"), [81, 82], agregado, "TODOS")
    assert libro.active.title == "TODOS" and integrado.verificar_base_tipo(libro, base, "TODOS") == 3
    libro.active["H5"] = 9  # BULTOS de la tienda 82 del artículo 3
    with pytest.raises(ErrorValidacion, match=r"TIPO TODOS .*fila 5, columna H: '9' en lugar de '2'"):
        integrado.verificar_base_tipo(libro, base, "TODOS")


def test_nombres_con_todos(tmp_path):
    rutas = integrado.rutas_salida(tmp_path / "salalm.xlsx", "TODOS", FECHA)
    assert (rutas.prueba.name, rutas.reparto.name) == ("PRUEBAESTANDAR_TD_20261103.xlsx", "REPARTOESTANDAR_TD_20261103.xls")
    assert rutas.base.name == "FICHERO BASE_20261103.xlsx"


def test_extremo_a_extremo_con_todos(entradas, tabla):
    calculo = integrado.calcular_tipo(integrado.preparar(*entradas, "3"), "TODOS", tabla, FECHA)
    resumen = calculo.guardar()
    base = contenido(resumen.rutas.base)
    prueba = contenido(resumen.rutas.prueba)
    assert [f[0] for f in base[2:]] == [f[0] for f in prueba[2:]] == [102, 101, 103]
    assert [f[:1] + f[2:] for f in base[2:]] == [[c if (i < 4 or (i - 4) % 3 != 2) else None for i, c in enumerate(f)] for f in prueba[2:]]
    hoja = xlrd.open_workbook(str(resumen.rutas.reparto)).sheet_by_name("Hoja1")
    assert hoja.col_values(0)[1:] == [102.0, 101.0, 103.0]
    assert "TODOS: 3 artículos de los 3 del FICHERO BASE." in resumen.texto()
    assert "PALET ESTÁNDAR — TIPO TODOS" in resumen.texto()


@pytest.mark.lento
def test_rendimiento_1000x180_sin_contar_el_access(tmp_path):
    import time

    from generabase.access import MovimientosUsados

    from .conftest import datos_aleatorios

    articulos, tiendas, tabla = datos_aleatorios(1000, 180, semilla=7)
    elegidos = [fila(c, "ALTA ROTACIÓN", peso=p, volumen=v, unixcaja=u) for c, p, v, u in articulos]
    codigos_tienda = [t for t, _ in tiendas]
    agregado = {(articulos[i][0], t): (float(b), lin) for t, salidas in tiendas for i, (b, lin) in salidas.items()}
    usados = MovimientosUsados(lineas=[], filas_leidas=0, filas_declaradas=0, fechas_pi={20251001 + d for d in range(5)})
    libro_base = integrado.fichero_base.construir_libro(elegidos, codigos_tienda, agregado)
    resumen_gb = proceso_gb.Resumen(tmp_path / "s", tmp_path / "b", 1000, 1000, {}, 0, 1000, 180, 0.0, 0, usados)
    generados = proceso_gb.DatosGenerados(
        calculo=proceso_gb.Calculo(openpyxl.Workbook(), libro_base, resumen_gb), n=1000,
        elegidos=elegidos, tiendas=codigos_tienda, agregado=agregado, usados=usados,
    )
    datos = integrado.Datos(generados=generados, ruta_salalm=tmp_path / "salalm.xlsx", clave=None)
    ruta_tabla = crear_tabla(tmp_path / "tabla.xlsx", tabla)

    inicio = time.perf_counter()
    resumen = integrado.calcular_tipo(datos, "ALTA ROTACIÓN", ruta_tabla, FECHA, reutilizado=True).guardar()
    duracion = time.perf_counter() - inicio
    print(f"1000x180 (sin Access): {duracion:.1f} s, {resumen.palet.total_cajas} cajas")
    assert resumen.palet.tiendas_procesadas == 180 and all(r.exists() for r in resumen.rutas)
    assert duracion < 60
