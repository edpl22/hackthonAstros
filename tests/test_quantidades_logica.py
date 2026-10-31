import pytest

from app.atividades.quantidades import logica


def test_tres_conjuntos_com_figura():
    from app.nucleo import caminhos

    ids = [c.id for c in logica.conjuntos()]
    assert ids == ["maca", "peixe", "bolinha"]
    for c in logica.conjuntos():
        assert caminhos.asset(c.figura).exists()


@pytest.mark.parametrize(
    ("n", "conjunto", "esperado"),
    [
        (0, "maca", "nenhuma maçã"), (1, "maca", "uma maçã"), (2, "maca", "duas maçãs"),
        (3, "maca", "três maçãs"), (1, "peixe", "um peixe"), (2, "peixe", "dois peixes"),
        (12, "bolinha", "doze bolinhas de gude"), (0, "peixe", "nenhum peixe"),
    ],
)
def test_quantidade_por_extenso(n, conjunto, esperado):
    assert logica.quantidade(n, logica.conjunto(conjunto)) == esperado


def test_comparar():
    assert [logica.comparar(5, 3), logica.comparar(2, 4), logica.comparar(3, 3)] == [
        "maior", "menor", "igual",
    ]


@pytest.mark.parametrize("semente", range(30))
def test_rodadas_validas_em_todos_os_niveis(semente):
    montar = logica.nova_rodada(logica.MONTAR, semente)
    assert 2 <= montar.a <= 7 and [c.id for c in montar.cartoes] == ["cartao-pronto"]

    comparar = logica.nova_rodada(logica.COMPARAR, semente)
    assert comparar.certo == logica.comparar(comparar.a, comparar.b)
    assert {c.valor for c in comparar.cartoes} == {"maior", "menor", "igual"}

    for nivel in (logica.SOMA, logica.CONTAS):
        r = logica.nova_rodada(nivel, semente)
        valores = [c.valor for c in r.cartoes]
        assert len(valores) == len(set(valores)) == 3 and r.certo in valores
        assert 0 <= int(r.certo) <= 20 and r.a <= 12 and r.b <= 12
        if nivel == logica.SOMA:
            assert r.operacao == "+" and int(r.certo) <= 10


def test_cartoes_errados_tem_um_motivo():
    # 7 + 5 = 12: os errados são 2 (operação trocada) e 21 (dígitos invertidos).
    import random

    valores = logica._cartoes_de_conta(7, 5, "+", 12, random.Random(0))
    assert sorted(valores) == [2, 12, 21]


def test_max_itens_pequeno_usa_quantidades_menores():
    for semente in range(30):
        assert logica.nova_rodada(logica.MONTAR, semente, max_itens=3).a <= 5
        r = logica.nova_rodada(logica.COMPARAR, semente, max_itens=3)
        assert r.a <= 5 and r.b <= 5


def test_conferir():
    r = logica.Rodada(logica.SOMA, 3, 4, "+", "7")
    assert logica.conferir(r, "7", 5000) is None
    assert logica.conferir(r, "8", 5000) == "um_a_mais_ou_menos"
    assert logica.conferir(r, "15", 800) == "chute"
    montar = logica.Rodada(logica.MONTAR, 4, 0, None, "4")
    assert logica.conferir(montar, "pronto", 5000, contados=4) is None
    assert logica.conferir(montar, "pronto", 5000, contados=5) == "um_a_mais_ou_menos"
    comparar = logica.Rodada(logica.COMPARAR, 5, 3, None, "maior")
    assert logica.conferir(comparar, "menor", 5000) == "comparacao_errada"


def test_sinal():
    assert logica.sinal("-") == "−" and logica.sinal("+") == "+"
