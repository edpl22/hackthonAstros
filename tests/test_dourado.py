"""Jogo Dourado: lógica pura, classificação do erro e a tela por barramento, mouse e agente."""

import json

import pytest

from app.atividades.base import FIM, Contexto
from app.atividades.dourado import logica
from app.atividades.dourado.tela import TelaDourado, id_coluna
from app.entrada import mao_simulada
from app.entrada.camera import CameraNula
from app.headless import agente
from app.nucleo import erros
from app.nucleo.audio import ServicoAudio
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao

# --- lógica pura ------------------------------------------------------------------------


def test_algarismos_valor_e_texto():
    assert logica.algarismos(1234) == {"milhar": 1, "centena": 2, "dezena": 3, "unidade": 4}
    assert logica.valor({"milhar": 1, "centena": 0, "dezena": 5, "unidade": 0}) == 1050
    assert logica.texto_numero(7312) == "7.312" and logica.texto_numero(64) == "64"


@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_faixa_e_pilhas_de_cada_nivel(nivel):
    for semente in range(20):
        r = logica.nova_rodada(nivel, semente)
        menor, maior = logica.FAIXAS[nivel]
        assert menor <= r.numero <= maior
        assert len(r.ordens) == nivel + 1
        if nivel < 3:  # nos primeiros níveis toda pilha é usada
            assert 0 not in [logica.algarismos(r.numero)[o] for o in r.ordens]


def test_nao_repete_o_numero_anterior():
    r = logica.nova_rodada(1, 4)
    assert logica.nova_rodada(1, 4, anterior=r.numero).numero != r.numero


def test_classificar_dourado():
    certo = logica.algarismos(352)
    assert erros.classificar_dourado(dict(certo), certo) is None
    trocado = {"milhar": 0, "centena": 2, "dezena": 5, "unidade": 3}
    assert erros.classificar_dourado(trocado, certo) == "trocou_as_ordens"
    um_a_mais = {"milhar": 0, "centena": 3, "dezena": 6, "unidade": 2}
    assert erros.classificar_dourado(um_a_mais, certo) == "contou_pecas_errado"
    assert erros.classificar_dourado(dict.fromkeys(certo, 0), certo) == "outro"
    for tipo in ("trocou_as_ordens", "contou_pecas_errado"):
        assert erros.recomendacao(tipo)


# --- tela -------------------------------------------------------------------------------


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), CameraNula)
    t = TelaDourado(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _abrir(tela, nivel=2, semente=3):
    tela.ctx.sessao.definir(None)
    tela.iniciar(tela.ctx.sessao.perfil, semente=semente, nivel=nivel)
    tela.comecar()


def _topo(tela, ordem):
    return next(i for i in tela.pilhas[ordem] if not tela.cena.pecas[i].encaixada)


def _levar(tela, ordem, coluna=None, vezes=1):
    b = tela.barramento
    for _ in range(vezes):
        b.apontar.emit(*tela.cena.centro(_topo(tela, ordem)))
        b.pegar.emit()
        b.apontar.emit(*tela.cena.centro(id_coluna(coluna or ordem)))
        b.soltar.emit()


def _montar(tela, contagem):
    for ordem, n in contagem.items():
        if n and ordem in tela.pilhas:
            _levar(tela, ordem, vezes=n)


def test_tela_tem_numero_colunas_e_pilhas(tela):
    _abrir(tela, nivel=3)
    estado = tela.estado()
    assert estado["numero"] == tela.rodada.numero
    assert [a["id"] for a in estado["alvos"]] == [id_coluna(o) for o in logica.ORDENS]
    livres = [i["id"] for i in estado["itens"] if i["disponivel"]]
    assert len(livres) == 5  # só a peça de cima de cada pilha + "Pronto"


def test_monta_o_numero_e_conclui(tela):
    _abrir(tela)
    _montar(tela, logica.algarismos(tela.rodada.numero))
    assert tela.rodada.total == tela.rodada.numero
    tela.barramento.escolher.emit("cartao-pronto")
    assert tela.momento == FIM
    assert tela.ctx.registro.listar_tentativas()[-1]["correta"]


def test_peca_na_coluna_de_outra_ordem_volta(tela):
    _abrir(tela)
    _levar(tela, "unidade", coluna="centena")
    assert tela.cena.caixas[id_coluna("centena")].ocupantes == []
    assert tela.ultimo_anuncio.startswith("Um cubinho vai na coluna Unidade.")
    assert tela.ctx.registro.listar_tentativas() == []  # não é resposta


def test_pronto_errado_devolve_so_as_colunas_erradas(tela):
    _abrir(tela)
    certo = logica.algarismos(tela.rodada.numero)
    montagem = dict(certo, unidade=certo["unidade"] - 1)  # uma unidade a menos
    _montar(tela, montagem)
    tela.barramento.escolher.emit("cartao-pronto")
    tentativa = tela.ctx.registro.listar_tentativas()[-1]
    assert tentativa["tipo_erro"] == "contou_pecas_errado"
    assert tela.rodada.na_mesa["unidade"] == 0  # a coluna errada voltou
    assert tela.rodada.na_mesa["centena"] == certo["centena"]  # as certas ficaram
    _levar(tela, "unidade", vezes=certo["unidade"])
    tela.barramento.escolher.emit("cartao-pronto")
    assert tela.momento == FIM


def test_pista_2_realca_e_pista_3_monta_o_modelo(tela):
    _abrir(tela)
    tela.barramento.escolher.emit("cartao-pronto")  # mesa vazia
    tela.barramento.escolher.emit("cartao-pronto")
    assert tela.cena.caixas[id_coluna("centena")].realcado
    tela.barramento.escolher.emit("cartao-pronto")
    assert tela.rodada.total == tela.rodada.numero  # o modelo montou
    assert tela.ctx.registro.listar_tentativas()[-1]["precisou_modelo"]


def test_mao_simulada_leva_uma_peca(tela):
    _abrir(tela, nivel=1)
    mao_simulada.reproduzir(tela.entrada_mao, tela.cena, passos=[
        {"ir_para": _topo(tela, "dezena"), "ms": 500}, {"esperar": 300},
        {"pinca": True, "ms": 300}, {"ir_para": id_coluna("dezena"), "ms": 500},
        {"esperar": 300}, {"pinca": False, "ms": 300},
    ])
    assert tela.rodada.na_mesa["dezena"] == 1


def test_agente_monta_o_numero(capsys, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    agente.executar("dourado", [], entrada=[json.dumps({"acao": "estado"})])
    estado = json.loads(capsys.readouterr().out.splitlines()[-1])["estado"]
    certo = logica.algarismos(estado["numero"])
    pedidos = [{"acao": "proximo"}]
    for ordem in estado["na_mesa"]:
        for k in range(certo[ordem]):
            pedidos += [{"acao": "pegar", "id": f"{ordem}-{8 - k}"},
                        {"acao": "soltar", "alvo": id_coluna(ordem)}]
    pedidos.append({"acao": "escolher", "id": "cartao-pronto"})
    agente.executar("dourado", [], entrada=[json.dumps(p) for p in pedidos])
    respostas = [json.loads(linha) for linha in capsys.readouterr().out.splitlines()]
    assert respostas[-1]["estado"]["concluida"] is True
