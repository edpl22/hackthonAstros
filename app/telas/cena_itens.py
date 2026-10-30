"""Cena das atividades de pegar e soltar: peças, caixas e o cursor da mão.

Só escuta o barramento (apontar, pegar, soltar) e avisa a atividade por sinais. Não decide
se uma jogada está certa: a atividade decide e chama `encaixar` ou `devolver`.
A cena tem tamanho lógico fixo (1280 x 720) e é escalada para caber na janela.
"""

import os

from PySide6.QtCore import QPointF, QPropertyAnimation, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QGraphicsObject, QGraphicsScene, QGraphicsView

from app.entrada.alvos import Area, mais_proximo
from app.entrada.cursor import CursorMao
from app.nucleo.tema import paleta_atual

LARGURA, ALTURA = 1280, 720
DURACAO_MS = 250  # animações sempre até 300 ms


def _sem_animacao() -> bool:
    return os.environ.get("ATLAS_SEM_ANIMACAO") == "1"


class _Figura(QGraphicsObject):
    def __init__(self, id: str, rotulo: str, tipo: str, lado: float, contorno: int):
        super().__init__()
        self.id, self.rotulo, self.tipo = id, rotulo, tipo
        self.lado = lado
        self.contorno = contorno
        self.focado = False
        self.realcado = False  # pista 2

    def boundingRect(self) -> QRectF:
        m = self.lado / 2 + 16
        return QRectF(-m, -m, 2 * m, 2 * m)

    def _quadro(self) -> QRectF:
        return QRectF(-self.lado / 2, -self.lado / 2, self.lado, self.lado)

    def _desenhar_foco(self, pintor) -> None:
        if self.realcado:  # pista: contorno duplo grosso, forma e não só cor
            pintor.setPen(QPen(QColor(paleta_atual().primaria), 6))
            pintor.setBrush(Qt.NoBrush)
            pintor.drawRoundedRect(self._quadro().adjusted(-6, -6, 6, 6), 12, 12)
            pintor.drawRoundedRect(self._quadro().adjusted(-11, -11, 11, 11), 12, 12)
        if self.focado:
            pintor.setPen(QPen(QColor(paleta_atual().primaria), 4))
            pintor.setBrush(Qt.NoBrush)
            pintor.drawRoundedRect(self._quadro().adjusted(-8, -8, 8, 8), 12, 12)

    def _desenhar_rotulo(self, pintor, tamanho: float) -> None:
        fonte = QFont(pintor.font())
        fonte.setPixelSize(round(tamanho))
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.setPen(QColor(paleta_atual().texto))
        pintor.drawText(self._quadro(), Qt.AlignCenter, self.rotulo)


class Peca(_Figura):
    """Peça que a criança pega. Segurada: preenchimento de destaque + contorno mais grosso."""

    def __init__(self, *args):
        super().__init__(*args)
        self.segurada = False
        self.encaixada = False
        self.origem = QPointF()
        self.setZValue(5)

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        espessura = self.contorno + (3 if self.segurada else 0)
        pintor.setPen(QPen(QColor(p.texto), espessura))
        pintor.setBrush(QBrush(QColor(p.destaque if self.segurada else p.superficie)))
        pintor.drawRoundedRect(self._quadro(), 12, 12)
        self._desenhar_rotulo(pintor, self.lado * 0.5)
        self._desenhar_foco(pintor)


class Caixa(_Figura):
    """Destino. Vazia: borda tracejada; ocupada: borda contínua (forma, não só cor)."""

    def __init__(self, *args):
        super().__init__(*args)
        self.ocupada_por: str | None = None
        self.setZValue(1)

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        caneta = QPen(QColor(p.texto), self.contorno)
        if self.ocupada_por is None:
            caneta.setStyle(Qt.DashLine)
        pintor.setPen(caneta)
        pintor.setBrush(QBrush(QColor(p.fundo)))
        pintor.drawRoundedRect(self._quadro(), 12, 12)
        self._desenhar_rotulo(pintor, self.lado * 0.3)
        self._desenhar_foco(pintor)


class CenaItens(QGraphicsView):
    pegou = Signal(str)
    soltou = Signal(str, object)  # id da peça, id da caixa (ou None se caiu fora)
    nada_para_pegar = Signal()

    def __init__(self, barramento, perfil, parent=None):
        super().__init__(parent)
        self.barramento = barramento
        self.perfil = perfil
        self.pecas: dict[str, Peca] = {}
        self.caixas: dict[str, Caixa] = {}
        self.segurada: str | None = None
        self.ponto = (LARGURA / 2, ALTURA / 2)
        self._animacoes = []

        self.setScene(QGraphicsScene(0, 0, LARGURA, ALTURA, self))
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setBackgroundBrush(QColor(paleta_atual().fundo))
        self.setAccessibleName("Área da atividade")

        self.cursor = CursorMao(perfil.escala)
        self.scene().addItem(self.cursor)

        barramento.apontar.connect(self._apontar)
        barramento.pegar.connect(self._pegar)
        barramento.soltar.connect(self._soltar)
        barramento.segurando = False

    # --- montagem ------------------------------------------------------------

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def adicionar_peca(self, id: str, rotulo: str, x: float, y: float, lado: float) -> Peca:
        peca = Peca(id, rotulo, "peca", lado, self.perfil.contorno_px)
        peca.setPos(x, y)
        peca.origem = QPointF(x, y)
        self.scene().addItem(peca)
        self.pecas[id] = peca
        return peca

    def adicionar_caixa(self, id: str, rotulo: str, x: float, y: float, lado: float) -> Caixa:
        caixa = Caixa(id, rotulo, "caixa", lado, self.perfil.contorno_px)
        caixa.setPos(x, y)
        self.scene().addItem(caixa)
        self.caixas[id] = caixa
        return caixa

    # --- consultas -----------------------------------------------------------

    @staticmethod
    def _area(figura: _Figura) -> Area:
        lado = figura.lado
        return Area(figura.id, figura.x() - lado / 2, figura.y() - lado / 2, lado, lado)

    def pecas_livres(self) -> list[Peca]:
        return [p for p in self.pecas.values() if not p.encaixada and p.id != self.segurada]

    def caixas_livres(self) -> list[Caixa]:
        return [c for c in self.caixas.values() if c.ocupada_por is None]

    def ids_foco(self) -> list[str]:
        figuras = self.caixas_livres() if self.segurada else self.pecas_livres()
        return [f.id for f in sorted(figuras, key=lambda f: (round(f.y()), f.x()))]

    def centro(self, id: str) -> tuple[float, float]:
        figura = self.pecas.get(id) or self.caixas[id]
        return figura.x(), figura.y()

    def alvo_em(self, x: float, y: float) -> str | None:
        figuras = self.caixas_livres() if self.segurada else self.pecas_livres()
        return mais_proximo([self._area(f) for f in figuras], x, y, self.perfil.tolerancia_alvo_px)

    def realcar(self, ids) -> None:
        ids = set(ids)
        for figura in (*self.pecas.values(), *self.caixas.values()):
            if figura.realcado != (figura.id in ids):
                figura.realcado = figura.id in ids
                figura.update()

    def marcar_foco(self, id: str | None) -> None:
        for figura in (*self.pecas.values(), *self.caixas.values()):
            if figura.focado != (figura.id == id):
                figura.focado = figura.id == id
                figura.update()

    # --- eventos do barramento -----------------------------------------------

    def _apontar(self, x: float, y: float) -> None:
        self.ponto = (x, y)
        if self.segurada:
            self.pecas[self.segurada].setPos(x, y)

    def _pegar(self) -> None:
        if self.segurada:
            return
        id = self.alvo_em(*self.ponto)
        if id is None:
            self.nada_para_pegar.emit()
            return
        self.segurada = id
        peca = self.pecas[id]
        peca.segurada = True
        peca.setZValue(10)
        peca.setPos(*self.ponto)
        peca.update()
        self.barramento.segurando = True
        self.pegou.emit(id)

    def _soltar(self) -> None:
        if not self.segurada:
            return
        caixa = self.alvo_em(*self.ponto)
        id, self.segurada = self.segurada, None
        peca = self.pecas[id]
        peca.segurada = False
        peca.setZValue(5)
        peca.update()
        self.barramento.segurando = False
        self.soltou.emit(id, caixa)

    # --- respostas da atividade ----------------------------------------------

    def _mover(self, peca: Peca, destino: QPointF) -> None:
        if _sem_animacao() or self.perfil.reduzir_movimento:
            peca.setPos(destino)
            return
        animacao = QPropertyAnimation(peca, b"pos", self)
        animacao.setDuration(DURACAO_MS)
        animacao.setEndValue(destino)
        animacao.finished.connect(lambda: self._animacoes.remove(animacao))
        self._animacoes.append(animacao)
        animacao.start()

    def encaixar(self, peca_id: str, caixa_id: str) -> None:
        peca, caixa = self.pecas[peca_id], self.caixas[caixa_id]
        peca.encaixada = True
        caixa.ocupada_por = peca_id
        caixa.update()
        self._mover(peca, caixa.pos())

    def devolver(self, peca_id: str) -> None:
        peca = self.pecas[peca_id]
        self._mover(peca, peca.origem)

    def estado(self) -> dict:
        def posicao(f):
            return [round(f.x()), round(f.y())]

        return {
            "itens": [
                {
                    "id": p.id,
                    "rotulo": p.rotulo,
                    "tipo": p.tipo,
                    "posicao": posicao(p),
                    "disponivel": not p.encaixada,
                    "realcado": p.realcado,
                }
                for p in self.pecas.values()
            ],
            "alvos": [
                {
                    "id": c.id,
                    "rotulo": c.rotulo,
                    "tipo": c.tipo,
                    "posicao": posicao(c),
                    "ocupado_por": c.ocupada_por,
                }
                for c in self.caixas.values()
            ],
            "segurando": self.segurada,
        }
