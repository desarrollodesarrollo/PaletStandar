import time

import pytest

tk = pytest.importorskip("tkinter")

from generabase import gui  # noqa: E402


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


def elegir(app, monkeypatch, rutas):
    filtros = []
    pila = iter(str(r) for r in rutas)
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **k: filtros.append(k["filetypes"]) or next(pila))
    for clave, nombre, tipos in gui.ENTRADAS[: len(rutas)]:
        app.elegir(clave, nombre, tipos)
    return filtros


def esperar(app, limite=30):
    fin = time.time() + limite
    while app.ocupado and time.time() < fin:
        app.root.update()
        time.sleep(0.01)
    app.root.update()
    assert not app.ocupado


def test_ventana_principal(app):
    assert app.root.title() == "GENERABASE"
    assert [c for c, _, _ in gui.ENTRADAS] == ["salalm", "maestro", "caducidad", "access"]
    assert all(e.cget("text") == "(sin seleccionar)" for e in app.etiquetas.values())
    assert app.btn_ejecutar.cget("text") == "Ejecutar"


def test_selector_del_access_filtra_accdb_y_mdb(app, monkeypatch, entradas):
    filtros = elegir(app, monkeypatch, entradas)
    assert filtros[0] == gui.TIPOS_EXCEL and filtros[3][0] == ("Bases de datos Access", "*.accdb *.mdb")
    assert app.etiquetas["access"].cget("text") == "movimientos.accdb"


def test_falta_el_access(app, monkeypatch, entradas):
    elegir(app, monkeypatch, entradas[:3])
    app.var_n.set("10")
    app.ejecutar()
    assert app.avisos == [("showwarning", "Selecciona el fichero de MOVIMIENTOS (Access).")] and not app.ocupado


def test_n_no_valido(app, monkeypatch, entradas):
    elegir(app, monkeypatch, entradas)
    app.var_n.set("mil")
    app.ejecutar()
    assert app.avisos[0][0] == "showwarning" and "entero mayor que 0" in app.avisos[0][1]


def test_ejecucion_correcta(app, monkeypatch, entradas):
    elegir(app, monkeypatch, entradas)
    app.var_n.set("2")
    app.ejecutar()
    assert app.ocupado and app.btn_ejecutar.instate(["disabled"])
    esperar(app)
    carpeta = entradas[0].parent
    assert (carpeta / "SALALM FILTRADO.xlsx").exists() and (carpeta / "FICHERO BASE.xlsx").exists()
    tipo, texto = app.avisos[-1]
    assert tipo == "showinfo" and "SALALM FILTRADO.xlsx" in texto and "FICHERO BASE.xlsx" in texto
    resumen = app.txt_resumen.get("1.0", "end")
    assert "Totales de control del Access" in resumen and "Filas leídas / declaradas: 8 / 8" in resumen
    assert app.lbl_estado.cget("text") == "Proceso terminado."


def test_salida_existente_y_usuario_dice_no(app, monkeypatch, entradas):
    existente = entradas[0].parent / "FICHERO BASE.xlsx"
    existente.write_bytes(b"previo")
    preguntas = []
    monkeypatch.setattr(gui.messagebox, "askyesno", lambda t, texto: preguntas.append(texto) or False)
    elegir(app, monkeypatch, entradas)
    app.var_n.set("2")
    app.ejecutar()
    assert len(preguntas) == 1 and "FICHERO BASE.xlsx" in preguntas[0] and "SALALM FILTRADO" not in preguntas[0]
    assert not app.ocupado and existente.read_bytes() == b"previo"
    assert not (entradas[0].parent / "SALALM FILTRADO.xlsx").exists()


def test_error_de_datos_sin_traza_y_ventana_lista(app, monkeypatch, entradas, tmp_path):
    malo = tmp_path / "malo.accdb"
    malo.write_text("no es access")
    elegir(app, monkeypatch, [*entradas[:3], malo])
    app.var_n.set("2")
    app.ejecutar()
    esperar(app)
    tipo, texto = app.avisos[-1]
    assert tipo == "showerror" and "no ser un Access" in texto and "Traceback" not in texto
    assert not app.btn_ejecutar.instate(["disabled"])


def test_fichero_abierto_reintentar(app, monkeypatch, entradas):
    from openpyxl.workbook import Workbook

    original = Workbook.save
    intentos = []

    def save(libro, destino):
        intentos.append(destino)
        if len(intentos) == 1:
            raise PermissionError
        original(libro, destino)

    monkeypatch.setattr(Workbook, "save", save)
    monkeypatch.setattr(gui.messagebox, "askretrycancel", lambda t, texto: True)
    elegir(app, monkeypatch, entradas)
    app.var_n.set("2")
    app.ejecutar()
    esperar(app)
    esperar(app)
    assert app.avisos[-1][0] == "showinfo" and (entradas[0].parent / "FICHERO BASE.xlsx").exists()
