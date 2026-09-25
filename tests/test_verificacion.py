from fractions import Fraction

import pytest

from pruebaestandar.modelo import DatosBase, DemandaTienda, ErrorValidacion
from pruebaestandar.verificacion import errores_tienda, verificar

from .conftest import articulo, fr, medio


def test_seleccion_valida_sin_errores():
    arts = [articulo(0, 400, 620), articulo(1, 400, 620)]  # 800 kg, 1240 L -> 0,645 kg/L
    assert errores_tienda(arts, fr([2, 2]), medio(), 1, {0: 1, 1: 1}) == []


def test_detecta_volumen_por_encima_del_96_por_ciento():
    arts = [articulo(0, 400, 645), articulo(1, 400, 645)]  # 1290 L > 1248 L
    errores = errores_tienda(arts, fr([2, 2]), medio(), 1, {0: 1, 1: 1})
    assert errores == ["volumen 1290.00 L supera el máximo 1248.00 L (96 %)"]


def test_limites_exactos_del_96_por_ciento_son_validos():
    arts = [articulo(0, 420, 624)]  # 2 cajas = 840 kg y 1248 L, densidad 0,673 < 0,6731
    assert errores_tienda(arts, fr([2]), medio(densidad="0.6731"), 1, {0: 2}) == []


def test_detecta_volumen_excedido_en_tienda_10082():
    arts = [articulo(0, 10, 700)]
    datos = DatosBase(arts, [DemandaTienda(10082, 7, fr([5]), fr([1]))])
    with pytest.raises(ErrorValidacion, match=r"Tienda 10082: volumen 1400.00 L supera"):
        verificar(datos, {10082: medio()}, 1, {10082: {0: 2}})


def test_detecta_seleccion_demasiado_densa():
    arts = [articulo(0, 700, 1000)]  # 0,70 kg/L >= 0,673
    assert any("densidad 0.7000" in e for e in errores_tienda(arts, fr([1]), medio(), 1, {0: 1}))


@pytest.mark.parametrize(
    "seleccion,texto",
    [
        ({0: 2.0}, "no entero"),
        ({0: 0}, "no entero"),
        ({0: True}, "no entero"),
        ({0: 3}, "superan el máximo 2"),
        ({1: 1}, "sin salida de bultos"),
        ({2: 1}, "sin peso o volumen"),
        ({7: 1}, "inexistente"),
    ],
)
def test_detecta_cada_incumplimiento(seleccion, texto):
    arts = [articulo(0, 1, 10), articulo(1, 1, 10), articulo(2, 0, 10)]
    errores = errores_tienda(arts, fr([10, 0, 3]), medio(), 5, seleccion)
    assert any(texto in e for e in errores), errores


def test_detecta_peso_excedido_con_carros():
    arts = [articulo(0, 500, 1000)]
    errores = errores_tienda(arts, fr([2]), medio("CARRO", 475, 600, densidad=10), 1, {0: 2})
    assert any("peso 1000.00 kg supera el máximo 912.00" in e for e in errores)


def test_tienda_sin_seleccion_es_valida():
    assert errores_tienda([articulo(0, 1, 1)], [Fraction(3)], medio(), 1, {}) == []
