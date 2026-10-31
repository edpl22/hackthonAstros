"""Ímã das Sílabas: BOLA completada por cada entrada, erros, níveis, perfis e agente."""

import json

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from app.atividades.base import FIM, Contexto
from app.atividades.silabas.tela import TelaSilabas
from app.entrada import mao_simulada
from app.entrada.camera import CameraNula
from app.headless import agente
from app.nucleo.audio import ServicoAudio
from app.nucleo.perfis import combinar
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), CameraNula)
    t = TelaSilabas(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _abrir(tela, perfis=(), palavra="bola", nivel=None, varredura=False):
    tela.ctx.sessao.definir(None, list(perfis))
    tela.iniciar(tela.ctx.sessao.perfil, semente=3, varredura=varredura, nivel=nivel,
                 palavra=palavra)
    tela.comecar()


def _bolha(tela, silaba):
    return next(b.id for b in tela.rodada.bolhas if b.silaba == silaba)


def _mouse(cena, tipo, ponto, botoes):
    local = QPointF(cena.mapFromScene(QPointF(*ponto)))
    botao = Qt.NoButton if tipo == QEvent.MouseMove else Qt.LeftButton
    QApplication.sendEvent(
        cena.viewport(),
        QMouseEvent(tipo, local, cena.viewport().mapToGlobal(local), botao, botoes, Qt.NoModifier),
    )


# --- as entradas ---------------------------------------------------------------------


def _arrastar(tela, qtbot, origem, destino):
    cena = tela.cena
    _mouse(cena, QEvent.MouseButtonPress, cena.centro(origem), Qt.LeftButton)
    _mouse(cena, QEvent.MouseMove, cena.centro(destino), Qt.LeftButton)
    _mouse(cena, QEvent.MouseButtonRelease, cena.centro(destino), Qt.NoButton)


def _clique_clique(tela, qtbot, origem, destino):
    for alvo in (origem, destino):
        _mouse(tela.cena, QEvent.MouseButtonPress, tela.cena.centro(alvo), Qt.LeftButton)
        _mouse(tela.cena, QEvent.MouseButtonRelease, tela.cena.centro(alvo), Qt.NoButton)


def _por_foco(tela, origem, destino, avancar, selecionar):
    for alvo in (origem, destino):
        for _ in range(10):
            if tela.entrada_teclado.foco.atual == alvo:
                break
            avancar()
        assert tela.entrada_teclado.foco.atual == alvo
        selecionar()


def _teclado(tela, qtbot, origem, destino):
    _por_foco(tela, origem, destino,
              lambda: qtbot.keyClick(tela.cena, Qt.Key_Right),
              lambda: qtbot.keyClick(tela.cena, Qt.Key_Return))


def _varredura(tela, qtbot, origem, destino):
    _por_foco(tela, origem, destino, tela.entrada_teclado.avancar,
              lambda: qtbot.keyClick(tela.cena, Qt.Key_Space))


def _mao(tela, qtbot, origem, destino):
    mao_simulada.reproduzir(tela.entrada_mao, tela.cena, passos=[
        {"ir_para": origem, "ms": 600}, {"esperar": 300}, {"pinca": True, "ms": 300},
        {"ir_para": destino, "ms": 600}, {"esperar": 300}, {"pinca": False, "ms": 300},
    ])


@pytest.mark.parametrize(
    "jogar", [_arrastar, _clique_clique, _teclado, _varredura, _mao],
    ids=["arrastar", "clique-clique", "teclado", "varredura", "mao-simulada"],
)
def test_completa_bola_com_cada_entrada(tela, qtbot, jogar):
    _abrir(tela, varredura=jogar is _varredura)
    assert tela.rodada.palavra.texto == "BOLA"
    jogar(tela, qtbot, _bolha(tela, "LA"), "caixa-1")  # erro proposital: ordem trocada
    assert tela.estado()["pista_nivel"] == 1
    jogar(tela, qtbot, _bolha(tela, "BO"), "caixa-1")
    jogar(tela, qtbot, _bolha(tela, "LA"), "caixa-2")
    assert tela.momento == FIM
    tentativas = tela.ctx.registro.listar_tentativas()
    assert [(t["item"], t["resposta"], t["tipo_erro"]) for t in tentativas] == [
        ("bola-1", "LA", "ordem_trocada"), ("bola-1", "BO", None), ("bola-2", "LA", None),
    ]


# --- regras da atividade -------------------------------------------------------------


def _jogar_bus(tela, origem, destino):
    b = tela.barramento
    b.apontar.emit(*tela.cena.centro(origem))
    b.pegar.emit()
    b.apontar.emit(*tela.cena.centro(destino))
    b.soltar.emit()


def test_tela_tem_figura_caixas_e_bolhas(tela):
    _abrir(tela)
    estado = tela.estado()
    assert estado["palavra"] == "BOLA" and estado["figura"] == "figuras/palavras/bola.svg"
    assert tela.cena.figura.renderer().isValid()
    assert [a["id"] for a in estado["alvos"]] == ["caixa-1", "caixa-2"]
    assert [a["rotulo"] for a in estado["alvos"]] == ["primeira caixa", "segunda caixa"]
    assert len(estado["itens"]) == 4 and all(i["tipo"] == "bolha" for i in estado["itens"])
    assert estado["instrucao"] == "Pegue a bolha BO. Coloque na primeira caixa."


def test_pegar_toca_a_silaba_e_palavra_pronta_toca_a_palavra(tela):
    _abrir(tela)
    audio = tela.ctx.audio
    tela.barramento.apontar.emit(*tela.cena.centro(_bolha(tela, "BO")))
    tela.barramento.pegar.emit()
    assert audio.log[-1] == f"toca {audio.arquivo_de('bó')}"  # BO de BOLA soa aberto
    tela.barramento.apontar.emit(*tela.cena.centro("caixa-1"))
    tela.barramento.soltar.emit()
    _jogar_bus(tela, _bolha(tela, "LA"), "caixa-2")
    # Só a sílaba pega e a palavra pronta têm voz; instruções e retornos ficam na legenda.
    assert audio.log == [f"toca {audio.arquivo_de(fala)}" for fala in ("bó", "la", "bola")]
    assert all(audio.arquivo_de(fala) for fala in ("bó", "la", "bola"))


def test_distratora_classificada(tela):
    _abrir(tela)
    distratora = next(b for b in tela.rodada.bolhas if b.posicao is None)
    _jogar_bus(tela, distratora.id, "caixa-1")
    assert tela.ctx.registro.listar_tentativas()[-1]["tipo_erro"] in {
        "silaba_de_outra_palavra", "par_surdo_sonoro",
    }


def test_tres_erros_mostram_o_modelo(tela):
    _abrir(tela)
    for _ in range(3):
        _jogar_bus(tela, _bolha(tela, "LA"), "caixa-1")
    assert tela.rodada.colocadas == {0: "BO"}
    assert tela.ctx.registro.listar_tentativas()[-1]["precisou_modelo"] is True


def test_nivel_3_minusculas_e_par_surdo_sonoro(tela):
    _abrir(tela, palavra="prato", nivel=3)
    rotulos = [i["rotulo"] for i in tela.estado()["itens"]]
    assert "pra" in rotulos and "to" in rotulos
    assert {"bra", "do"} & set(rotulos)  # distratora do par surdo/sonoro
    assert tela.estado()["instrucao"] == "Pegue a bolha pra. Coloque na primeira caixa."


def test_nivel_4_silaba_tonica_por_escolha(tela):
    _abrir(tela, palavra="janela", nivel=4)
    estado = tela.estado()
    assert estado["alvos"] == [] and len(estado["itens"]) == 3
    assert estado["instrucao"] == "Ouça a palavra JANELA. Qual bolha é a mais forte?"
    tela.barramento.escolher.emit(_bolha(tela, "JA"))
    assert tela.ctx.registro.listar_tentativas()[-1]["tipo_erro"] == "tonica_errada"
    assert tela.momento != FIM
    tela.barramento.escolher.emit(_bolha(tela, "NE"))
    assert tela.momento == FIM
    ultima = tela.ctx.registro.listar_tentativas()[-1]
    assert ultima["habilidade"] == "achar a sílaba tônica" and ultima["item"] == "janela-tonica"


def test_nivel_4_pegar_com_a_mao_tambem_escolhe(tela):
    _abrir(tela, palavra="bola", nivel=4)
    tela.barramento.apontar.emit(*tela.cena.centro(_bolha(tela, "BO")))
    tela.barramento.pegar.emit()
    assert tela.momento == FIM and not tela.barramento.segurando


def test_quatro_acertos_levam_ao_proximo_nivel(tela):
    _abrir(tela, palavra="bola")
    _jogar_bus(tela, _bolha(tela, "BO"), "caixa-1")
    _jogar_bus(tela, _bolha(tela, "LA"), "caixa-2")
    tela.proximo()
    for pos in range(len(tela.rodada.palavra.silabas)):
        _jogar_bus(tela, tela.rodada.bolha_da_posicao(pos).id, f"caixa-{pos + 1}")
    assert tela.oferece_desafio
    tela.responder_desafio(True)
    assert tela.nivel.nivel == 2 and tela.rodada.palavra.nivel == 2


def test_dislexia_alterna_cor_e_sublinhado(tela):
    _abrir(tela, ["dislexia"], palavra="sapato")
    alternadas = {p.rotulo for p in tela.cena.pecas.values() if p.alternada}
    assert alternadas == {"PA"}  # 2ª sílaba da palavra: cor + sublinhado


def test_tea_tres_bolhas_paradas(tela):
    _abrir(tela, ["tea"])
    assert len(tela.cena.pecas) == 3
    assert not tela.cena._timer_flutuar.isActive()


def test_velocidade_faz_as_bolhas_flutuarem(tela, monkeypatch):
    monkeypatch.delenv("ATLAS_SEM_ANIMACAO")
    _abrir(tela)
    assert tela.cena._timer_flutuar.isActive()
    bolha = tela.cena.pecas[_bolha(tela, "BO")]
    antes = bolha.pos()
    for _ in range(10):
        tela.cena._passo_flutuar()
    assert bolha.pos() != antes
    assert combinar([]).velocidade * 40 == tela.cena._velocidade_px_s


# --- agente ---------------------------------------------------------------------------


def test_agente_completa_bola(capsys, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")

    def conversar(pedidos, **opcoes):
        linhas = [json.dumps(p) for p in pedidos] + [json.dumps({"acao": "sair"})]
        agente.executar("silabas", [], entrada=linhas, **opcoes)
        return [json.loads(linha) for linha in capsys.readouterr().out.splitlines()]

    estado = conversar([{"acao": "estado"}])[1]["estado"]
    assert estado["palavra"] == "BOLA"  # o agente começa sempre em BOLA
    ids = {i["rotulo"]: i["id"] for i in estado["itens"]}
    respostas = conversar([
        {"acao": "proximo"},
        {"acao": "pegar", "id": ids["LA"]}, {"acao": "soltar", "alvo": "caixa-1"},
        {"acao": "pegar", "id": ids["BO"]}, {"acao": "soltar", "alvo": "caixa-1"},
        {"acao": "pegar", "id": ids["LA"]}, {"acao": "soltar", "alvo": "caixa-2"},
        {"acao": "estado"},
    ])
    assert all(r.get("ok", True) for r in respostas)
    assert respostas[3]["estado"]["pista_nivel"] == 1  # LA na 1ª caixa: pista
    assert respostas[5]["anuncio"] == "Bolha BO colocada na primeira caixa."
    assert respostas[-2]["estado"]["concluida"] is True


def test_agente_outra_palavra_e_palavra_inexistente(capsys, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    agente.executar("silabas", [], entrada=['{"acao": "estado"}'], palavra="janela")
    assert json.loads(capsys.readouterr().out.splitlines()[1])["estado"]["palavra"] == "JANELA"
    assert agente.executar("silabas", [], entrada=[], palavra="xyz") == 1
    assert "palavra inexistente" in capsys.readouterr().out
