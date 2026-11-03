import time
from datetime import date

import pytest

tk = pytest.importorskip("tkinter")
pytest.importorskip("access_parser")

from generabase import access  # noqa: E402
from pruebaestandar import gui  # noqa: E402
from tests_generabase.apoyo import entradas, falso_access  # noqa: E402,F401

from .conftest import crear_tabla  # noqa: E402

FECHA = date(2026, 11, 3)
TIENDAS = [81, 349, 400, 500, 999]


@pytest.fixture
def app(monkeypatch):
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("sin pantalla disponible")
    avisos = []
    for nombre in ("showwarning", "showerror", "showinfo"):
        monkeypatch.setattr(gui.messagebox, nombre, lambda titulo, texto, n=nombre: avisos.append((n, texto)))
    monkeypatch.setattr(gui, "hoy", lambda: FECHA)
    aplicacion = gui.App(root)
    aplicacion.avisos = avisos
    yield aplicacion
    root.destroy()


@pytest.fixture
def ficheros(entradas, tmp_path):
    """Los 5 ficheros de entrada, en el orden de la ventana."""
    return [*entradas, crear_tabla(tmp_path / "tabla.xlsx", [(t, "PALET", 875, 1300) for t in TIENDAS])]


def elegir(app, monkeypatch, rutas):
    filtros = []
    pila = iter(str(r) for r in rutas)
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: filtros.append(k["filetypes"]) or next(pila))
    for clave, nombre, tipos in gui.ENTRADAS[: len(rutas)]:
        app.elegir(clave, nombre, tipos)
    return filtros


def preparar(app, monkeypatch, ficheros, n="3", tipo="ALIMENTACIÓN"):
    elegir(app, monkeypatch, ficheros)
    app.var_n.set(n)
    app.var_tipo.set(tipo)


def esperar(app, limite=30):
    fin = time.time() + limite
    while app.ocupado and time.time() < fin:
        app.root.update()
        time.sleep(0.01)
    app.root.update()
    assert not app.ocupado


def generados(carpeta):
    return sorted(p.name for p in carpeta.iterdir() if "_" in p.name and not p.name.startswith("."))


# 4.1
def test_ventana_principal(app):
    assert app.root.title() == "PRUEBAESTANDAR"
    assert [c for c, _, _ in gui.ENTRADAS] == ["salalm", "maestro", "caducidad", "access", "tabla"]
    assert all(e.cget("text") == "(sin seleccionar)" for e in app.etiquetas.values())
    assert list(app.cmb_tipo.cget("values")) == ["ALTA ROTACIÓN", "DROGUERÍA", "ALIMENTACIÓN"]
    assert app.var_tipo.get() == "" and str(app.cmb_tipo.cget("state")) == "readonly"
    assert app.var_n.get() == "" and app.btn_ejecutar.cget("text") == "Ejecutar"
    assert not hasattr(app, "var_dias") and not hasattr(app, "ent_dias")


def test_selectores_y_filtros(app, monkeypatch, ficheros):
    filtros = elegir(app, monkeypatch, ficheros)
    assert filtros[0] == filtros[4] == gui.TIPOS_EXCEL and filtros[3][0] == ("Bases de datos Access", "*.accdb *.mdb")
    assert app.etiquetas["access"].cget("text") == "movimientos.accdb" and app.etiquetas["tabla"].cget("text") == "tabla.xlsx"
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: "")
    app.elegir("tabla", "TABLA DE TIENDAS Y MEDIOS", gui.TIPOS_EXCEL)
    assert app.etiquetas["tabla"].cget("text") == "tabla.xlsx"


# 4.2
def test_falta_la_tabla(app, monkeypatch, ficheros):
    preparar(app, monkeypatch, ficheros[:4])
    app.ejecutar()
    assert app.avisos == [("showwarning", "Selecciona el fichero de TABLA DE TIENDAS Y MEDIOS.")] and not app.ocupado


def test_n_no_valido(app, monkeypatch, ficheros):
    preparar(app, monkeypatch, ficheros, n="mil")
    app.ejecutar()
    assert app.avisos[0][0] == "showwarning" and "nº de artículos debe ser un número entero mayor que 0" in app.avisos[0][1]


def test_falta_el_tipo(app, monkeypatch, ficheros):
    preparar(app, monkeypatch, ficheros, tipo="")
    app.ejecutar()
    assert app.avisos == [("showwarning", "Elige el TIPO de palet estándar: ALTA ROTACIÓN, DROGUERÍA o ALIMENTACIÓN.")]
    assert not app.ocupado


def test_solo_existe_el_reparto_y_usuario_dice_no(app, monkeypatch, ficheros):
    carpeta = ficheros[0].parent
    existente = carpeta / "REPARTOESTANDAR_AL_20261103.xls"
    existente.write_bytes(b"previo")
    preguntas = []
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda t, texto: preguntas.append(texto) or False)
    preparar(app, monkeypatch, ficheros)
    app.ejecutar()
    assert len(preguntas) == 1 and "REPARTOESTANDAR_AL_20261103.xls" in preguntas[0]
    assert "PRUEBAESTANDAR" not in preguntas[0] and "FICHERO BASE" not in preguntas[0]
    assert not app.ocupado and existente.read_bytes() == b"previo"
    assert generados(carpeta) == ["REPARTOESTANDAR_AL_20261103.xls"]


def test_ficheros_de_otro_tipo_no_se_preguntan(app, monkeypatch, ficheros):
    carpeta = ficheros[0].parent
    for nombre in ("PRUEBAESTANDAR_DR_20261103.xlsx", "REPARTOESTANDAR_DR_20261103.xls"):
        (carpeta / nombre).write_bytes(b"DR")
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda *a: pytest.fail("no debe preguntar"))
    preparar(app, monkeypatch, ficheros)
    app.ejecutar()
    esperar(app)
    assert app.avisos[-1][0] == "showinfo"
    assert (carpeta / "PRUEBAESTANDAR_DR_20261103.xlsx").read_bytes() == b"DR"


# 4.3
def test_ejecucion_correcta_y_segundo_tipo_sin_releer(app, monkeypatch, ficheros):
    carpeta = ficheros[0].parent
    preparar(app, monkeypatch, ficheros)
    app.ejecutar()
    assert app.ocupado and app.btn_ejecutar.instate(["disabled"]) and app.cmb_tipo.instate(["disabled"])
    esperar(app)
    assert generados(carpeta) == [
        "FICHERO BASE_20261103.xlsx", "PRUEBAESTANDAR_AL_20261103.xlsx",
        "REPARTOESTANDAR_AL_20261103.xls", "SALALM FILTRADO_20261103.xlsx",
    ]
    tipo, texto = app.avisos[-1]
    assert tipo == "showinfo" and "PRUEBAESTANDAR_AL_20261103.xlsx" in texto and "SALALM FILTRADO_20261103.xlsx" in texto
    resumen = app.txt_resumen.get("1.0", "end")
    assert "PALET ESTÁNDAR — TIPO ALIMENTACIÓN" in resumen and "Nº de días de datos (MVFECI distintos con MVTMOV = PI): 1" in resumen
    assert "reutilizado" not in resumen and app.lbl_estado.cget("text") == "Proceso terminado."
    assert app.cmb_tipo.instate(["!disabled", "readonly"])

    monkeypatch.setattr(access, "leer_movimientos", lambda *a: pytest.fail("no debe releer el Access"))
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda *a: True)  # SALALM FILTRADO y FICHERO BASE del día
    app.var_tipo.set("DROGUERÍA")
    app.ejecutar()
    esperar(app)
    assert app.avisos[-1][0] == "showinfo"
    assert "PRUEBAESTANDAR_DR_20261103.xlsx" in generados(carpeta)
    assert "Se han reutilizado el FICHERO BASE y los días" in app.txt_resumen.get("1.0", "end")


def test_cambiar_n_vuelve_a_leer(app, monkeypatch, ficheros):
    preparar(app, monkeypatch, ficheros)
    app.ejecutar()
    esperar(app)
    lecturas = []
    original = access.leer_movimientos
    monkeypatch.setattr(access, "leer_movimientos", lambda r: lecturas.append(r) or original(r))
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda *a: True)
    app.var_n.set("2")
    app.var_tipo.set("ALTA ROTACIÓN")
    app.ejecutar()
    esperar(app)
    assert len(lecturas) == 1 and "reutilizado" not in app.txt_resumen.get("1.0", "end")


def test_error_de_tabla_y_nuevo_intento_sin_releer(app, monkeypatch, ficheros, tmp_path):
    corta = crear_tabla(tmp_path / "corta.xlsx", [(81, "PALET", 875, 1300)])
    preparar(app, monkeypatch, [*ficheros[:4], corta])
    app.ejecutar()
    esperar(app)
    tipo, texto = app.avisos[-1]
    assert tipo == "showerror" and "Faltan 4 tiendas" in texto and "Traceback" not in texto
    assert generados(ficheros[0].parent) == [] and not app.btn_ejecutar.instate(["disabled"])

    monkeypatch.setattr(access, "leer_movimientos", lambda *a: pytest.fail("no debe releer el Access"))
    elegir(app, monkeypatch, ficheros)
    app.ejecutar()
    esperar(app)
    assert app.avisos[-1][0] == "showinfo"


def test_access_no_valido(app, monkeypatch, ficheros, tmp_path):
    malo = tmp_path / "malo.accdb"
    malo.write_text("no es access")
    preparar(app, monkeypatch, [*ficheros[:3], malo, ficheros[4]])
    app.ejecutar()
    esperar(app)
    tipo, texto = app.avisos[-1]
    assert tipo == "showerror" and "no ser un Access" in texto and "Traceback" not in texto
    assert not app.btn_ejecutar.instate(["disabled"]) and app._datos is None


def test_fichero_abierto_reintentar(app, monkeypatch, ficheros):
    from openpyxl.workbook import Workbook

    original = Workbook.save
    intentos = []

    def save(libro, destino):
        if "PRUEBAESTANDAR" in str(destino):
            intentos.append(destino)
            if len(intentos) == 1:
                raise PermissionError
        original(libro, destino)

    monkeypatch.setattr(Workbook, "save", save)
    preguntas = []
    monkeypatch.setattr(gui.messagebox, "askretrycancel", lambda t, texto: preguntas.append(texto) or True)
    preparar(app, monkeypatch, ficheros)
    app.ejecutar()
    esperar(app)
    esperar(app)
    assert "PRUEBAESTANDAR_AL_20261103.xlsx" in preguntas[0] and len(intentos) == 2
    assert app.avisos[-1][0] == "showinfo" and (ficheros[0].parent / "PRUEBAESTANDAR_AL_20261103.xlsx").exists()


def test_error_inesperado_sin_traza(app, monkeypatch, ficheros):
    def explota(*a, **k):
        raise RuntimeError("fallo raro")

    monkeypatch.setattr(gui.integrado, "calcular_tipo", explota)
    preparar(app, monkeypatch, ficheros)
    app.ejecutar()
    esperar(app)
    tipo, texto = app.avisos[-1]
    assert tipo == "showerror" and "fallo raro" in texto and "Traceback" not in texto
