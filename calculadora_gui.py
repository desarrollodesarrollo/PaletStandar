"""
Calculadora de sumas con interfaz grafica (tkinter).

Ejecutar desde el codigo fuente:
    python3 calculadora_gui.py

Para generar un ejecutable independiente, ver build_exe.sh.
"""

import tkinter as tk
from tkinter import messagebox


def sumar():
    valor_a = entry_a.get().strip()
    valor_b = entry_b.get().strip()

    if not valor_a or not valor_b:
        messagebox.showerror("Error", "Debes introducir un valor en ambos campos.")
        return

    try:
        a = float(valor_a)
        b = float(valor_b)
    except ValueError:
        messagebox.showerror("Error", "Los valores introducidos no son numeros validos.")
        return

    resultado_var.set(str(a + b))


root = tk.Tk()
root.title("Calculadora de sumas")

tk.Label(root, text="Numero 1:").grid(row=0, column=0, padx=5, pady=5)
entry_a = tk.Entry(root)
entry_a.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Numero 2:").grid(row=1, column=0, padx=5, pady=5)
entry_b = tk.Entry(root)
entry_b.grid(row=1, column=1, padx=5, pady=5)

tk.Button(root, text="Sumar", command=sumar).grid(row=2, column=0, columnspan=2, pady=10)

resultado_var = tk.StringVar()
tk.Label(root, text="Resultado:").grid(row=3, column=0, padx=5, pady=5)
tk.Label(root, textvariable=resultado_var).grid(row=3, column=1, padx=5, pady=5)

if __name__ == "__main__":
    root.mainloop()
