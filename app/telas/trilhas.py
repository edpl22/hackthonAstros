"""Trilhas de uma matéria. Mostra só o nome da habilidade, nunca o ano escolar."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from app.nucleo.conteudo import carregar, texto
from app.telas.comum import botao, botao_voltar, rotulo

COLUNAS = 3


class TelaTrilhas(QWidget):
    escolheu = Signal(str)  # id da atividade
    voltar = Signal()

    def __init__(self, atividades_disponiveis, parent=None):
        super().__init__(parent)
        self.atividades_disponiveis = set(atividades_disponiveis)
        self.botoes = []

        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)
        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addStretch()

        self.grade = QGridLayout()
        self.grade.setSpacing(32)
        grade_centro = QHBoxLayout()
        grade_centro.addStretch()
        grade_centro.addLayout(self.grade)
        grade_centro.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addStretch(1)
        layout.addWidget(rotulo(texto("trilhas.instrucao"), "instrucao"))
        layout.addSpacing(32)
        layout.addLayout(grade_centro)
        layout.addStretch(2)

    def mostrar(self, materia: str) -> None:
        for b in self.botoes:
            self.grade.removeWidget(b)
            b.deleteLater()
        self.botoes = []

        # Trilhas cujas atividades ainda não existem ficam escondidas.
        disponiveis = self.atividades_disponiveis
        trilhas = [t for t in carregar("trilhas.json")[materia] if t["atividade"] in disponiveis]
        anterior = self.botao_voltar
        for i, trilha in enumerate(trilhas):
            b = botao(trilha["nome"], "grande")
            b.clicked.connect(lambda _=False, a=trilha["atividade"]: self.escolheu.emit(a))
            self.grade.addWidget(b, i // COLUNAS, i % COLUNAS)
            QWidget.setTabOrder(anterior, b)
            anterior = b
            self.botoes.append(b)

    def focar(self) -> None:
        (self.botoes[0] if self.botoes else self.botao_voltar).setFocus()
