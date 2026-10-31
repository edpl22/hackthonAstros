"""Tabuada Protetora: lógica pura, gesto de arminha e a tela por mouse, teclado e mão."""

import json
import random

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from app.atividades.base import FIM, Contexto
from app.atividades.tabuada import logica
from app.atividades.tabuada.tela import TelaTabuada
from app.entrada import mao_simulada
from app.entrada.camera import CameraNula
from app.entrada.mao import DetectorDisparo, eh_arminha
from app.headless import agente
from app.nucleo import erros
from app.nucleo.audio import ServicoAudio
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao

# --- lógica pura ------------------------------------------------------------------------


def test_conta_tem_um_monstro_certo_e_distratores_comuns():
    partida = logica.nova_partida(1, 4, semente=3)
    conta = partida.conta
    valores = [m.valor for m in conta.monstros]
    assert len(valores) == 4 and len(set(valores)) == 4
    assert valores.count(conta.certo) == 1
    assert conta.a in logica.FATORES[1] and conta.b in logica.SEGUNDO_FATOR
    assert logica.distratores(3, 4, 2, random.Random(0)) == [7, 15]  # 3+4 e 3x5


def test_pontos_sobem_no_certo_e_descem_no_errado():
    partida = logica.nova_partida(1, 3, semente=1)
    certo = partida.conta.certo
    assert logica.acertar(partida, certo) == 1
    assert logica.acertar(partida, certo + 1) == 0
    assert logica.acertar(partida, certo + 1) == -1


def test_partida_dura_um_minuto():
    partida = logica.nova_partida(1, 3, semente=1)
    assert logica.relogio(partida.restante_s) == "1:00"
    for _ in range(59):
        assert not logica.passar_segundo(partida)
    assert logica.relogio(partida.restante_s) == "0:01"
    assert logica.passar_segundo(partida) and partida.acabou


def test_contas_nao_repetem_na_partida():
    partida = logica.nova_partida(1, 3, semente=2)
    contas = {partida.conta.id}
    for _ in range(20):
        contas.add(logica.nova_conta(partida).id)
    assert len(contas) == 21


def test_classificar_tabuada():
    assert erros.classificar_tabuada(12, 3, 4) is None
    assert erros.classificar_tabuada(7, 3, 4) == "somou_em_vez_de_multiplicar"
    assert erros.classificar_tabuada(15, 3, 4) == "vizinho_na_tabuada"
    assert erros.classificar_tabuada(40, 3, 4) == "outro"
    for tipo in ("somou_em_vez_de_multiplicar", "vizinho_na_tabuada"):
        assert erros.recomendacao(tipo)


# --- gesto de arminha -------------------------------------------------------------------


def test_arminha_reconhecida_e_mao_apontando_nao():
    assert eh_arminha(mao_simulada.pontos_sinteticos(0.5, 0.5, False, arminha=True))
    assert not eh_arminha(mao_simulada.pontos_sinteticos(0.5, 0.5, False))


def test_disparo_so_com_coice_rapido_para_cima():
    d = DetectorDisparo()
    assert d.atualizar(0.0, 0.60, (100, 300), True) is None
    assert d.atualizar(0.1, 0.55, (100, 280), True) is None  # subiu pouco
    assert d.atualizar(0.2, 0.45, (100, 240), True) == (100, 300)  # coice: mira de antes
    assert d.atualizar(0.3, 0.30, (100, 200), True) is None  # espera o intervalo


def test_subida_lenta_ou_sem_arminha_nao_dispara():
    d = DetectorDisparo()
    for i in range(20):  # sobe 0,3 em 2 s: devagar demais
        assert d.atualizar(i * 0.1, 0.6 - i * 0.015, (0, 0), True) is None
    d = DetectorDisparo()
    assert d.atualizar(0.0, 0.6, (0, 0), False) is None
    assert d.atualizar(0.1, 0.3, (0, 0), False) is None


# --- tela -------------------------------------------------------------------------------


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), CameraNula)
    t = TelaTabuada(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _abrir(tela, perfis=(), semente=5):
    tela.ctx.sessao.definir(None, list(perfis))
    tela.iniciar(tela.ctx.sessao.perfil, semente=semente)
    tela.comecar()


def _id(tela, certo: bool) -> str:
    conta = tela.partida.conta
    return next(m.id for m in conta.monstros if (m.valor == conta.certo) == certo)


def _clicar(tela, id_monstro):
    cena = tela.cena
    local = QPointF(cena.mapFromScene(QPointF(*cena.centro(id_monstro))))
    for tipo, botoes in ((QEvent.MouseButtonPress, Qt.LeftButton),
                         (QEvent.MouseButtonRelease, Qt.NoButton)):
        QApplication.sendEvent(cena.viewport(), QMouseEvent(
            tipo, local, cena.viewport().mapToGlobal(local), Qt.LeftButton, botoes, Qt.NoModifier
        ))


def _disparar_com_a_mao(tela, id_monstro):
    mao_simulada.reproduzir(tela.entrada_mao, tela.cena, passos=[
        {"arminha": True}, {"ir_para": id_monstro, "ms": 500}, {"esperar": 300},
        {"disparar": True}, {"esperar": 300},
    ])


def test_tela_mostra_conta_relogio_pontos_e_monstros(tela):
    _abrir(tela)
    estado = tela.estado()
    assert estado["conta"] == tela.partida.conta.texto
    assert estado["pontos"] == 0 and estado["tempo_restante"] == 60
    monstros = [i for i in estado["itens"] if i["tipo"] == "monstro"]
    assert len(monstros) == 4
    assert tela.texto_relogio.text() == "1:00"
    assert tela.gesto_mao == "arminha" and tela.entrada_mao.disparo is not None


def test_mouse_acerta_o_certo_e_ganha_ponto(tela):
    _abrir(tela)
    conta_antes = tela.partida.conta.id
    _clicar(tela, _id(tela, certo=True))
    assert tela.partida.pontos == 1
    assert tela.partida.conta.id != conta_antes  # vem a próxima conta
    tentativa = tela.ctx.registro.listar_tentativas()[-1]
    assert tentativa["correta"] and tentativa["item"] == conta_antes
    assert tentativa["modo_entrada"] == "mouse"


def test_errado_perde_ponto_e_o_monstro_some(tela):
    _abrir(tela)
    errado = _id(tela, certo=False)
    _clicar(tela, errado)
    assert tela.partida.pontos == -1
    assert errado not in tela.cena.pecas
    assert tela.ctx.registro.listar_tentativas()[-1]["tipo_erro"] is not None
    assert tela.texto_pontos.text() == "Pontos: -1"


def test_tiro_no_vazio_nao_muda_nada(tela):
    _abrir(tela)
    tela.barramento.apontar.emit(5, 5)
    tela.barramento.pegar.emit()
    assert tela.partida.pontos == 0
    assert tela.ctx.registro.listar_tentativas() == []


def test_mao_dispara_com_a_arminha(tela):
    _abrir(tela)
    _disparar_com_a_mao(tela, _id(tela, certo=True))
    assert tela.partida.pontos == 1
    assert tela.ctx.registro.listar_tentativas()[-1]["modo_entrada"] == "camera"


def test_pinca_nao_pega_nada_na_tabuada(tela):
    _abrir(tela)
    mao_simulada.reproduzir(tela.entrada_mao, tela.cena, passos=[
        {"ir_para": _id(tela, certo=True), "ms": 500}, {"esperar": 300},
        {"pinca": True, "ms": 300}, {"pinca": False, "ms": 300},
    ])
    assert tela.partida.pontos == 0
    assert tela.ctx.registro.listar_tentativas() == []


def test_teclado_tambem_joga(tela, qtbot):
    _abrir(tela)
    alvo = _id(tela, certo=True)
    for _ in range(10):
        if tela.entrada_teclado.foco.atual == alvo:
            break
        qtbot.keyClick(tela.cena, Qt.Key_Tab)
    qtbot.keyClick(tela.cena, Qt.Key_Return)
    assert tela.partida.pontos == 1


def test_tres_erros_mostram_o_modelo_e_trocam_a_conta(tela):
    _abrir(tela, perfis=["padrao"])
    conta = tela.partida.conta.id
    for _ in range(3):
        _clicar(tela, _id(tela, certo=False))
    assert tela.partida.conta.id != conta
    assert "=" in tela.ultimo_anuncio


def test_tempo_acaba_e_mostra_os_pontos(tela):
    _abrir(tela)
    _clicar(tela, _id(tela, certo=True))
    tela.passar_tempo(59)
    assert tela.momento != FIM and tela.texto_relogio.text() == "0:01"
    tela.passar_tempo(1)
    assert tela.momento == FIM
    assert "1 pontos" in tela.texto_fim_detalhe.text()
    _clicar_depois = tela.partida.pontos
    tela.passar_tempo(5)  # depois do fim o relógio não anda
    assert tela.partida.pontos == _clicar_depois and tela.partida.restante_s == 0


def test_pausa_congela_o_relogio(tela):
    _abrir(tela)
    tela.pausar()
    tela.passar_tempo(10)
    assert tela.partida.restante_s == 60
    tela.continuar()
    tela.passar_tempo(10)
    assert tela.partida.restante_s == 50


def test_matematica_sem_voz(tela):
    _abrir(tela)
    _clicar(tela, _id(tela, certo=True))
    _clicar(tela, _id(tela, certo=False))
    assert tela.ctx.audio.log == []


def test_agente_joga_a_tabuada(capsys, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    linhas = [json.dumps(p) for p in ({"acao": "proximo"}, {"acao": "estado"})]
    agente.executar("tabuada", [], entrada=linhas)
    estado = json.loads(capsys.readouterr().out.splitlines()[-1])["estado"]
    a, b = (int(v) for v in estado["conta"].split(" × "))
    certo = next(i["id"] for i in estado["itens"] if i["rotulo"] == str(a * b))
    pedidos = [{"acao": "proximo"}, {"acao": "escolher", "id": certo}]
    agente.executar("tabuada", [], entrada=[json.dumps(p) for p in pedidos])
    resposta = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert resposta["ok"] and resposta["estado"]["pontos"] == 1
