import pytest

from generabase import access, lectura
from generabase.columnas import codigo_texto, entero, indice, numero
from generabase.modelo import ErrorValidacion

from .apoyo import ENC_SALALM, CADUCIDADES, art, crear_access, crear_caducidades, crear_excel, crear_maestro, crear_salalm, mov


# 2.1
@pytest.mark.parametrize("valor,esperado", [
    ("000010389", 10389), ("8682851", 8682851), (273137.0, 273137), (273137, 273137), (" 42 ", 42),
    ("ABC", None), ("", None), (None, None), (2.5, None), (True, None),
])
def test_entero(valor, esperado):
    assert entero(valor) == esperado


@pytest.mark.parametrize("valor,esperado", [(1, "1"), ("1", "1"), (1.0, "1"), (" K ", "K"), (None, ""), ("B02", "B02")])
def test_codigo_texto(valor, esperado):
    assert codigo_texto(valor) == esperado


def test_numero():
    assert numero("2,5") == 2.5 and numero(3) == 3 and numero("x") is None and numero("") is None


def test_indice_por_nombre_sin_mayusculas_ni_espacios():
    assert indice(["a", " Codigo ", "CAJAS"], ["CODIGO", "cajas"], "SALALM") == {"CODIGO": 1, "cajas": 2}
    with pytest.raises(ErrorValidacion, match="Falta la columna MACLCA en el fichero MAESTRO"):
        indice(["MAARTI", "MACADU"], ["MAARTI", "MACADU", "MACLCA"], "MAESTRO")


# 2.2
def test_leer_salalm_con_columnas_extra_y_en_otro_orden(tmp_path):
    encabezados = ["VOLUMEN", "x", "PESO", "RADUBICA", "UNIXCAJA", "BAJA", "DESSEC", "DESCRIPC", "CAJAS", "CODIGO"]
    ruta = crear_excel(tmp_path / "s.xlsx", encabezados, [[12648, "z", 8000, "24012404", 6, "", "BEBIDAS", "BEBIDAS", 474.5, 273137]])
    articulos, avisos = lectura.leer_salalm(ruta)
    a = articulos[0]
    assert (a.codigo, a.cajas, a.peso, a.volumen, a.unixcaja, a.radubica, a.seccion) == (273137, 474.5, 8000, 12648, 6, "24012404", "BEBIDAS")
    assert avisos == []


def test_salalm_codigo_repetido(tmp_path):
    ruta = crear_salalm(tmp_path / "s.xlsx", [art(273137), art(5), art(273137)])
    with pytest.raises(ErrorValidacion, match="CODIGO 273137 está repetido en las filas 2 y 4"):
        lectura.leer_salalm(ruta)


@pytest.mark.parametrize("columna", ["CAJAS", "PESO", "VOLUMEN", "UNIXCAJA"])
def test_salalm_valor_no_numerico(tmp_path, columna):
    a = art(1)
    a[columna] = "abc"
    with pytest.raises(ErrorValidacion, match=rf"SALALM fila 2, columna [A-Z]+ \({columna}\)"):
        lectura.leer_salalm(crear_salalm(tmp_path / "s.xlsx", [a]))


def test_salalm_codigo_no_numerico_es_aviso(tmp_path):
    articulos, avisos = lectura.leer_salalm(crear_salalm(tmp_path / "s.xlsx", [art("XX"), art(2)]))
    assert [a.codigo for a in articulos] == [2] and "fila 2" in avisos[0]


def test_salalm_columna_ausente(tmp_path):
    ruta = crear_excel(tmp_path / "s.xlsx", [c for c in ENC_SALALM if c != "RADUBICA"], [])
    with pytest.raises(ErrorValidacion, match="Falta la columna RADUBICA en el fichero SALALM"):
        lectura.leer_salalm(ruta)


def test_maestro_y_duplicados(tmp_path):
    ruta = crear_maestro(tmp_path / "m.xlsx", [(1, "S", "K"), (2, "n", None), (1, "N", "")])
    maestro, avisos = lectura.leer_maestro(ruta)
    assert maestro == {1: ("S", "K"), 2: ("N", "")}
    assert len(avisos) == 1 and "MAARTI 1 repetido" in avisos[0]


def test_caducidades(tmp_path):
    cad = lectura.leer_caducidades(crear_caducidades(tmp_path / "c.xlsx", CADUCIDADES + [(10, 600, "FRUTOS SECOS")]))
    assert cad["N"] == (182, "ARTICULOS DE 6 MESES") and cad["10"] == (600, "FRUTOS SECOS")


def test_caducidades_duplicado_y_no_numerico(tmp_path):
    with pytest.raises(ErrorValidacion, match="C3CADU 'K' está repetido"):
        lectura.leer_caducidades(crear_caducidades(tmp_path / "c.xlsx", [("K", 92, "a"), ("K", 93, "b")]))
    with pytest.raises(ErrorValidacion, match=r"fila 2, columna C \(C3UTIL\)"):
        lectura.leer_caducidades(crear_caducidades(tmp_path / "d.xlsx", [("K", "tres meses", "a")]))


def test_excel_inexistente_o_no_valido(tmp_path):
    with pytest.raises(ErrorValidacion, match="No se encuentra el fichero MAESTRO"):
        lectura.leer_maestro(tmp_path / "no.xlsx")
    falso = tmp_path / "falso.xlsx"
    falso.write_text("hola")
    with pytest.raises(ErrorValidacion, match="no es un Excel"):
        lectura.leer_salalm(falso)


# 2.3
def test_leer_movimientos_conserva_solo_las_columnas_necesarias(tmp_path, falso_access):
    m = access.leer_movimientos(crear_access(tmp_path / "a.accdb", [mov(1, 10081, 6, 6)] * 3))
    assert set(m.columnas) == {"MVARTI", "MVTMOV", "MVDESM", "MVCANM", "MVUNCA", "MVFECI"}
    assert (m.filas_leidas, m.filas_declaradas) == (3, 3)


def test_access_sin_columna_id(tmp_path, falso_access):
    m = access.leer_movimientos(crear_access(tmp_path / "a.accdb", [mov(1, 10081, 6, 6)], con_id=False))
    assert m.filas_leidas == 1


def test_access_lectura_incompleta(tmp_path, falso_access):
    ruta = crear_access(tmp_path / "a.accdb", [mov(1, 10081, 6, 6)] * 3, declaradas=52150)
    with pytest.raises(ErrorValidacion, match=r"leídas 3 filas de 52\.150 declaradas"):
        access.leer_movimientos(ruta)


def test_access_columnas_desiguales(tmp_path, falso_access, monkeypatch):
    ruta = crear_access(tmp_path / "a.accdb", [mov(1, 10081, 6, 6)] * 2)
    original = access.AccessParser.parse_table
    monkeypatch.setattr(access.AccessParser, "parse_table", lambda self, n: {**original(self, n), "MVUNCA": [6.0]})
    with pytest.raises(ErrorValidacion, match="distinto nº de valores"):
        access.leer_movimientos(ruta)


def test_access_tabla_ausente(tmp_path, falso_access):
    ruta = crear_access(tmp_path / "a.accdb", [mov(1, 10081, 6, 6)], tabla="MOVS_2025")
    with pytest.raises(ErrorValidacion, match="no contiene la tabla MOVIMIENTOS. Tablas encontradas: MOVS_2025"):
        access.leer_movimientos(ruta)


def test_access_columna_ausente(tmp_path, falso_access):
    ruta = crear_access(tmp_path / "a.accdb", [mov(1, 10081, 6, 6)], quitar=("MVUNCA",))
    with pytest.raises(ErrorValidacion, match="Falta la columna MVUNCA en la tabla MOVIMIENTOS"):
        access.leer_movimientos(ruta)


def test_access_fichero_no_valido_o_inexistente(tmp_path, falso_access):
    malo = tmp_path / "malo.accdb"
    malo.write_text("esto no es un access")
    with pytest.raises(ErrorValidacion, match="dañado, protegido con contraseña o no ser un Access"):
        access.leer_movimientos(malo)
    with pytest.raises(ErrorValidacion, match="No se encuentra el fichero de MOVIMIENTOS"):
        access.leer_movimientos(tmp_path / "no.accdb")


# 2.4
def test_filtro_de_tipo_y_rangos_de_tienda(tmp_path, falso_access):
    tiendas = [10080, 10081, 10349, 10350, 10398, 10399, 10999, 11000]
    movs = [mov(1, t, 6, 6) for t in tiendas] + [mov(1, 10100, 6, 6, tipo="SI")]
    usados = access.filtrar(access.leer_movimientos(crear_access(tmp_path / "a.accdb", movs)))
    assert usados.tiendas == [81, 349, 399, 999]
    assert (usados.filas_pi, usados.filas_en_rango, len(usados.lineas)) == (8, 4, 4)


def test_cajas_valor_absoluto_entre_unidades(tmp_path, falso_access):
    usados = access.filtrar(access.leer_movimientos(crear_access(tmp_path / "a.accdb", [mov(7, 10081, 18, 12)])))
    assert usados.lineas == [(7, 81, 1.5)] and usados.total_cajas == 1.5


def test_movimientos_no_validos_se_cuentan(tmp_path, falso_access):
    movs = [mov("ABC", 10081, 6, 6), mov(1, "TIENDA", 6, 6), mov(2, 10081, 6, 0), mov(3, 10081, 6, None), mov(4, 10081, 6, 6)]
    usados = access.filtrar(access.leer_movimientos(crear_access(tmp_path / "a.accdb", movs)))
    assert (usados.articulo_no_valido, usados.tienda_no_valida, usados.sin_unidades_caja, len(usados.lineas)) == (1, 1, 2, 1)
    assert len(usados.avisos) == 3 and any("1 movimientos PI con código de artículo" in a for a in usados.avisos)


def test_mvcanm_no_numerico_detiene(tmp_path, falso_access):
    m = mov(1, 10081, 6, 6)
    m["MVCANM"] = "x"
    with pytest.raises(ErrorValidacion, match="MVCANM 'x' no es un número"):
        access.filtrar(access.leer_movimientos(crear_access(tmp_path / "a.accdb", [m])))


def test_totales_de_control_y_fechas(tmp_path, falso_access):
    movs = [mov(1, 10081, 6, 6, fecha=20251015), mov(2, 10082, 12, 6, fecha=20251001), mov(1, 10082, 3, 6, fecha=20251020)]
    usados = access.filtrar(access.leer_movimientos(crear_access(tmp_path / "a.accdb", movs)))
    assert (usados.articulos, usados.tiendas, usados.total_cajas) == (2, [81, 82], 3.5)
    assert (usados.fecha_min, usados.fecha_max) == (20251001, 20251020)
