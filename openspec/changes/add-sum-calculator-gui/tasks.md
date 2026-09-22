# Tasks

## 1. GUI application

- [ ] 1.1 Create `calculadora_gui.py` at the repo root with a `tkinter` window containing two number input fields, a "Sumar" button, and a result label, and verify it launches with `python3 calculadora_gui.py` showing the window
- [ ] 1.2 Wire the "Sumar" button to parse both fields as `float`, compute the sum, and display it in the result label, and verify entering `2` and `5` and clicking the button shows `7`
- [ ] 1.3 Add input validation that catches non-numeric or empty fields and shows a `tkinter.messagebox` error without crashing, and verify entering `abc` (or leaving a field empty) and clicking the button shows an error dialog and the app remains open

## 2. Executable build

- [ ] 2.1 Add `build_exe.sh`, a script that installs PyInstaller if missing and runs `pyinstaller --onefile --windowed calculadora_gui.py`, and verify running it produces a binary under `dist/`
- [ ] 2.2 Run the build and verify the produced executable launches the calculator window without a separate Python invocation (e.g. `./dist/calculadora_gui`)

## 3. Documentation

- [ ] 3.1 Add a short usage section (README or top-of-file comment) covering how to run `calculadora_gui.py` from source and how to build/launch the executable via `build_exe.sh`, and verify the documented commands match the actual script names and paths
