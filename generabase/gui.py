from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import proceso
from .fichero_base import parsear_n
from .modelo import ErrorEscritura, ErrorValidacion

TIPOS_EXCEL = [("Ficheros Excel", "*.xlsx"), ("Todos los ficheros", "*.*")]
TIPOS_ACCESS = [("Bases de datos Access", "*.accdb *.mdb"), ("Todos los ficheros", "*.*")]
SIN_SELECCION = "(sin seleccionar)"
ENTRADAS = (
    ("salalm", "SALALM", TIPOS_EXCEL),
    ("maestro", "MAESTRO", TIPOS_EXCEL),
    ("caducidad", "MAESTRO DE CADUCIDAD", TIPOS_EXCEL),
    ("access", "MOVIMIENTOS (Access)", TIPOS_ACCESS),
)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("GENERABASE")
        self.rutas: dict[str, Path | None] = {clave: None for clave, _, _ in ENTRADAS}
        self.etiquetas: dict[str, ttk.Label] = {}
        self.botones: dict[str, ttk.Button] = {}
        self._calculo: proceso.Calculo | None = None
        self._cola: queue.Queue = queue.Queue()
        self.ocupado = False

        marco = ttk.Frame(root, padding=12)
        marco.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)

        for fila, (clave, nombre, tipos) in enumerate(ENTRADAS):
            ttk.Label(marco, text=f"{nombre}:").grid(row=fila, column=0, sticky="w", pady=3)
            etiqueta = ttk.Label(marco, text=SIN_SELECCION, width=50, relief="sunken", padding=(4, 2))
            etiqueta.grid(row=fila, column=1, sticky="ew", padx=6)
            boton = ttk.Button(marco, text="Seleccionar…", command=lambda c=clave, n=nombre, t=tipos: self.elegir(c, n, t))
            boton.grid(row=fila, column=2)
            self.etiquetas[clave], self.botones[clave] = etiqueta, boton

        fila = len(ENTRADAS)
        ttk.Label(marco, text="Nº de artículos del FICHERO BASE:").grid(row=fila, column=0, sticky="w", pady=6)
        self.var_n = tk.StringVar()
        self.ent_n = ttk.Entry(marco, textvariable=self.var_n, width=10)
        self.ent_n.grid(row=fila, column=1, sticky="w", padx=6)

        self.btn_ejecutar = ttk.Button(marco, text="Ejecutar", command=self.ejecutar)
        self.btn_ejecutar.grid(row=fila + 1, column=0, columnspan=3, pady=(8, 4))
        self.progreso = ttk.Progressbar(marco, mode="indeterminate")
        self.progreso.grid(row=fila + 2, column=0, columnspan=3, sticky="ew")
        self.progreso.grid_remove()
        self.lbl_estado = ttk.Label(marco, text="")
        self.lbl_estado.grid(row=fila + 3, column=0, columnspan=3)

        marco.rowconfigure(fila + 4, weight=1)
        self.txt_resumen = tk.Text(marco, height=16, width=96, wrap="word", state="disabled")
        self.txt_resumen.grid(row=fila + 4, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.txt_resumen.yview)
        barra.grid(row=fila + 4, column=3, sticky="ns", pady=(8, 0))
        self.txt_resumen.configure(yscrollcommand=barra.set)

    def elegir(self, clave: str, nombre: str, tipos):
        ruta = filedialog.askopenfilename(title=f"Seleccionar {nombre}", filetypes=tipos)
        if ruta:
            self.rutas[clave] = Path(ruta)
            self.etiquetas[clave].configure(text=self.rutas[clave].name)

    def ejecutar(self):
        if self.ocupado:
            return
        for clave, nombre, _ in ENTRADAS:
            if self.rutas[clave] is None:
                messagebox.showwarning("Falta un fichero", f"Selecciona el fichero de {nombre}.")
                return
        try:
            n = parsear_n(self.var_n.get())
        except ErrorValidacion as exc:
            messagebox.showwarning("Dato no válido", str(exc))
            return
        existentes = [d for d in proceso.rutas_salida(self.rutas["salalm"]) if d.exists()]
        if existentes and not messagebox.askyesno(
            "Sobrescribir",
            "Ya existe:\n" + "\n".join(f"  {d}" for d in existentes) + "\n\n¿Quieres sobrescribir?",
        ):
            return
        rutas = dict(self.rutas)

        def tarea():
            self._calculo = proceso.calcular(
                rutas["salalm"], rutas["maestro"], rutas["caducidad"], rutas["access"], n, progreso=self._fase
            )
            self._fase("Guardando…")
            return self._calculo.guardar()

        self._escribir_resumen("")
        self._lanzar(tarea)

    def _fase(self, texto: str):
        self._cola.put(("fase", texto))

    def _lanzar(self, tarea):
        self.ocupado = True
        self._controles("disabled")
        self.progreso.grid()
        self.progreso.start(12)
        threading.Thread(target=self._trabajar, args=(tarea,), daemon=True).start()
        self.root.after(100, self._comprobar)

    def _trabajar(self, tarea):
        try:
            self._cola.put(("ok", tarea()))
        except ErrorEscritura as exc:
            self._cola.put(("escritura", exc))
        except ErrorValidacion as exc:
            self._cola.put(("validacion", exc))
        except MemoryError:
            self._cola.put(("validacion", ErrorValidacion(
                "No hay memoria suficiente para leer el Access. Cierra otros programas y vuelve a intentarlo."
            )))
        except Exception as exc:  # noqa: BLE001 - se muestra al usuario sin traza
            self._cola.put(("inesperado", exc))

    def _comprobar(self):
        while True:
            try:
                tipo, valor = self._cola.get_nowait()
            except queue.Empty:
                self.root.after(100, self._comprobar)
                return
            if tipo == "fase":
                self.lbl_estado.configure(text=valor)
                continue
            break
        self._terminar()
        if tipo == "ok":
            self._escribir_resumen(valor.texto())
            self.lbl_estado.configure(text="Proceso terminado.")
            messagebox.showinfo("Proceso terminado", f"Se han generado:\n{valor.ruta_salalm}\n{valor.ruta_base}")
        elif tipo == "escritura":
            self.lbl_estado.configure(text="No se pudo guardar.")
            if messagebox.askretrycancel("No se puede guardar", str(valor)):
                self._lanzar(self._calculo.guardar)
        elif tipo == "validacion":
            self.lbl_estado.configure(text="Revisa los datos y vuelve a ejecutar.")
            self._escribir_resumen(str(valor))
            messagebox.showerror("Error en los datos", str(valor))
        else:
            self.lbl_estado.configure(text="Error inesperado.")
            messagebox.showerror("Error inesperado", f"Se ha producido un error inesperado:\n{valor}")

    def _controles(self, estado: str):
        marca = ["disabled"] if estado == "disabled" else ["!disabled"]
        for control in (self.btn_ejecutar, self.ent_n, *self.botones.values()):
            control.state(marca)

    def _terminar(self):
        self.ocupado = False
        self.progreso.stop()
        self.progreso.grid_remove()
        self._controles("normal")

    def _escribir_resumen(self, texto: str):
        self.txt_resumen.configure(state="normal")
        self.txt_resumen.delete("1.0", "end")
        self.txt_resumen.insert("1.0", texto)
        self.txt_resumen.configure(state="disabled")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
