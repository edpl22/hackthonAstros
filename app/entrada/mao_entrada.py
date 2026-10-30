"""Liga os pontos da mão (câmera real ou simulada) ao barramento de eventos.

Pinça fechando = pegar; pinça abrindo = soltar. No modo permanência, ficar parado sobre um
alvo pelo tempo do perfil também pega e solta.
"""

import time

from PySide6.QtCore import QObject

from app.entrada.mao import DetectorPermanencia, RastreadorMao


class EntradaMao(QObject):
    def __init__(self, cena, barramento, perfil, parent=None):
        super().__init__(parent or cena)
        self.cena = cena
        self.barramento = barramento
        self.rastreador = RastreadorMao()
        self.permanencia = (
            DetectorPermanencia(perfil.tolerancia_alvo_px, perfil.tempo_permanencia_ms)
            if perfil.modo_entrada_preferido == "permanencia"
            else None
        )
        self._pinca_anterior = False
        self.ultimo_estado = None

    def receber(self, pontos, presente: bool, t: float | None = None) -> None:
        t = time.monotonic() if t is None else t
        estado = self.rastreador.atualizar(pontos, presente, t)
        self.ultimo_estado = estado
        if not estado.presente:
            self.cena.cursor.setVisible(False)
            self._pinca_anterior = False
            if self.permanencia:
                self.permanencia.reiniciar()
            return

        area = self.cena.sceneRect()
        x = area.left() + estado.x * area.width()
        y = area.top() + estado.y * area.height()
        self.barramento.usar("camera")
        self.barramento.apontar.emit(x, y)

        if estado.pinca_fechada and not self._pinca_anterior and not self.barramento.segurando:
            self.barramento.pegar.emit()
        elif not estado.pinca_fechada and self._pinca_anterior and self.barramento.segurando:
            self.barramento.soltar.emit()
        self._pinca_anterior = estado.pinca_fechada

        progresso = 0.0
        if self.permanencia:
            sobre_alvo = self.cena.alvo_em(x, y) is not None
            if self.permanencia.atualizar(x, y, t, sobre_alvo):
                self.barramento.usar("permanencia")
                b = self.barramento
                (b.soltar if b.segurando else b.pegar).emit()
            progresso = self.permanencia.progresso
        self.cena.cursor.atualizar(x, y, estado.pinca_fechada, progresso)
