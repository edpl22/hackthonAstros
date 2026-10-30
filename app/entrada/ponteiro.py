"""Mouse e toque: arrastar e soltar, ou clicar no item e depois no destino.

`GestoPonteiro` é puro (decide quais eventos emitir); `EntradaPonteiro` só liga o Qt nele.
"""

import math

from PySide6.QtCore import QEvent, QObject, Qt

LIMIAR_ARRASTO_PX = 12  # abaixo disso, soltar o botão é um clique (modo clique-clique)


class GestoPonteiro:
    def __init__(self, esta_segurando):
        self._esta_segurando = esta_segurando  # pergunta à cena se há item na mão
        self._inicio = None
        self._arrastou = False
        self._pressionado = False

    def pressionar(self, x: float, y: float) -> list[tuple]:
        self._pressionado = True
        self._inicio, self._arrastou = (x, y), False
        if self._esta_segurando():
            return [("apontar", x, y), ("soltar",)]  # 2º clique do clique-clique
        return [("apontar", x, y), ("pegar",)]

    def mover(self, x: float, y: float) -> list[tuple]:
        if self._pressionado and self._inicio is not None:
            if math.dist(self._inicio, (x, y)) > LIMIAR_ARRASTO_PX:
                self._arrastou = True
        if self._pressionado or self._esta_segurando():
            return [("apontar", x, y)]
        return []

    def liberar(self, x: float, y: float) -> list[tuple]:
        self._pressionado = False
        if self._arrastou and self._esta_segurando():
            return [("apontar", x, y), ("soltar",)]
        return []  # foi um clique: o item continua na mão até o próximo clique


class EntradaPonteiro(QObject):
    """Filtro de eventos no viewport de uma QGraphicsView."""

    def __init__(self, view, barramento, parent=None):
        super().__init__(parent or view)
        self.view = view
        self.barramento = barramento
        self.gesto = GestoPonteiro(lambda: barramento.segurando)
        view.viewport().setAttribute(Qt.WA_AcceptTouchEvents, True)  # toque vira mouse
        view.viewport().setMouseTracking(True)
        view.viewport().installEventFilter(self)

    def eventFilter(self, _obj, evento):
        tipo = evento.type()
        if tipo not in (QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease):
            return False
        if tipo != QEvent.MouseMove and evento.button() != Qt.LeftButton:
            return False
        ponto = self.view.mapToScene(evento.position().toPoint())
        x, y = ponto.x(), ponto.y()
        if tipo == QEvent.MouseButtonPress:
            acoes = self.gesto.pressionar(x, y)
        elif tipo == QEvent.MouseMove:
            acoes = self.gesto.mover(x, y)
        else:
            acoes = self.gesto.liberar(x, y)
        if acoes:
            self.barramento.usar("mouse")
        emitir(self.barramento, acoes)
        return bool(acoes)


def emitir(barramento, acoes) -> None:
    for acao, *args in acoes:
        getattr(barramento, acao).emit(*args)
