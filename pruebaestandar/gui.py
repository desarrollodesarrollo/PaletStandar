from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from . import proceso
from .modelo import ErrorEscritura, ErrorValidacion
from .seleccion import parsear_dias

TIPOS_EXCEL = [("Ficheros Excel", "*.xlsx"), ("Todos los ficheros", "*.*")]
SIN_SELECCION = "(sin seleccionar)"


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("PRUEBAESTANDAR")
        self.ruta_base: Path | None = None
        self.ruta_tabla: Path | None = None
        self._calculo: proceso.Calculo | None = None
        self._cola: queue.Queue = queue.Queue()
        self.ocupado = False

        marco = ttk.Frame(root, padding=12)
        marco.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        marco.columnconfigure(1, weight=1)
        marco.rowconfigure(5, weight=1)

        ttk.Label(marco, text="Fichero base:").grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_base = ttk.Label(marco, text=SIN_SELECCION, width=50, relief="sunken", padding=(4, 2))
        self.lbl_base.grid(row=0, column=1, sticky="ew", padx=6)
        self.btn_base = ttk.Button(marco, text="Seleccionar…", command=self.elegir_base)
        self.btn_base.grid(row=0, column=2)

        ttk.Label(marco, text="Tabla de tiendas y medios:").grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_tabla = ttk.Label(marco, text=SIN_SELECCION, width=50, relief="sunken", padding=(4, 2))
        self.lbl_tabla.grid(row=1, column=1, sticky="ew", padx=6)
        self.btn_tabla = ttk.Button(marco, text="Seleccionar…", command=self.elegir_tabla)
        self.btn_tabla.grid(row=1, column=2)

        ttk.Label(marco, text="Nº de días de datos:").grid(row=2, column=0, sticky="w", pady=4)
        self.var_dias = tk.StringVar()
        self.ent_dias = ttk.Entry(marco, textvariable=self.var_dias, width=10)
        self.ent_dias.grid(row=2, column=1, sticky="w", padx=6)

        self.btn_ejecutar = ttk.Button(marco, text="Ejecutar", command=self.ejecutar)
        self.btn_ejecutar.grid(row=3, column=0, columnspan=3, pady=(10, 4))

        self.progreso = ttk.Progressbar(marco, mode="indeterminate")
        self.progreso.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.lbl_estado = ttk.Label(marco, text="")
        self.lbl_estado.grid(row=4, column=0, columnspan=3)
        self.progreso.grid_remove()

        self.txt_resumen = tk.Text(marco, height=12, width=80, wrap="word", state="disabled")
        self.txt_resumen.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.txt_resumen.yview)
        barra.grid(row=5, column=3, sticky="ns", pady=(8, 0))
        self.txt_resumen.configure(yscrollcommand=barra.set)

    def elegir_base(self):
        ruta = filedialog.askopenfilename(title="Seleccionar FICHERO BASE", filetypes=TIPOS_EXCEL)
        if ruta:
            self.ruta_base = Path(ruta)
            self.lbl_base.configure(text=self.ruta_base.name)

    def elegir_tabla(self):
        ruta = filedialog.askopenfilename(title="Seleccionar TABLA DE TIENDAS Y MEDIOS", filetypes=TIPOS_EXCEL)
        if ruta:
            self.ruta_tabla = Path(ruta)
            self.lbl_tabla.configure(text=self.ruta_tabla.name)

    def ejecutar(self):
        if self.ocupado:
            return
        if self.ruta_base is None:
            messagebox.showwarning("Falta un fichero", "Selecciona el FICHERO BASE.")
            return
        if self.ruta_tabla is None:
            messagebox.showwarning("Falta un fichero", "Selecciona la TABLA DE TIENDAS Y MEDIOS.")
            return
        try:
            dias = parsear_dias(self.var_dias.get())
            destinos = proceso.rutas_salida(self.ruta_base)
        except ErrorValidacion as exc:
            messagebox.showwarning("Dato no válido", str(exc))
            return
        existentes = [d for d in destinos if d.exists()]
        if existentes and not messagebox.askyesno(
            "Sobrescribir",
            "Ya existe:\n" + "\n".join(f"  {d}" for d in existentes) + "\n\n¿Quieres sobrescribir?",
        ):
            return

        base, tabla = self.ruta_base, self.ruta_tabla

        def tarea():
            self._calculo = proceso.calcular(base, tabla, dias)
            return self._calculo.guardar()

        self._escribir_resumen("")
        self._lanzar(tarea, "Calculando…")

    def _lanzar(self, tarea, estado: str):
        self.ocupado = True
        for control in (self.btn_ejecutar, self.btn_base, self.btn_tabla, self.ent_dias):
            control.state(["disabled"])
        self.lbl_estado.grid_remove()
        self.progreso.grid()
        self.progreso.start(12)
        self.root.title(f"PRUEBAESTANDAR - {estado}")
        threading.Thread(target=self._trabajar, args=(tarea,), daemon=True).start()
        self.root.after(100, self._comprobar)

    def _trabajar(self, tarea):
        try:
            self._cola.put(("ok", tarea()))
        except ErrorEscritura as exc:
            self._cola.put(("escritura", exc))
        except ErrorValidacion as exc:
            self._cola.put(("validacion", exc))
        except Exception as exc:  # noqa: BLE001 - se muestra al usuario sin traza
            self._cola.put(("inesperado", exc))

    def _comprobar(self):
        try:
            tipo, valor = self._cola.get_nowait()
        except queue.Empty:
            self.root.after(100, self._comprobar)
            return
        self._terminar()
        if tipo == "ok":
            self._escribir_resumen(valor.texto())
            self.lbl_estado.configure(text="Proceso terminado.")
            messagebox.showinfo(
                "Proceso terminado", f"Se han generado:\n{valor.ruta_salida}\n{valor.ruta_reparto}"
            )
        elif tipo == "escritura":
            self.lbl_estado.configure(text="No se pudo guardar el fichero.")
            if messagebox.askretrycancel("No se puede guardar", str(valor)):
                self._lanzar(self._calculo.guardar, "Guardando…")
        elif tipo == "validacion":
            self.lbl_estado.configure(text="Revisa los datos y vuelve a ejecutar.")
            self._escribir_resumen(str(valor))
            messagebox.showerror("Error en los datos", str(valor))
        else:
            self.lbl_estado.configure(text="Error inesperado.")
            messagebox.showerror("Error inesperado", f"Se ha producido un error inesperado:\n{valor}")

    def _terminar(self):
        self.ocupado = False
        self.progreso.stop()
        self.progreso.grid_remove()
        self.lbl_estado.grid()
        for control in (self.btn_ejecutar, self.btn_base, self.btn_tabla, self.ent_dias):
            control.state(["!disabled"])
        self.root.title("PRUEBAESTANDAR")

    def _escribir_resumen(self, texto: str):
        self.txt_resumen.configure(state="normal")
        self.txt_resumen.delete("1.0", "end")
        self.txt_resumen.insert("1.0", texto)
        self.txt_resumen.configure(state="disabled")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
