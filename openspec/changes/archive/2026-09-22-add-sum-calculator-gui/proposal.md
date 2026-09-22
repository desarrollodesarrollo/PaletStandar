# Proposal

## Why

The repository currently only has command-line scripts (`suma.py`) for basic arithmetic. The user wants a sum calculator with a graphical interface that non-technical users can run directly, plus a standalone executable so it can be launched without needing Python installed or invoked from a terminal.

## What Changes

- Add a desktop GUI application that lets a user enter two numbers and see their sum, built with Python's standard `tkinter` library (no extra runtime dependencies).
- Add input validation so non-numeric input shows a clear error instead of crashing.
- Add a build step (via PyInstaller) that packages the GUI app into a single standalone executable for the platform it's built on, so it can be launched by double-clicking / running the binary without a Python environment.
- Add a short README section (or script) documenting how to run the app from source and how to build/launch the executable.

## Capabilities

### New Capabilities
- `sum-calculator-gui`: A desktop GUI application that adds two numbers entered by the user and displays the result, distributable as a standalone executable.

### Modified Capabilities
(none)

## Impact

- New files: GUI application source (e.g. `calculadora_gui.py`), a PyInstaller build script/config, and build/usage documentation.
- New dev-time dependency: `pyinstaller` (only needed to produce the executable, not to run the app from source).
- No impact on existing `suma.py` / `holamundo2.py` scripts — they are left as-is.
