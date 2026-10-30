"""Indicador de privacidade: ponto + texto dizendo se a câmera está ligada.

O ponto é desenhado (cheio quando ligada, vazado quando não), em vez de usar um caractere
que pode faltar na fonte. O texto sempre acompanha: nunca só cor ou só forma.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from app.nucleo.conteudo import texto
from app.nucleo.tema import paleta_atual

FRASES = {
    "ligada": "teste_camera.camera_ligada",
    "ligando": "teste_camera.camera_ligando",
}
FRASE_DESLIGADA = "teste_camera.camera_desligada"
DIAMETRO = 18


class _Ponto(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cheio = False
        self.setFixedSize(DIAMETRO + 4, DIAMETRO + 4)

    def paintEvent(self, _evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        cor = QColor(paleta_atual().primaria if self.cheio else paleta_atual().texto)
        pintor.setPen(QPen(cor, 3))
        pintor.setBrush(cor if self.cheio else Qt.NoBrush)
        pintor.drawEllipse(QRectF(2, 2, DIAMETRO, DIAMETRO))


class IndicadorCamera(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ponto = _Ponto()
        self.rotulo = QLabel()
        self.rotulo.setWordWrap(False)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.ponto)
        layout.addWidget(self.rotulo)
        self.mostrar("desligada")

    def mostrar(self, estado: str) -> None:
        frase = texto(FRASES.get(estado, FRASE_DESLIGADA))
        self.ponto.cheio = estado == "ligada"
        self.ponto.update()
        self.rotulo.setText(frase)
        self.setAccessibleName(frase)
