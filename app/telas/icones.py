"""Ícones desenhados com QPainter (sem emoji nem caracteres que a fonte pode não ter)."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import QWidget

from app.nucleo.tema import paleta_atual


def desenhar(pintor: QPainter, tipo: str, lado: float) -> None:
    p = paleta_atual()
    caneta = QPen(QColor(p.texto), max(2.0, lado / 12))
    caneta.setJoinStyle(Qt.RoundJoin)
    caneta.setCapStyle(Qt.RoundCap)
    pintor.setPen(caneta)
    pintor.setBrush(Qt.NoBrush)
    m = lado * 0.15
    r = QRectF(m, m, lado - 2 * m, lado - 2 * m)
    if tipo == "apresentacao":  # balão de fala
        caminho = QPainterPath()
        caminho.addRoundedRect(QRectF(r.left(), r.top(), r.width(), r.height() * 0.7), 6, 6)
        pintor.drawPath(caminho)
        pintor.drawPolygon(QPolygonF([
            QPointF(r.left() + r.width() * 0.25, r.top() + r.height() * 0.7),
            QPointF(r.left() + r.width() * 0.2, r.bottom()),
            QPointF(r.left() + r.width() * 0.45, r.top() + r.height() * 0.7),
        ]))
    elif tipo == "atividade":  # seta entrando numa caixa
        pintor.drawRect(QRectF(r.left(), r.center().y(), r.width(), r.height() / 2))
        cx = r.center().x()
        pintor.drawLine(QPointF(cx, r.top()), QPointF(cx, r.center().y() + 6))
        pintor.drawPolyline(QPolygonF([
            QPointF(r.center().x() - 8, r.center().y() - 2),
            QPointF(r.center().x(), r.center().y() + 6),
            QPointF(r.center().x() + 8, r.center().y() - 2),
        ]))
    elif tipo == "fim":  # visto
        pintor.drawPolyline(QPolygonF([
            QPointF(r.left(), r.center().y()),
            QPointF(r.left() + r.width() * 0.38, r.bottom()),
            QPointF(r.right(), r.top()),
        ]))
    elif tipo == "nova_rodada":  # seta circular
        pintor.drawArc(r, 60 * 16, 300 * 16)
        topo = QPointF(r.center().x() + r.width() * 0.25, r.top() + r.height() * 0.07)
        pintor.drawPolyline(QPolygonF([topo + QPointF(-9, -6), topo, topo + QPointF(-3, 10)]))
    elif tipo in ("camera", "camera_desligada"):  # corpo, lente e visor; desligada: risco
        corpo = QRectF(r.left(), r.top() + r.height() * 0.25, r.width(), r.height() * 0.65)
        pintor.drawRoundedRect(corpo, 4, 4)
        pintor.drawRect(QRectF(r.left() + r.width() * 0.3, r.top() + r.height() * 0.1,
                               r.width() * 0.3, r.height() * 0.15))
        raio = r.width() * 0.2
        pintor.drawEllipse(corpo.center(), raio, raio)
        if tipo == "camera_desligada":
            pintor.drawLine(QPointF(r.left(), r.bottom()), QPointF(r.right(), r.top()))
    elif tipo == "pausa":  # duas barras
        pintor.setBrush(QColor(p.texto))
        largura = r.width() * 0.28
        pintor.drawRect(QRectF(r.left() + r.width() * 0.1, r.top(), largura, r.height()))
        pintor.drawRect(QRectF(r.right() - r.width() * 0.1 - largura, r.top(), largura, r.height()))


def icone(tipo: str, lado: int = 48) -> QIcon:
    imagem = QPixmap(lado, lado)
    imagem.fill(Qt.transparent)
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing)
    desenhar(pintor, tipo, lado)
    pintor.end()
    return QIcon(imagem)


class Pictograma(QWidget):
    """Ícone de momento na faixa Agora/Depois."""

    def __init__(self, tipo: str, lado: int = 40, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.setFixedSize(lado, lado)

    def definir(self, tipo: str) -> None:
        self.tipo = tipo
        self.update()

    def paintEvent(self, _evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        desenhar(pintor, self.tipo, self.width())
