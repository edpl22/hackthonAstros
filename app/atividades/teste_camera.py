"""Atividade "Teste da mão": mostra o cursor seguindo o indicador e o estado da pinça.

A câmera liga ao entrar na atividade e desliga ao sair. Na Etapa 2 o cursor passa a vir
de `entrada/cursor.py` e a posição chega pelo barramento de eventos.
"""

import time

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.entrada.camera import CameraNula
from app.entrada.mao import EstadoMao, RastreadorMao
from app.nucleo.conteudo import texto
from app.nucleo.tema import PALETA_PADRAO
from app.telas.comum import botao_voltar, rotulo
from app.telas.indicador_camera import IndicadorCamera

RAIO_ABERTO = 28
RAIO_FECHADO = 18


class Cena(QGraphicsView):
    """Área onde o cursor da mão se move. A cena sempre tem o tamanho da view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        p = PALETA_PADRAO
        self.setScene(QGraphicsScene(self))
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setBackgroundBrush(QColor(p.fundo))
        self.setFocusPolicy(Qt.NoFocus)

        self.cursor = QGraphicsEllipseItem()
        self.cursor.setPen(QPen(QColor(p.texto), 4))
        self.cursor.setVisible(False)
        self.scene().addItem(self.cursor)
        self._pincel_aberto = QBrush(QColor(p.superficie))
        self._pincel_fechado = QBrush(QColor(p.primaria))

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.scene().setSceneRect(QRectF(self.viewport().rect()))

    def mostrar(self, estado: EstadoMao) -> None:
        self.cursor.setVisible(estado.presente)
        if not estado.presente:
            return
        area = self.scene().sceneRect()
        # Pinça fechada muda tamanho e preenchimento, não só a cor.
        raio = RAIO_FECHADO if estado.pinca_fechada else RAIO_ABERTO
        self.cursor.setBrush(self._pincel_fechado if estado.pinca_fechada else self._pincel_aberto)
        self.cursor.setRect(-raio, -raio, 2 * raio, 2 * raio)
        self.cursor.setPos(
            area.left() + estado.x * area.width(), area.top() + estado.y * area.height()
        )


class TelaTesteCamera(QWidget):
    voltar = Signal()

    def __init__(self, fabrica_camera=CameraNula, parent=None):
        super().__init__(parent)
        self.fabrica_camera = fabrica_camera
        self.camera = None
        self.rastreador = RastreadorMao()
        self._fps = 0.0
        self._razao = float("inf")

        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)
        self.indicador = IndicadorCamera()

        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addSpacing(24)
        topo.addWidget(rotulo(texto("teste_camera.instrucao"), "instrucao"), 1)
        topo.addSpacing(24)
        topo.addWidget(self.indicador)

        self.cena = Cena()

        self.rotulo_mao = rotulo(texto("teste_camera.mao_ausente"), centro=False)
        self.rotulo_pinca = rotulo(texto("teste_camera.pinca_aberta"), centro=False)
        self.rotulo_tecnico = rotulo("", centro=False)
        self.miniatura = QLabel()
        self.miniatura.setFixedSize(160, 120)
        self.miniatura.setAccessibleName(texto("teste_camera.camera_ligada"))

        rodape = QHBoxLayout()
        rodape.setSpacing(32)
        rodape.addWidget(self.rotulo_mao)
        rodape.addWidget(self.rotulo_pinca)
        rodape.addStretch()
        rodape.addWidget(self.rotulo_tecnico)
        rodape.addWidget(self.miniatura)

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addWidget(self.cena, 1)
        layout.addLayout(rodape)

    # --- ciclo de vida -----------------------------------------------------

    def iniciar(self) -> None:
        if self.camera is not None:
            return
        self.rastreador = RastreadorMao()
        self.camera = self.fabrica_camera(mostrar_miniatura=True)
        self.camera.pontos.connect(self.ao_receber_pontos)
        self.camera.fps.connect(self._ao_receber_fps)
        self.camera.estado.connect(self.indicador.mostrar)
        self.camera.miniatura.connect(self._ao_receber_miniatura)
        self.camera.start()

    def parar(self) -> None:
        if self.camera is None:
            return
        camera, self.camera = self.camera, None
        camera.parar()
        camera.deleteLater()
        self.miniatura.clear()
        self.indicador.mostrar("desligada")
        self.ao_receber_pontos([], False)

    def focar(self) -> None:
        self.botao_voltar.setFocus()

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Escape:
            self.voltar.emit()
        else:
            super().keyPressEvent(evento)

    # --- sinais da câmera --------------------------------------------------

    def ao_receber_pontos(self, pontos, presente: bool) -> None:
        estado = self.rastreador.atualizar(pontos, presente, time.monotonic())
        self._razao = estado.razao
        self.cena.mostrar(estado)
        mao = "mao_presente" if estado.presente else "mao_ausente"
        pinca = "pinca_fechada" if estado.pinca_fechada else "pinca_aberta"
        self.rotulo_mao.setText(texto(f"teste_camera.{mao}"))
        self.rotulo_pinca.setText(texto(f"teste_camera.{pinca}"))
        self._atualizar_tecnico()

    def _ao_receber_fps(self, fps: float) -> None:
        self._fps = fps
        self._atualizar_tecnico()

    def _ao_receber_miniatura(self, imagem) -> None:
        self.miniatura.setPixmap(QPixmap.fromImage(imagem))

    def _atualizar_tecnico(self) -> None:
        razao = "–" if self._razao == float("inf") else f"{self._razao:.2f}".replace(".", ",")
        self.rotulo_tecnico.setText(f"{self._fps:.0f} fps · pinça {razao}")
