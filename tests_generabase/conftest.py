import importlib.util

# Sin las dependencias de GENERABASE (p. ej. en la compilación de PRUEBAESTANDAR) sus pruebas no se recogen.
if importlib.util.find_spec("access_parser") is None:
    collect_ignore_glob = ["test_*.py"]
else:
    from .apoyo import entradas, falso_access  # noqa: F401  (fixtures)
