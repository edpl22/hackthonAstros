"""Cursor da mão desenhado na cena, com o anel de permanência.

Mão aberta: círculo vazado. Pinça fechada: círculo menor e cheio. O anel cresce enquanto o
cursor fica parado sobre um alvo (modo permanência). Forma e preenchimento mudam, não só a cor.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen
from PySide6.QtWidgets import QGraphicsItem

from app.nucleo.tema import paleta_atual

RAIO_ABERTO = 28
RAIO_FECHADO = 18
RAIO_ANEL = 38


class CursorMao(QGraphicsItem):
    def __init__(self, escala: float = 1.0):
        super().__init__()
        self.escala = escala
        self.fechado = False
        self.progresso = 0.0
        self.setZValue(1000)
        self.setVisible(False)

    def boundingRect(self) -> QRectF:
        r = (RAIO_ANEL + 6) * self.escala
        return QRectF(-r, -r, 2 * r, 2 * r)

    def atualizar(self, x: float, y: float, fechado: bool, progresso: float) -> None:
        self.setPos(x, y)
        if (fechado, progresso) != (self.fechado, self.progresso):
            self.fechado, self.progresso = fechado, progresso
            self.update()
        self.setVisible(True)

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        raio = (RAIO_FECHADO if self.fechado else RAIO_ABERTO) * self.escala
        pintor.setPen(QPen(QColor(p.texto), 4))
        # Aberta: só o contorno, para não cobrir a letra embaixo. Fechada: cheio e menor.
        pintor.setBrush(QBrush(QColor(p.primaria)) if self.fechado else Qt.NoBrush)
        pintor.drawEllipse(QRectF(-raio, -raio, 2 * raio, 2 * raio))
        if self.progresso > 0:
            anel = RAIO_ANEL * self.escala
            caneta = QPen(QColor(p.primaria), 6)
            caneta.setCapStyle(Qt.FlatCap)
            pintor.setPen(caneta)
            pintor.setBrush(Qt.NoBrush)
            # Ângulos do Qt em 1/16 de grau; começa no topo e anda no sentido horário.
            arco = -int(360 * 16 * self.progresso)
            pintor.drawArc(QRectF(-anel, -anel, 2 * anel, 2 * anel), 90 * 16, arco)
