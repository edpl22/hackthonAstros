import pytest

from app.atividades.pizza import logica


@pytest.mark.parametrize(
    ("f", "esperado"), [((3, 4), "3/4"), ((15, 8), "1 e 7/8"), ((8, 8), "1"), ((16, 8), "2")]
)
def test_misto(f, esperado):
    assert logica.misto(f) == esperado


@pytest.mark.parametrize("semente", range(40))
def test_rodadas_validas(semente):
    m = logica.nova_rodada(logica.MONTAR, semente)
    assert m.corte in logica.CORTES and 1 <= m.certo[0] < m.corte

    s = logica.nova_rodada(logica.SOMAR, semente)
    (n1, d), (n2, _) = s.parcelas
    assert s.certo == (n1 + n2, d) and n1 + n2 < d  # cabe numa pizza
    valores = [c.valor for c in s.cartoes]
    assert len(set(valores)) == 3 and s.certo in valores
    assert (n1 + n2, 2 * d) in valores  # sempre o cartão de somar denominadores

    desafio = logica.nova_rodada(logica.DESAFIO, semente)
    assert desafio.certo[0] > desafio.corte  # fração imprópria


def test_tea_cortes_menores():
    assert all(logica.nova_rodada(logica.MONTAR, s, max_itens=3).corte <= 4 for s in range(30))


def test_conferir():
    r = logica.Rodada(logica.SOMAR, 4, [(1, 4), (2, 4)], (3, 4))
    assert logica.conferir_soma(r, (3, 4)) is None
    assert logica.conferir_soma(r, (3, 8)) == "somou_denominadores"
    assert logica.conferir_soma(r, (4, 3)) == "confundiu_numerador_denominador"
    m = logica.Rodada(logica.MONTAR, 4, [(3, 4)], (3, 4))
    assert logica.conferir_montar(m, 3) is None
    assert logica.conferir_montar(m, 2) == "contou_fatias_errado"
