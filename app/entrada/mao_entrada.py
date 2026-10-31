"""Liga os pontos da mão (câmera real ou simulada) ao barramento de eventos.

Pinça fechando = pegar; pinça abrindo = soltar. No modo permanência, ficar parado sobre um
alvo pelo tempo do perfil também pega e solta.
Gesto "arminha" (Tabuada Protetora): a pinça fica desligada; o coice para cima dispara, ou
seja, aponta para a mira e pega o alvo que estiver lá.
"""

import time

from PySide6.QtCore import QObject

from app.entrada.mao import DetectorDisparo, DetectorPermanencia, RastreadorMao


class EntradaMao(QObject):
    def __init__(self, cena, barramento, perfil, gesto: str = "pinca", parent=None):
        super().__init__(parent or cena)
        self.cena = cena
        self.barramento = barramento
        self.rastreador = RastreadorMao()
        self.disparo = DetectorDisparo() if gesto == "arminha" else None
        self.permanencia = (
            DetectorPermanencia(perfil.tolerancia_alvo_px, perfil.tempo_permanencia_ms)
            if perfil.modo_entrada_preferido == "permanencia" and self.disparo is None
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
            if self.disparo:
                self.disparo.reiniciar()
            return

        area = self.cena.sceneRect()
        x = area.left() + estado.x * area.width()
        y = area.top() + estado.y * area.height()
        self.barramento.usar("camera")
        if self.disparo:
            self._arminha(estado, t, x, y)
            return
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

    def _arminha(self, estado, t: float, x: float, y: float) -> None:
        mira = self.disparo.atualizar(t, estado.y_bruto, (x, y), estado.arminha)
        if mira is not None:
            self.barramento.apontar.emit(*mira)
            self.barramento.pegar.emit()
            self.cena.cursor.atualizar(*mira, True, 0.0)
            return
        self.barramento.apontar.emit(x, y)
        self.cena.cursor.atualizar(x, y, False, 0.0)
