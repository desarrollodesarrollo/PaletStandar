import random
from fractions import Fraction

import pytest

from pruebaestandar.modelo import ErrorValidacion
from pruebaestandar.seleccion import maximo_cajas, parsear_dias, seleccionar
from pruebaestandar.verificacion import errores_tienda

from .conftest import articulo, fr, medio

HOLGADO = dict(peso=10_000, densidad=100)  # sólo limita el volumen


# 3.1
@pytest.mark.parametrize("texto,esperado", [("5", 5), (" 7 ", 7), ("1", 1), (30, 30)])
def test_dias_validos(texto, esperado):
    assert parsear_dias(texto) == esperado


@pytest.mark.parametrize("texto", ["0", "-3", "2,5", "2.5", "5.0", "abc", "", "   ", None])
def test_dias_no_validos(texto):
    with pytest.raises(ErrorValidacion, match="entero mayor que 0"):
        parsear_dias(texto)


@pytest.mark.parametrize("bultos,dias,maximo", [(10, 5, 2), (7, 5, 2), (1, 20, 1), (Fraction(5, 2), 1, 3), (5, 5, 1)])
def test_maximo_cajas(bultos, dias, maximo):
    assert maximo_cajas(Fraction(bultos), dias) == maximo


# 3.2
def test_mas_lineas_mas_cajas():
    arts = [articulo(0, 10, 100), articulo(1, 10, 100)]
    sel = seleccionar(arts, fr([5, 5]), fr([10, 4]), medio(volumen=300, **HOLGADO), dias=1)
    assert sel == {0: 2, 1: 1}


def test_reparto_proporcional_a_lineas():
    arts = [articulo(0, 1, 10), articulo(1, 1, 10), articulo(2, 1, 10)]
    sel = seleccionar(arts, fr([50, 50, 50]), fr([12, 6, 3]), medio(volumen=70, **HOLGADO), dias=1)
    assert sel == {0: 4, 1: 2, 2: 1}


def test_empate_prefiere_articulo_nuevo():
    # A (10 líneas) con 1 caja -> índice 5; B (5 líneas) sin cajas -> índice 5: gana B por variedad
    arts = [articulo(0, 1, 10), articulo(1, 1, 10)]
    sel = seleccionar(arts, fr([9, 9]), fr([10, 5]), medio(volumen=20, **HOLGADO), dias=1)
    assert sel == {0: 1, 1: 1}


def test_empate_prefiere_menor_volumen_y_luego_menor_codigo():
    arts = [articulo(0, 1, 12, codigo=5), articulo(1, 1, 10, codigo=9), articulo(2, 1, 10, codigo=7)]
    sel = seleccionar(arts, fr([1, 1, 1]), fr([3, 3, 3]), medio(volumen=10, **HOLGADO), dias=1)
    assert sel == {2: 1}


# 3.3
def test_caja_que_no_cabe_no_bloquea_al_resto():
    arts = [articulo(0, 1, 30), articulo(1, 1, 30), articulo(2, 1, 12)]
    sel = seleccionar(arts, fr([1, 1, 1]), fr([10, 9, 1]), medio(volumen=42, **HOLGADO), dias=1)
    assert sel == {0: 1, 2: 1}


def test_articulo_denso_compensado_por_ligeros():
    arts = [articulo(0, 9.7, 10), articulo(1, 1, 10)]  # 0,97 y 0,10 kg/L
    sel = seleccionar(arts, fr([1, 1]), fr([10, 1]), medio(), dias=1)  # palet 0,673 kg/L
    assert sel == {0: 1, 1: 1}


def test_seleccion_demasiado_densa_rechazada():
    arts = [articulo(0, 9.7, 10)]
    assert seleccionar(arts, fr([5]), fr([10]), medio(), dias=1) == {}


def test_densidad_igual_al_limite_no_se_admite():
    arts = [articulo(0, 5, 10)]
    assert seleccionar(arts, fr([1]), fr([1]), medio(peso=100, volumen=200, densidad="0.5"), dias=1) == {}


def test_limite_de_peso_con_dos_carros():
    arts = [articulo(0, 60, 1)]
    sel = seleccionar(arts, fr([10]), fr([1]), medio("CARRO", peso=100, volumen=1000, densidad=100), dias=1)
    assert sel == {0: 3}  # 180 kg ≤ 200 kg; 240 kg no cabe


def test_todo_cabe_todos_al_maximo():
    arts = [articulo(i, 2, 10) for i in range(4)]
    sel = seleccionar(arts, fr([7, 3, 10, 1]), fr([4, 3, 2, 1]), medio(), dias=5)
    assert sel == {0: 2, 1: 1, 2: 2, 3: 1}


def test_tienda_sin_articulos_elegibles():
    arts = [articulo(i, 2, 10) for i in range(3)]
    assert seleccionar(arts, fr([0, 0, 0]), fr([0, 0, 0]), medio(), dias=1) == {}


def test_articulo_sin_salida_o_sin_medidas_nunca_se_elige():
    arts = [articulo(0, 2, 10), articulo(1, 0, 10), articulo(2, 2, 10)]
    sel = seleccionar(arts, fr([0, 5, 1]), fr([50, 40, 1]), medio(), dias=1)
    assert sel == {2: 1}


# 3.4
def _tienda_aleatoria(rnd):
    n = rnd.randint(1, 120)
    arts = []
    for i in range(n):
        volumen = round(rnd.uniform(0.5, 60), 3)
        peso = round(volumen * rnd.uniform(0.005, 1.0), 2) if rnd.random() > 0.02 else 0
        arts.append(articulo(i, peso, volumen))
    bultos = fr([rnd.choice([0, 0, rnd.randint(1, 80), round(rnd.uniform(0.1, 40), 1)]) for _ in range(n)])
    lineas = fr([rnd.randint(0, 20) for _ in range(n)])
    m = medio(*rnd.choice([("PALET", 875, 1300), ("CARRO", 475, 600), ("PALET", 50, 90)]))
    return arts, bultos, lineas, m, rnd.randint(1, 30)


def test_resultado_determinista():
    arts, bultos, lineas, m, dias = _tienda_aleatoria(random.Random(7))
    assert seleccionar(arts, bultos, lineas, m, dias) == seleccionar(arts, bultos, lineas, m, dias)


def test_propiedades_200_tiendas_aleatorias():
    rnd = random.Random(20260923)
    for _ in range(200):
        arts, bultos, lineas, m, dias = _tienda_aleatoria(rnd)
        sel = seleccionar(arts, bultos, lineas, m, dias)
        assert errores_tienda(arts, bultos, m, dias, sel) == []
        # Al terminar, ninguna caja más de ningún artículo elegible cabe (no queda hueco aprovechable).
        peso = sum(q * arts[i].peso for i, q in sel.items())
        vol = sum(q * arts[i].volumen for i, q in sel.items())
        for i, art in enumerate(arts):
            if art.valido and bultos[i] > 0 and sel.get(i, 0) < maximo_cajas(bultos[i], dias):
                p, v = peso + art.peso, vol + art.volumen
                assert p > m.peso_max or v > m.volumen_max or not p < m.densidad * v
