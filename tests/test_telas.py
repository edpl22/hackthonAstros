import pytest
from PySide6.QtCore import Qt

from app.entrada import mao
from app.entrada.camera import CameraNula
from app.janela import JanelaPrincipal


class CameraFalsa(CameraNula):
    instancias: list["CameraFalsa"] = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ligada = False
        CameraFalsa.instancias.append(self)

    def start(self):
        self.ligada = True
        self.estado.emit("ligada")

    def parar(self):
        self.ligada = False
        super().parar()


@pytest.fixture
def janela(qtbot):
    CameraFalsa.instancias = []
    j = JanelaPrincipal(fabrica_camera=CameraFalsa)
    qtbot.addWidget(j)
    j.resize(1280, 720)
    j.show()
    return j


def _mao_em(x, y, pinca=False):
    pontos = [(0.5, 0.5, 0.0)] * 21
    pontos[mao.PUNHO] = (0.5, 0.9, 0.0)
    pontos[mao.BASE_MEDIO] = (0.5, 0.6, 0.0)
    pontos[mao.INDICADOR] = (x, y, 0.0)
    pontos[mao.POLEGAR] = (x, y, 0.0) if pinca else (x - 0.2, y, 0.0)
    return pontos


def test_navegacao_inicio_materias_trilhas(janela, qtbot):
    assert janela.pilha.currentWidget() is janela.inicio
    qtbot.mouseClick(janela.inicio.botao_comecar, Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.materias
    qtbot.mouseClick(janela.materias.botoes["matematica"], Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.trilhas
    assert [b.text() for b in janela.trilhas.botoes] == ["Teste da mão"]
    qtbot.mouseClick(janela.trilhas.botao_voltar, Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.materias


def test_navegacao_por_teclado(janela, qtbot):
    qtbot.keyClick(janela.inicio.botao_comecar, Qt.Key_Space)
    assert janela.pilha.currentWidget() is janela.materias
    assert janela.materias.botoes["portugues"].hasFocus()


def test_trilhas_escondem_atividades_que_nao_existem(janela):
    janela.abrir_materia("portugues")
    assert [b.text() for b in janela.trilhas.botoes] == ["Teste da mão"]


def test_camera_liga_so_dentro_da_atividade(janela, qtbot):
    janela.abrir_materia("portugues")
    assert CameraFalsa.instancias == []
    qtbot.mouseClick(janela.trilhas.botoes[0], Qt.LeftButton)
    tela = janela.atividades["teste_camera"]
    assert janela.pilha.currentWidget() is tela
    camera = CameraFalsa.instancias[-1]
    assert camera.ligada
    assert tela.indicador.accessibleName() == "Câmera ligada"

    qtbot.mouseClick(tela.botao_voltar, Qt.LeftButton)
    assert not camera.ligada
    assert tela.camera is None
    assert tela.indicador.accessibleName() == "Câmera desligada"


def test_teste_da_mao_mostra_cursor_e_pinca(janela):
    janela.abrir_atividade("teste_camera")
    tela = janela.atividades["teste_camera"]
    camera = CameraFalsa.instancias[-1]

    camera.pontos.emit(_mao_em(0.5, 0.5), True)
    assert tela.cena.cursor.isVisible()
    assert tela.rotulo_pinca.text() == "Pinça: aberta"
    area = tela.cena.scene().sceneRect()
    assert tela.cena.cursor.pos().x() == pytest.approx(area.center().x(), abs=1)

    camera.pontos.emit(_mao_em(0.5, 0.5, pinca=True), True)
    assert tela.rotulo_pinca.text() == "Pinça: fechada"

    camera.pontos.emit([], False)
    assert not tela.cena.cursor.isVisible()
    assert tela.rotulo_mao.text() == "Mão: não vejo"


def test_esc_sai_da_atividade(janela, qtbot):
    janela.abrir_materia("portugues")
    janela.abrir_atividade("teste_camera")
    qtbot.keyClick(janela.atividades["teste_camera"], Qt.Key_Escape)
    assert janela.pilha.currentWidget() is janela.trilhas


def test_botoes_tem_nome_acessivel(janela):
    from PySide6.QtWidgets import QPushButton

    janela.abrir_materia("matematica")
    for botao in janela.findChildren(QPushButton):
        assert botao.accessibleName(), botao.text()
