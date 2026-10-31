import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton, QToolButton

from app.entrada import mao
from app.entrada.camera import CameraNula
from app.janela import JanelaPrincipal
from app.nucleo.registro import Registro


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
def janela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    CameraFalsa.instancias = []
    j = JanelaPrincipal(fabrica_camera=CameraFalsa, registro=Registro(":memory:"))
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


def _visitante(janela):
    return janela.inicio.botoes[-1]


def test_navegacao_inicio_materias_trilhas(janela, qtbot):
    assert janela.pilha.currentWidget() is janela.inicio
    assert _visitante(janela).text() == "Visitante"
    qtbot.mouseClick(_visitante(janela), Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.materias
    qtbot.mouseClick(janela.materias.botoes["matematica"], Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.trilhas
    esperado = ["Contar e comparar", "Frações com pizza"]  # treino e teste da mão saíram
    assert [b.text() for b in janela.trilhas.botoes] == esperado
    qtbot.mouseClick(janela.trilhas.botao_voltar, Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.materias


def test_navegacao_por_teclado(janela, qtbot):
    qtbot.keyClick(_visitante(janela), Qt.Key_Space)
    assert janela.pilha.currentWidget() is janela.materias
    assert janela.materias.botoes["portugues"].hasFocus()


def test_area_do_adulto_so_abre_segurando(janela, qtbot):
    botao = janela.inicio.adulto.botao
    janela.inicio.adulto.timer.setInterval(50)
    qtbot.mouseClick(botao, Qt.LeftButton)  # clique rápido não abre
    assert janela.pilha.currentWidget() is janela.inicio
    qtbot.mousePress(botao, Qt.LeftButton)
    qtbot.waitUntil(lambda: janela.pilha.currentWidget() is janela.adulto, timeout=1000)
    qtbot.mouseRelease(botao, Qt.LeftButton)


def test_cadastrar_aluno_e_jogar_com_os_perfis_dele(janela, qtbot):
    adulto = janela.adulto
    janela.ir_para(adulto)
    adulto.apelido.setText("Lia")
    adulto.botoes_avatar["sapo"].setChecked(True)
    adulto.caixas_perfil["baixa_visao"].setChecked(True)
    qtbot.mouseClick(adulto.botao_salvar, Qt.LeftButton)
    assert adulto.aviso.text() == "Aluno salvo."
    assert [a.apelido for a in janela.registro.listar_alunos()] == ["Lia"]

    qtbot.mouseClick(adulto.botao_voltar, Qt.LeftButton)
    lia = janela.inicio.botoes[0]
    assert lia.text() == "Lia" and not lia.icon().isNull()
    qtbot.mouseClick(lia, Qt.LeftButton)
    assert janela.sessao.perfil.escala == 1.75
    assert "#FFFFFF" in QApplication.instance().styleSheet()  # alto contraste

    janela.abrir_atividade("treino", semente=1)
    assert len(janela.atividades["treino"].cena.pecas) == 3  # baixa visão: até 3 itens


def test_adulto_nao_salva_sem_apelido(janela, qtbot):
    janela.ir_para(janela.adulto)
    qtbot.mouseClick(janela.adulto.botao_salvar, Qt.LeftButton)
    assert janela.adulto.aviso.text() == "Escreva um apelido."
    assert janela.registro.listar_alunos() == []


def test_adulto_edita_e_apaga(janela, qtbot):
    janela.registro.salvar_aluno("Rui", "gato", ["tea"])
    janela.adulto.recarregar()
    janela.adulto.lista.setCurrentRow(0)
    assert janela.adulto.caixas_perfil["tea"].isChecked()
    qtbot.mouseClick(janela.adulto.botao_apagar, Qt.LeftButton)
    assert janela.registro.listar_alunos() == []


def test_trilhas_escondem_atividades_que_nao_existem(janela):
    janela.abrir_materia("portugues")
    esperado = ["Treino de arrastar", "Juntar sílabas"]
    assert [b.text() for b in janela.trilhas.botoes] == esperado


def test_teste_da_mao_abre_pela_tela_inicial(janela, qtbot):
    assert CameraFalsa.instancias == []
    assert janela.inicio.teste_mao.text() == "Teste da mão"
    qtbot.mouseClick(janela.inicio.teste_mao, Qt.LeftButton)
    tela = janela.atividades["teste_camera"]
    assert janela.pilha.currentWidget() is tela
    camera = CameraFalsa.instancias[-1]
    assert camera.ligada and camera.mostrar_miniatura
    assert tela.indicador.accessibleName() == "Câmera ligada"

    qtbot.mouseClick(tela.botao_voltar, Qt.LeftButton)
    assert janela.pilha.currentWidget() is janela.inicio  # volta para onde abriu
    assert not camera.ligada
    assert tela.camera is None
    assert tela.indicador.accessibleName() == "Câmera desligada"


def test_tea_desliga_a_miniatura_da_camera(janela):
    janela.escolher_aluno(None, ["tea"])
    janela.abrir_atividade("teste_camera")
    assert CameraFalsa.instancias[-1].mostrar_miniatura is False


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


def test_esc_sai_do_teste_da_mao(janela, qtbot):
    janela.inicio.teste_mao.click()
    qtbot.keyClick(janela.atividades["teste_camera"], Qt.Key_Escape)
    assert janela.pilha.currentWidget() is janela.inicio


def test_todo_controle_tem_nome_acessivel(janela):
    janela.registro.salvar_aluno("Ana", "gato", [])
    janela.abrir_inicio()
    janela.abrir_materia("matematica")
    janela.abrir_atividade("treino", semente=1)
    for tipo in (QPushButton, QToolButton, QCheckBox):
        for controle in janela.findChildren(tipo):
            assert controle.accessibleName(), controle.text()
