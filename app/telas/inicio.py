"""Tela inicial. Na Etapa 2 vira "Quem vai jogar?", com os apelidos e avatares."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.nucleo.conteudo import texto
from app.telas.comum import botao, rotulo


class TelaInicio(QWidget):
    comecar = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.botao_comecar = botao(texto("inicio.comecar"), "grande")
        self.botao_comecar.clicked.connect(self.comecar)

        layout = QVBoxLayout(self)
        layout.setSpacing(32)
        layout.addStretch(2)
        layout.addWidget(rotulo(texto("inicio.titulo"), "titulo"))
        layout.addWidget(rotulo(texto("inicio.subtitulo"), "instrucao"))
        layout.addSpacing(16)
        layout.addWidget(self.botao_comecar, alignment=Qt.AlignHCenter)
        layout.addStretch(3)

    def focar(self) -> None:
        self.botao_comecar.setFocus()
