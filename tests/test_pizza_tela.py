"""Pizza de Frações: montar, somar, desafio, barra de chocolate, pista e agente."""

import json

import pytest
from PySide6.QtCore import Qt

from app.atividades.base import FIM, Contexto
from app.atividades.pizza import logica
from app.atividades.pizza.tela import TelaPizza
from app.entrada.camera import CameraNula
from app.headless import agente
from app.nucleo import erros
from app.nucleo.audio import ServicoAudio
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), CameraNula)
    t = TelaPizza(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _abrir(tela, nivel, semente=3, perfis=(), **opcoes):
    tela.ctx.sessao.definir(None, list(perfis))
    tela.iniciar(tela.ctx.sessao.perfil, semente=semente, nivel=nivel, **opcoes)
    tela.comecar()


def _tocar(tela, peca_id):
    tela.barramento.apontar.emit(*tela.cena.centro(peca_id))
    tela.barramento.pegar.emit()


def test_montar_tocando_nas_fatias(tela):
    _abrir(tela, logica.MONTAR)
    n, corte = tela.rodada.certo
    for i in range(n):
        _tocar(tela, f"fatia-a-{i}")
    assert tela.fracao.text() == f"{n}/{corte}"
    assert tela.estado()["fatias_escolhidas"] == n
    fatia = tela.cena.pecas["fatia-a-0"]
    assert fatia.escolhida and not tela.barramento.segurando
    _tocar(tela, "cartao-pronto")
    assert tela.momento == FIM


def test_tocar_de_novo_devolve_a_fatia(tela):
    _abrir(tela, logica.MONTAR)
    _tocar(tela, "fatia-a-0")
    _tocar(tela, "fatia-a-0")
    assert tela.estado()["fatias_escolhidas"] == 0


def test_montar_contou_errado(tela):
    _abrir(tela, logica.MONTAR)
    tela.barramento.escolher.emit("cartao-pronto")  # nenhuma fatia
    assert tela.ctx.registro.listar_tentativas()[-1]["tipo_erro"] == "contou_fatias_errado"


def test_somar_classifica_e_mostra_a_pista_sobreposta(tela):
    _abrir(tela, logica.SOMAR)
    r = tela.rodada
    (n1, d), (n2, _) = r.parcelas
    errado = f"cartao-{n1 + n2}-{2 * d}"
    tela.barramento.escolher.emit(errado)
    assert tela.ctx.registro.listar_tentativas()[-1]["tipo_erro"] == "somou_denominadores"
    tela.barramento.escolher.emit(errado)
    assert tela.dica.text() == "As fatias continuam do mesmo tamanho."
    assert tela.fatias["b"][0].centro == tela.fatias["a"][0].centro  # pizzas sobrepostas
    tela.barramento.escolher.emit(f"cartao-{n1 + n2}-{d}")
    assert tela.momento == FIM


def test_operar_tem_tres_pratos_com_soma_e_subtracao(tela):
    _abrir(tela, logica.OPERAR)
    r = tela.rodada
    assert len(r.parcelas) == 3 and "-" in r.sinais
    assert set(tela.fatias) == {"a", "b", "c"}
    estado = tela.estado()
    assert estado["modo"] == "operar" and estado["sinais"] == r.sinais
    assert "−" in tela.instrucao.text()  # sinal de menos de verdade na tela
    trocada = erros.resultado_fracao(r.parcelas, ["+"] * len(r.sinais))
    tela.barramento.escolher.emit(f"cartao-{trocada[0]}-{trocada[1]}")
    tentativa = tela.ctx.registro.listar_tentativas()[-1]
    assert tentativa["tipo_erro"] == "operacao_trocada"
    assert tentativa["habilidade"] == "somar e subtrair frações de mesmo denominador"
    tela.barramento.escolher.emit(f"cartao-{trocada[0]}-{trocada[1]}")  # pista 2
    assert tela.dica.text() == "As fatias continuam do mesmo tamanho."
    tela.barramento.escolher.emit(f"cartao-{r.certo[0]}-{r.certo[1]}")
    assert tela.momento == FIM


def test_operar_com_perfil_de_menos_itens_usa_dois_pratos(tela):
    _abrir(tela, logica.OPERAR, perfis=["tea"])
    assert len(tela.rodada.parcelas) == 2 and tela.rodada.sinais == ["-"]


def test_desafio_mostra_numero_misto(tela):
    _abrir(tela, logica.DESAFIO)
    r = tela.rodada
    tela.barramento.escolher.emit(f"cartao-{r.certo[0]}-{r.certo[1]}")
    assert logica.misto(r.certo) in tela.ultimo_anuncio


def test_barra_de_chocolate(tela):
    _abrir(tela, logica.MONTAR, forma="barra")
    assert tela.estado()["forma"] == "barra"
    _tocar(tela, "fatia-a-0")
    assert tela.estado()["fatias_escolhidas"] == 1


def test_fatias_por_teclado(tela, qtbot):
    _abrir(tela, logica.MONTAR)
    qtbot.keyClick(tela.cena, Qt.Key_Tab)
    qtbot.keyClick(tela.cena, Qt.Key_Space)
    assert tela.estado()["fatias_escolhidas"] == 1


def test_agente_monta_a_fracao(capsys, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    agente.executar("pizza", [], entrada=['{"acao": "proximo"}'])
    estado = json.loads(capsys.readouterr().out.splitlines()[-1])["estado"]
    n = int(estado["instrucao"].split()[1])
    pedidos = [{"acao": "proximo"}]
    pedidos += [{"acao": "escolher", "id": f"fatia-a-{i}"} for i in range(n)]
    pedidos.append({"acao": "escolher", "id": "cartao-pronto"})
    agente.executar("pizza", [], entrada=[json.dumps(p) for p in pedidos])
    respostas = [json.loads(linha) for linha in capsys.readouterr().out.splitlines()]
    assert respostas[-1]["estado"]["concluida"] is True
