# Design

## Context

The repository currently has no application structure — only two standalone scripts (`holamundo2.py`, `suma.py`) at the root. See proposal.md - Why for the motivation. This design covers the GUI implementation and how the standalone executable is produced.

## Goals / Non-Goals

**Goals:**
- Keep the GUI implementation dependency-free at runtime (usable directly with a stock Python install, no `pip install` required to run from source).
- Produce a single-file executable via a build step, without requiring the end user to have Python or PyInstaller installed.
- Keep the build reproducible with one command.

**Non-Goals:**
- Cross-compiling for multiple OSes from a single build run (the executable targets whatever platform it's built on, per the spec's "Standalone executable" requirement).
- Advanced calculator features (subtraction, multiplication, history, etc.) — scope is limited to summing two numbers.
- Auto-updating or installer/packaging beyond a single executable file.

## Decisions

- **GUI toolkit: `tkinter`** (Python standard library) instead of a third-party toolkit (PyQt, Kivy, etc.). Rationale: ships with standard CPython installs, so there's nothing to install to run from source, and it keeps the PyInstaller bundle small. Alternative considered: PyQt5/PySide6 — rejected as unnecessary weight and an extra license/dependency for a two-field form.
- **Packaging tool: PyInstaller**, invoked as `pyinstaller --onefile --windowed calculadora_gui.py`. Rationale: the de-facto standard for turning a Python script into a standalone executable, handles bundling the Python runtime and tkinter automatically. Alternative considered: `cx_Freeze` — rejected, PyInstaller has simpler one-file output and is more commonly available.
- **File layout**: `calculadora_gui.py` at the repo root (consistent with existing `suma.py`, `holamundo2.py`), plus a `build_exe.sh` helper script that runs PyInstaller with the right flags and reports where the built binary ends up (`dist/calculadora_gui` or `dist/calculadora_gui.exe`).
- **Validation approach**: parse both fields with `float()` inside a try/except in the button's click handler; on failure, show a `tkinter.messagebox` error dialog rather than raising, satisfying the "does not crash" requirement.

## Risks / Trade-offs

- [PyInstaller is not installed in most environments] → Documented as a one-time `pip install pyinstaller` step in the build script's usage notes; only needed to build the executable, not to run the app from source.
- [The build only produces an executable for the OS it's built on] → Acceptable per Non-Goals; documented clearly in the README/usage notes so it isn't mistaken for a cross-platform binary.
- [`tkinter` may be missing from minimal/headless Python installs (e.g. some Linux distros ship Python without it)] → Documented as a prerequisite; not worked around, since adding a GUI toolkit dependency to avoid this would contradict the "no extra runtime dependency" goal.
