"""Recuento de días de datos de PRUEBAESTANDAR: MVFECI distintos de todas las filas PI."""

from generabase import access

from .apoyo import crear_access, mov


def filtrar(tmp_path, movs):
    return access.filtrar(access.leer_movimientos(crear_access(tmp_path / "a.accdb", movs)))


def test_dias_pi_cuenta_fechas_distintas_solo_de_pi(tmp_path, falso_access):
    movs = [mov(1, 10081, 6, 6, fecha=20251001), mov(2, 10082, 6, 6, fecha=20251001), mov(1, 10082, 6, 6, fecha=20251002),
            mov(3, 10400, 6, 6, fecha=20251006), mov(1, 10081, 6, 6, tipo="PS", fecha=20251003)]
    usados = filtrar(tmp_path, movs)
    assert usados.dias_pi == 3 and usados.fechas_pi == {20251001, 20251002, 20251006}
    assert (usados.fecha_pi_min, usados.fecha_pi_max) == (20251001, 20251006)
    assert usados.pi_sin_fecha == 0 and usados.aviso_pi_sin_fecha is None


def test_dias_pi_incluye_tiendas_fuera_de_rango_y_no_validas(tmp_path, falso_access):
    movs = [mov(1, 10081, 6, 6, fecha=20251001), mov(1, 10350, 6, 6, fecha=20251007), mov(1, "TIENDA", 6, 6, fecha=20251008),
            mov(1, 10081, 6, 0, fecha=20251009), mov(1, 10081, 6, 6, tipo=" pi ", fecha=20251010)]
    usados = filtrar(tmp_path, movs)
    assert usados.fechas_pi == {20251001, 20251007, 20251008, 20251009, 20251010} and usados.dias == 2


def test_pi_sin_fecha_no_cuenta_y_avisa_sin_cambiar_los_avisos_de_generabase(tmp_path, falso_access):
    movs = [mov(1, 10081, 6, 6, fecha=20251001), mov(1, 10350, 6, 6, fecha=None), mov(1, 10360, 6, 6, fecha="abc"),
            mov(1, 10081, 6, 6, tipo="SI", fecha=None)]
    usados = filtrar(tmp_path, movs)
    assert usados.dias_pi == 1 and usados.pi_sin_fecha == 2
    assert "2 filas PI sin fecha" in usados.aviso_pi_sin_fecha and usados.avisos == []


def test_sin_filas_pi(tmp_path, falso_access):
    usados = filtrar(tmp_path, [mov(1, 10081, 6, 6, tipo="SI")])
    assert usados.dias_pi == 0 and usados.fecha_pi_min is None and usados.fecha_pi_max is None
