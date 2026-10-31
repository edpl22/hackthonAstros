"""Treino de arrastar: lógica pura e a mesma atividade completada por cada entrada."""

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from app.atividades.base import Contexto
from app.atividades.treino import logica
from app.atividades.treino.tela import TelaTreino
from app.entrada import mao_simulada
from app.entrada.camera import CameraNula
from app.nucleo.audio import ServicoAudio
from app.nucleo.perfis import PERFIS, combinar
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao

# --- lógica pura -----------------------------------------------------------


def test_rodada_respeita_max_itens():
    assert logica.nova_rodada(4, 1).letras == ["A", "B", "C", "D"]
    assert logica.nova_rodada(3, 1).letras == ["A", "B", "C"]
    assert logica.nova_rodada(9, 1).letras == ["A", "B", "C", "D"]
    assert len(logica.nova_rodada(1, 1).letras) == 2


def test_rodadas_percorrem_o_alfabeto_inteiro():
    vistas = [logica.nova_rodada(4, 1, bloco).letras for bloco in range(8)]
    assert vistas[:2] == [["A", "B", "C", "D"], ["E", "F", "G", "H"]]
    assert vistas[6] == ["W", "X", "Y", "Z"]  # o último bloco sempre tem as n letras
    assert vistas[7] == ["A", "B", "C", "D"]  # depois do Z volta ao começo
    assert set().union(*vistas[:7]) == set(logica.ALFABETO)


@pytest.mark.parametrize("n", [2, 3, 4])
def test_todo_bloco_tem_n_letras_e_todas_aparecem(n):
    blocos = [logica.letras_do_bloco(b, n) for b in range(-(-26 // n))]
    assert all(len(b) == n for b in blocos)
    assert set().union(*blocos) == set(logica.ALFABETO)


@pytest.mark.parametrize("semente", range(20))
def test_pecas_nunca_ficam_todas_em_cima_das_caixas(semente):
    rodada = logica.nova_rodada(3, semente)
    assert rodada.ordem_pecas != [0, 1, 2]
    assert sorted(rodada.ordem_pecas) == [0, 1, 2]


def test_rodada_mesma_semente_mesmo_resultado():
    assert logica.nova_rodada(4, 7).ordem_pecas == logica.nova_rodada(4, 7).ordem_pecas


def test_proxima_letra_e_conclusao():
    rodada = logica.nova_rodada(2, 0)
    assert rodada.proxima_letra() == "A"
    rodada.colocadas.add("A")
    assert rodada.proxima_letra() == "B" and not rodada.concluida
    rodada.colocadas.add("B")
    assert rodada.proxima_letra() is None and rodada.concluida


def test_ids_estaveis():
    assert logica.id_peca("B", 1) == "peca-b-1"
    assert logica.id_caixa(0) == "caixa-1"
    assert logica.confere("A", "A") and not logica.confere("B", "A")


# --- a mesma atividade por mouse, clique-clique, teclado, varredura e mão ----


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), CameraNula)
    t = TelaTreino(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _iniciar(tela, perfil, **opcoes):
    """Abre a atividade e passa do momento "O que vamos fazer" para a atividade."""
    tela.iniciar(perfil, **opcoes)
    tela.comecar()


def _mouse(cena, tipo, ponto, botoes):
    local = QPointF(cena.mapFromScene(QPointF(*ponto)))
    botao = Qt.NoButton if tipo == QEvent.MouseMove else Qt.LeftButton
    QApplication.sendEvent(
        cena.viewport(),
        QMouseEvent(tipo, local, cena.viewport().mapToGlobal(local), botao, botoes, Qt.NoModifier),
    )


def _arrastar(tela, peca, caixa):
    cena = tela.cena
    _mouse(cena, QEvent.MouseButtonPress, cena.centro(peca), Qt.LeftButton)
    _mouse(cena, QEvent.MouseMove, cena.centro(caixa), Qt.LeftButton)
    _mouse(cena, QEvent.MouseButtonRelease, cena.centro(caixa), Qt.NoButton)


def _clique_clique(tela, peca, caixa):
    for ponto in (tela.cena.centro(peca), tela.cena.centro(caixa)):
        _mouse(tela.cena, QEvent.MouseButtonPress, ponto, Qt.LeftButton)
        _mouse(tela.cena, QEvent.MouseButtonRelease, ponto, Qt.NoButton)


def _por_foco(tela, peca, caixa, avancar, selecionar):
    for alvo in (peca, caixa):
        for _ in range(10):
            if tela.entrada_teclado.foco.atual == alvo:
                break
            avancar()
        assert tela.entrada_teclado.foco.atual == alvo
        selecionar()


def _teclado(qtbot):
    def jogar(tela, peca, caixa):
        _por_foco(
            tela, peca, caixa,
            lambda: qtbot.keyClick(tela.cena, Qt.Key_Tab),
            lambda: qtbot.keyClick(tela.cena, Qt.Key_Space),
        )
    return jogar


def _varredura(qtbot):
    def jogar(tela, peca, caixa):
        _por_foco(
            tela, peca, caixa,
            tela.entrada_teclado.avancar,
            lambda: qtbot.keyClick(tela.cena, Qt.Key_X),  # qualquer tecla seleciona
        )
    return jogar


def _mao(tela, peca, caixa):
    mao_simulada.reproduzir(
        tela.entrada_mao, tela.cena,
        passos=[
            {"ir_para": peca, "ms": 600}, {"esperar": 300}, {"pinca": True, "ms": 300},
            {"ir_para": caixa, "ms": 600}, {"esperar": 300}, {"pinca": False, "ms": 300},
        ],
    )


def _completar(tela, jogar):
    letras = tela.rodada.letras
    jogar(tela, logica.id_peca(letras[1], 1), logica.id_caixa(0))  # erro proposital
    assert tela.ultimo_anuncio.startswith("A letra B voltou")
    assert not tela.cena.pecas[logica.id_peca(letras[1], 1)].encaixada
    for i, letra in enumerate(letras):
        jogar(tela, logica.id_peca(letra, i), logica.id_caixa(i))
    assert tela.rodada.concluida, tela.ultimo_anuncio
    assert tela.estado()["concluida"]


@pytest.mark.parametrize("modo", ["arrastar", "clique-clique", "teclado", "varredura", "mao"])
def test_completa_o_treino_com_cada_entrada(tela, qtbot, modo):
    jogadas = {
        "arrastar": _arrastar,
        "clique-clique": _clique_clique,
        "teclado": _teclado(qtbot),
        "varredura": _varredura(qtbot),
        "mao": _mao,
    }
    _iniciar(tela, PERFIS["padrao"], semente=3, varredura=modo == "varredura")
    _completar(tela, jogadas[modo])
    esperado = {"mao": "camera", "varredura": "varredura", "teclado": "teclado"}.get(modo, "mouse")
    assert tela.estado()["modo_entrada"] == esperado


def test_mao_com_permanencia_perfil_motor(tela):
    perfil = combinar(["motor"])
    _iniciar(tela, perfil, semente=3)
    letras = tela.rodada.letras
    for i, letra in enumerate(letras):
        # Sem pinça: a criança só para a mão sobre a peça e depois sobre a caixa.
        mao_simulada.reproduzir(
            tela.entrada_mao, tela.cena,
            passos=[
                {"ir_para": logica.id_peca(letra, i), "ms": 500}, {"esperar": 2000},
                {"ir_para": logica.id_caixa(i), "ms": 500}, {"esperar": 2000},
            ],
        )
    assert tela.rodada.concluida, tela.ultimo_anuncio


def test_perfil_muda_a_quantidade_de_pecas(tela):
    _iniciar(tela, PERFIS["tea"], semente=1)
    assert len(tela.cena.pecas) == 3
    _iniciar(tela, PERFIS["padrao"], semente=1)
    assert len(tela.cena.pecas) == 4


def test_estado_tem_ids_estaveis(tela):
    _iniciar(tela, PERFIS["padrao"], semente=1)
    estado = tela.estado()
    assert [i["id"] for i in estado["itens"]] == ["peca-a-0", "peca-b-1", "peca-c-2", "peca-d-3"]
    assert [a["id"] for a in estado["alvos"]] == ["caixa-1", "caixa-2", "caixa-3", "caixa-4"]
    assert estado["instrucao"] == "Pegue a letra A. Coloque na caixa da letra A."


def test_proxima_rodada_avanca_no_alfabeto(tela):
    _iniciar(tela, PERFIS["padrao"], semente=1)
    _completar(tela, _arrastar)
    tela.proximo()
    assert tela.rodada.letras == ["E", "F", "G", "H"]
    assert tela.estado()["instrucao"] == "Pegue a letra E. Coloque na caixa da letra E."
    _iniciar(tela, PERFIS["padrao"], semente=1)  # abrir de novo recomeça no A
    assert tela.rodada.letras == ["A", "B", "C", "D"]


def test_soltar_fora_devolve_a_peca(tela):
    _iniciar(tela, PERFIS["padrao"], semente=1)
    cena = tela.cena
    origem = cena.centro("peca-a-0")
    _mouse(cena, QEvent.MouseButtonPress, origem, Qt.LeftButton)
    _mouse(cena, QEvent.MouseMove, (640, 40), Qt.LeftButton)
    _mouse(cena, QEvent.MouseButtonRelease, (640, 40), Qt.NoButton)
    assert cena.centro("peca-a-0") == origem
    assert tela.ultimo_anuncio == "A letra A voltou para o lugar."
    assert tela.ctx.registro.listar_tentativas() == []  # cair fora não conta como resposta


def test_esc_pausa(tela, qtbot):
    _iniciar(tela, PERFIS["padrao"], semente=1)
    with qtbot.waitSignal(tela.barramento.pausar):
        qtbot.keyClick(tela.cena, Qt.Key_Escape)
    assert tela.pausada
