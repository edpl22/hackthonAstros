"""Regras pedagógicas: pistas graduais, ajuste de nível e classificação de erros."""

import pytest

from app.nucleo import erros, progresso
from app.nucleo.progresso import ControleNivel, Pistas

# --- pistas -------------------------------------------------------------------------


def test_pistas_sobem_ate_o_modelo_e_param():
    p = Pistas()
    assert p.primeira_tentativa and not p.precisou_modelo
    assert [p.errar(), p.errar(), p.errar(), p.errar()] == [
        progresso.REPETIR_INSTRUCAO, progresso.REALCAR,
        progresso.MOSTRAR_MODELO, progresso.MOSTRAR_MODELO,
    ]
    assert p.precisou_modelo and not p.primeira_tentativa


# --- nível -------------------------------------------------------------------------


def test_quatro_acertos_seguidos_oferecem_desafio():
    n = ControleNivel(nivel=1, nivel_maximo=2)
    assert [n.registrar_item(True, False) for _ in range(3)] == [None, None, None]
    assert n.registrar_item(True, False) == progresso.OFERECER_DESAFIO
    assert n.aceitar_desafio() == 2


def test_erro_no_meio_zera_a_sequencia_de_acertos():
    n = ControleNivel(nivel=1, nivel_maximo=2)
    for ok in (True, True, True, False, True, True, True):
        assert n.registrar_item(ok, False) is None
    assert n.registrar_item(True, False) == progresso.OFERECER_DESAFIO


def test_nao_oferece_desafio_no_nivel_maximo():
    n = ControleNivel(nivel=2, nivel_maximo=2)
    assert all(n.registrar_item(True, False) is None for _ in range(8))


def test_dois_modelos_seguidos_voltam_um_nivel():
    n = ControleNivel(nivel=2, nivel_maximo=3)
    assert n.registrar_item(False, True) is None
    assert n.registrar_item(False, True) == progresso.VOLTAR_NIVEL
    assert n.nivel == 1
    assert n.registrar_item(False, True) is None
    assert n.registrar_item(False, True) is None  # já está no nível 1


def test_modelos_nao_seguidos_nao_voltam():
    n = ControleNivel(nivel=2, nivel_maximo=3)
    for item in [(False, True), (False, False), (False, True)]:
        assert n.registrar_item(*item) is None
    assert n.nivel == 2


def test_professor_trava_o_nivel():
    n = ControleNivel(nivel=2, nivel_maximo=3, travado=True)
    assert all(n.registrar_item(True, False) is None for _ in range(8))
    assert all(n.registrar_item(False, True) is None for _ in range(4))
    assert n.aceitar_desafio() == 2


# --- erros ---------------------------------------------------------------------------


def test_treino():
    assert erros.classificar_treino("A", "A") is None
    assert erros.classificar_treino("a", "A") is None  # minúscula na caixa maiúscula
    assert erros.classificar_treino("B", "A") == "letra_trocada"


@pytest.mark.parametrize(
    ("silabas", "posicao", "colocada", "esperado"),
    [
        (["BO", "LA"], 0, "BO", None),
        (["BO", "LA"], 0, "LA", "ordem_trocada"),
        (["BO", "LA"], 0, "PO", "par_surdo_sonoro"),
        (["PA", "TO"], 1, "DO", "par_surdo_sonoro"),
        (["VA", "CA"], 0, "FA", "par_surdo_sonoro"),
        (["GA", "TO"], 0, "CA", "par_surdo_sonoro"),
        (["BO", "LA"], 1, "SA", "silaba_de_outra_palavra"),
        (["BO", "LA"], 1, "LO", "silaba_de_outra_palavra"),
    ],
)
def test_silabas(silabas, posicao, colocada, esperado):
    assert erros.classificar_silaba(silabas, posicao, colocada) == esperado


def test_par_surdo_sonoro_exige_mesma_vogal():
    assert erros.eh_par_surdo_sonoro("BO", "PO")
    assert not erros.eh_par_surdo_sonoro("BO", "PA")
    assert not erros.eh_par_surdo_sonoro("BO", "MO")


@pytest.mark.parametrize(
    ("resposta", "certo", "a", "b", "op", "tempo", "esperado"),
    [
        (7, 7, 3, 4, "+", 5000, None),
        (8, 7, 3, 4, "+", 5000, "um_a_mais_ou_menos"),
        (6, 7, 3, 4, "+", 5000, "um_a_mais_ou_menos"),
        (2, 6, 4, 2, "+", 5000, "operacao_trocada"),
        (9, 5, 7, 2, "-", 5000, "operacao_trocada"),
        (21, 12, 8, 4, "+", 5000, "digitos_invertidos"),
        (15, 7, 3, 4, "+", 900, "chute"),
        (15, 7, 3, 4, "+", 5000, "outro"),
        (8, 7, 3, 4, "+", 900, "um_a_mais_ou_menos"),  # padrão vence o chute
    ],
)
def test_quantidades(resposta, certo, a, b, op, tempo, esperado):
    assert erros.classificar_quantidade(resposta, certo, a, b, op, tempo) == esperado


@pytest.mark.parametrize(
    ("resposta", "parcelas", "esperado"),
    [
        ((3, 4), [(1, 4), (2, 4)], None),
        ((3, 8), [(1, 4), (2, 4)], "somou_denominadores"),
        ((4, 3), [(1, 4), (2, 4)], "confundiu_numerador_denominador"),
        ((2, 4), [(1, 4), (2, 4)], "contou_fatias_errado"),
        ((15, 8), [(7, 8), (8, 8)], None),
        ((15, 16), [(7, 8), (8, 8)], "somou_denominadores"),
        ((6, 8), [(1, 4), (2, 4)], None),  # equivalente
        ((1, 3), [(1, 4), (2, 4)], "outro"),
    ],
)
def test_fracoes(resposta, parcelas, esperado):
    assert erros.classificar_fracao(resposta, parcelas) == esperado


def test_todo_tipo_de_erro_tem_recomendacao():
    tipos = {
        "letra_trocada", "ordem_trocada", "par_surdo_sonoro", "silaba_de_outra_palavra",
        "um_a_mais_ou_menos", "operacao_trocada", "digitos_invertidos", "chute",
        "somou_denominadores", "contou_fatias_errado", "confundiu_numerador_denominador", "outro",
    }
    for tipo in tipos:
        rec = erros.recomendacao(tipo)
        assert rec["descricao"] and rec["sugestao"]


def test_frase_para_professor():
    frase = erros.frase_para_professor("Ana", "somou_denominadores", 3, 4)
    assert frase == (
        "Ana somou os denominadores em 3 de 4 tentativas. "
        "Sugestão: pizzas sobrepostas, mostrando que o tamanho da fatia não muda."
    )
