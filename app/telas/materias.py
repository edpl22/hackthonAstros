"""Escolha da matéria: Português ou Matemática."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from app.nucleo.conteudo import texto
from app.telas.comum import botao, botao_voltar, rotulo

MATERIAS = ("portugues", "matematica")


class TelaMaterias(QWidget):
    escolheu = Signal(str)
    voltar = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)

        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addStretch()

        self.botoes = {}
        linha = QHBoxLayout()
        linha.setSpacing(48)
        linha.addStretch()
        for materia in MATERIAS:
            b = botao(texto(f"materias.{materia}"), "grande")
            b.clicked.connect(lambda _=False, m=materia: self.escolheu.emit(m))
            self.botoes[materia] = b
            linha.addWidget(b)
        linha.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addStretch(1)
        layout.addWidget(rotulo(texto("materias.instrucao"), "instrucao"))
        layout.addSpacing(32)
        layout.addLayout(linha)
        layout.addStretch(2)

        # Ordem do Tab = ordem visual: Voltar, Português, Matemática.
        QWidget.setTabOrder(self.botao_voltar, self.botoes["portugues"])
        QWidget.setTabOrder(self.botoes["portugues"], self.botoes["matematica"])

    def focar(self) -> None:
        self.botoes["portugues"].setFocus(Qt.OtherFocusReason)
