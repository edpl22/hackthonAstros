"""Janela principal: uma pilha de telas e a navegação entre elas."""

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.atividades.teste_camera import TelaTesteCamera
from app.entrada.camera import fabrica_padrao
from app.nucleo.conteudo import texto
from app.telas.inicio import TelaInicio
from app.telas.materias import TelaMaterias
from app.telas.trilhas import TelaTrilhas

MARGEM = 24


class JanelaPrincipal(QMainWindow):
    def __init__(self, fabrica_camera=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(texto("app.nome"))
        self.setMinimumSize(1024, 700)

        self.inicio = TelaInicio()
        self.materias = TelaMaterias()
        self.atividades = {"teste_camera": TelaTesteCamera(fabrica_camera or fabrica_padrao())}
        self.trilhas = TelaTrilhas(self.atividades.keys())

        self.pilha = QStackedWidget()
        for tela in (self.inicio, self.materias, self.trilhas, *self.atividades.values()):
            tela.layout().setContentsMargins(MARGEM, MARGEM, MARGEM, MARGEM)
            self.pilha.addWidget(tela)
        self.setCentralWidget(self.pilha)

        self.inicio.comecar.connect(lambda: self.ir_para(self.materias))
        self.materias.voltar.connect(lambda: self.ir_para(self.inicio))
        self.materias.escolheu.connect(self.abrir_materia)
        self.trilhas.voltar.connect(lambda: self.ir_para(self.materias))
        self.trilhas.escolheu.connect(self.abrir_atividade)
        for atividade in self.atividades.values():
            atividade.voltar.connect(lambda: self.ir_para(self.trilhas))

        self.ir_para(self.inicio)

    def ir_para(self, tela) -> None:
        atual = self.pilha.currentWidget()
        # A câmera só fica ligada dentro de uma atividade.
        if atual is not tela and atual in self.atividades.values():
            atual.parar()
        self.pilha.setCurrentWidget(tela)
        tela.focar()

    def abrir_materia(self, materia: str) -> None:
        self.trilhas.mostrar(materia)
        self.ir_para(self.trilhas)

    def abrir_atividade(self, atividade_id: str) -> None:
        atividade = self.atividades[atividade_id]
        self.ir_para(atividade)
        atividade.iniciar()

    def closeEvent(self, evento):
        for atividade in self.atividades.values():
            atividade.parar()
        super().closeEvent(evento)
