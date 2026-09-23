import time

import pytest

tk = pytest.importorskip("tkinter")

from pruebaestandar import gui  # noqa: E402

from .conftest import PALET, crear_tabla  # noqa: E402


@pytest.fixture
def app(monkeypatch):
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("sin pantalla disponible")
    avisos = []
    for nombre in ("showwarning", "showerror", "showinfo"):
        monkeypatch.setattr(gui.messagebox, nombre, lambda titulo, texto, n=nombre: avisos.append((n, texto)))
    aplicacion = gui.App(root)
    aplicacion.avisos = avisos
    yield aplicacion
    root.destroy()


def elegir(app, monkeypatch, base, tabla):
    rutas = iter([str(base), str(tabla)])
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: next(rutas))
    app.elegir_base()
    app.elegir_tabla()


def esperar(app, limite=30):
    fin = time.time() + limite
    while app.ocupado and time.time() < fin:
        app.root.update()
        time.sleep(0.01)
    app.root.update()
    assert not app.ocupado


# 5.1
def test_ventana_principal(app):
    assert app.root.title() == "PRUEBAESTANDAR"
    assert app.lbl_base.cget("text") == app.lbl_tabla.cget("text") == "(sin seleccionar)"
    assert app.btn_ejecutar.cget("text") == "Ejecutar"
    assert ("Ficheros Excel", "*.xlsx") in gui.TIPOS_EXCEL


def test_selector_muestra_nombre_y_cancelar_no_cambia(app, monkeypatch, ficheros_pequenos):
    base, tabla = ficheros_pequenos
    elegir(app, monkeypatch, base, tabla)
    assert app.lbl_base.cget("text") == "FICHERO_BASE.xlsx" and app.lbl_tabla.cget("text") == "TABLA.xlsx"
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: "")
    app.elegir_base()
    assert app.ruta_base == base


# 5.2
def test_falta_la_tabla(app, monkeypatch, ficheros_pequenos):
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: str(ficheros_pequenos[0]))
    app.elegir_base()
    app.var_dias.set("5")
    app.ejecutar()
    assert app.avisos == [("showwarning", "Selecciona la TABLA DE TIENDAS Y MEDIOS.")]
    assert not app.ocupado


def test_falta_el_fichero_base(app):
    app.ejecutar()
    assert app.avisos == [("showwarning", "Selecciona el FICHERO BASE.")]


def test_dias_no_numericos(app, monkeypatch, ficheros_pequenos):
    elegir(app, monkeypatch, *ficheros_pequenos)
    app.var_dias.set("cinco")
    app.ejecutar()
    assert app.avisos[0][0] == "showwarning" and "entero mayor que 0" in app.avisos[0][1]
    assert not app.ocupado


# 5.3 y 5.4
def test_ejecucion_correcta_con_boton_desactivado(app, monkeypatch, ficheros_pequenos):
    base, tabla = ficheros_pequenos
    elegir(app, monkeypatch, base, tabla)
    app.var_dias.set("2")
    app.ejecutar()
    assert app.ocupado and app.btn_ejecutar.instate(["disabled"])
    esperar(app)
    assert not app.btn_ejecutar.instate(["disabled"])
    assert (base.parent / "PRUEBAESTANDAR.xlsx").exists()
    assert app.avisos[-1][0] == "showinfo" and "PRUEBAESTANDAR.xlsx" in app.avisos[-1][1]
    texto = app.txt_resumen.get("1.0", "end")
    assert "Tiendas procesadas: 2" in texto and "Total de cajas seleccionadas" in texto


def test_salida_existente_y_usuario_dice_no(app, monkeypatch, ficheros_pequenos):
    base, tabla = ficheros_pequenos
    existente = base.parent / "PRUEBAESTANDAR.xlsx"
    existente.write_bytes(b"previo")
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda *a: False)
    elegir(app, monkeypatch, base, tabla)
    app.var_dias.set("2")
    app.ejecutar()
    assert not app.ocupado and existente.read_bytes() == b"previo"


def test_salida_existente_y_usuario_dice_si(app, monkeypatch, ficheros_pequenos):
    base, tabla = ficheros_pequenos
    existente = base.parent / "PRUEBAESTANDAR.xlsx"
    existente.write_bytes(b"previo")
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda *a: True)
    elegir(app, monkeypatch, base, tabla)
    app.var_dias.set("2")
    app.ejecutar()
    esperar(app)
    assert existente.read_bytes().startswith(b"PK")


def test_error_de_validacion_y_nuevo_intento(app, monkeypatch, ficheros_pequenos, tmp_path):
    base, tabla_buena = ficheros_pequenos
    tabla_mala = crear_tabla(tmp_path / "MALA.xlsx", [(10081, *PALET)])
    elegir(app, monkeypatch, base, tabla_mala)
    app.var_dias.set("2")
    app.ejecutar()
    esperar(app)
    tipo, texto = app.avisos[-1]
    assert tipo == "showerror" and "10082" in texto and "Traceback" not in texto
    assert not (base.parent / "PRUEBAESTANDAR.xlsx").exists()

    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: str(tabla_buena))
    app.elegir_tabla()
    app.ejecutar()
    esperar(app)
    assert app.avisos[-1][0] == "showinfo"


def test_fichero_abierto_reintentar(app, monkeypatch, ficheros_pequenos):
    base, tabla = ficheros_pequenos
    from openpyxl.workbook import Workbook

    guardar_original = Workbook.save
    intentos = []

    def save(libro, destino):
        intentos.append(destino)
        if len(intentos) == 1:
            raise PermissionError
        guardar_original(libro, destino)

    monkeypatch.setattr(Workbook, "save", save)
    respuestas = []
    monkeypatch.setattr(gui.messagebox, "askretrycancel", lambda t, texto: respuestas.append(texto) or True)
    elegir(app, monkeypatch, base, tabla)
    app.var_dias.set("2")
    app.ejecutar()
    esperar(app)
    esperar(app)
    assert len(intentos) == 2 and "Reintentar" in respuestas[0]
    assert app.avisos[-1][0] == "showinfo"
    assert (base.parent / "PRUEBAESTANDAR.xlsx").exists()


def test_error_inesperado_sin_traza(app, monkeypatch, ficheros_pequenos):
    monkeypatch.setattr(gui.proceso, "calcular", lambda *a: 1 / 0)
    elegir(app, monkeypatch, *ficheros_pequenos)
    app.var_dias.set("2")
    app.ejecutar()
    esperar(app)
    tipo, texto = app.avisos[-1]
    assert tipo == "showerror" and "error inesperado" in texto and "Traceback" not in texto
    assert not app.btn_ejecutar.instate(["disabled"])
