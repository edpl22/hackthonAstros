"""Cena das atividades de pegar e soltar: peças, caixas e o cursor da mão.

Só escuta o barramento (apontar, pegar, soltar) e avisa a atividade por sinais. Não decide
se uma jogada está certa: a atividade decide e chama `encaixar` ou `devolver`.
A cena tem tamanho lógico fixo (1280 x 560) e é escalada para caber na janela.
"""

import math
import os

from PySide6.QtCore import QPointF, QPropertyAnimation, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import QFrame, QGraphicsObject, QGraphicsScene, QGraphicsView

from app.entrada.alvos import Area, mais_proximo
from app.entrada.cursor import CursorMao
from app.nucleo import caminhos, figuras
from app.nucleo.tema import paleta_atual

# Mais larga que 16:9: é o formato da área que sobra abaixo da faixa e da instrução.
LARGURA, ALTURA = 1280, 560
DURACAO_MS = 250  # animações sempre até 300 ms
PX_POR_S_NA_VELOCIDADE_1 = 40  # bolhas flutuam a velocidade x 40 px/s
QUADRO_MS = 33


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

    def _contorno(self, pintor, margem: float) -> None:
        r = self._quadro().adjusted(-margem, -margem, margem, margem)
        if getattr(self, "forma", "") == "redondo":
            pintor.drawEllipse(r)
        else:
            pintor.drawRoundedRect(r, 12, 12)

    def _desenhar_foco(self, pintor) -> None:
        if self.realcado:  # pista: contorno duplo grosso, forma e não só cor
            pintor.setPen(QPen(QColor(paleta_atual().primaria), 6))
            pintor.setBrush(Qt.NoBrush)
            self._contorno(pintor, 6)
            self._contorno(pintor, 11)
        if self.focado:
            pintor.setPen(QPen(QColor(paleta_atual().primaria), 4))
            pintor.setBrush(Qt.NoBrush)
            self._contorno(pintor, 8)

    def _desenhar_rotulo(self, pintor, tamanho: float, sublinhado: bool = False) -> None:
        fonte = QFont(pintor.font())
        fonte.setPixelSize(round(tamanho))
        fonte.setBold(True)
        fonte.setUnderline(sublinhado)
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
        self.forma = "quadrado"  # ou "redondo" (bolha)
        self.alternada = False  # dislexia: sílabas alternam cor e sublinhado
        self.direcao = QPointF(0, 0)  # para flutuar
        self.figura: str | None = None  # SVG no lugar do rótulo (objetos da Mesa)
        self.hachura = False  # destaque da sobra: hachura + contorno grosso (não só cor)
        self.setZValue(5)

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        if self.figura:
            self._pintar_figura(pintor, p)
            return
        espessura = self.contorno + (3 if self.segurada else 0)
        pintor.setPen(QPen(QColor(p.texto), espessura))
        if self.segurada:
            fundo = p.destaque
        else:
            fundo = p.alternada if self.alternada else p.superficie
        pintor.setBrush(QBrush(QColor(fundo)))
        if self.forma == "redondo":
            pintor.drawEllipse(self._quadro())
        else:
            pintor.drawRoundedRect(self._quadro(), 12, 12)
        letras = len(self.rotulo)
        tamanho = self.lado * (0.42 if letras <= 2 else 0.36 if letras == 3 else 0.22)
        self._desenhar_rotulo(pintor, tamanho, sublinhado=self.alternada)
        self._desenhar_foco(pintor)

    def _pintar_figura(self, pintor, p) -> None:
        quadro = self._quadro()
        if self.segurada or self.hachura:
            pintor.setPen(QPen(QColor(p.texto), self.contorno + 2))
            pincel = QBrush(QColor(p.destaque), Qt.BDiagPattern) if self.hachura else QBrush(
                QColor(p.destaque)
            )
            pintor.setBrush(pincel)
            pintor.drawEllipse(quadro.adjusted(-6, -6, 6, 6))
        lado = max(8, round(self.lado))
        pintor.drawPixmap(quadro.toRect(), figuras.pixmap(self.figura, lado))
        self._desenhar_foco(pintor)


class Caixa(_Figura):
    @property
    def ocupada_por(self) -> str | None:
        return self.ocupantes[0] if self.ocupantes else None

    def posicao_vaga(self, indice: int) -> QPointF:
        """Centro da vaga `indice`: uma só no meio, ou uma grade de 4 colunas na bandeja."""
        if self.capacidade == 1:
            return self.pos()
        celula = self.lado / 4
        linha, coluna = divmod(indice, 4)
        canto = self.pos() - QPointF(self.lado / 2, self.lado / 2)
        return canto + QPointF(celula * (coluna + 0.5), celula * (linha + 0.5))

    """Destino. Vazia: borda tracejada; ocupada: borda contínua (forma, não só cor)."""

    def __init__(self, *args):
        super().__init__(*args)
        self.ocupantes: list[str] = []
        self.capacidade = 1  # bandejas da Mesa recebem vários objetos
        self.mostrar_rotulo = True
        self.setZValue(1)

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        caneta = QPen(QColor(p.texto), self.contorno)
        if self.ocupada_por is None:
            caneta.setStyle(Qt.DashLine)
        pintor.setPen(caneta)
        pintor.setBrush(QBrush(QColor(p.fundo)))
        pintor.drawRoundedRect(self._quadro(), 12, 12)
        if self.mostrar_rotulo:
            self._desenhar_rotulo(pintor, self.lado * 0.3)
        self._desenhar_foco(pintor)


class CenaItens(QGraphicsView):
    pegou = Signal(str)
    soltou = Signal(str, object)  # id da peça, id da caixa (ou None se caiu fora)
    nada_para_pegar = Signal()
    escolheu = Signal(str)  # escolha direta por id (cartões, sílaba tônica)

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
        barramento.escolher.connect(self._escolher)
        barramento.segurando = False
        self._timer_flutuar = QTimer(self)
        self._timer_flutuar.setInterval(QUADRO_MS)
        self._timer_flutuar.timeout.connect(self._passo_flutuar)
        self._regiao_flutuar = QRectF()
        self._velocidade_px_s = 0.0

    # --- montagem ------------------------------------------------------------

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def adicionar_peca(
        self, id: str, rotulo: str, x: float, y: float, lado: float,
        tipo: str = "peca", forma: str = "quadrado", alternada: bool = False,
    ) -> Peca:
        peca = Peca(id, rotulo, tipo, lado, self.perfil.contorno_px)
        peca.forma, peca.alternada = forma, alternada
        peca.setPos(x, y)
        peca.origem = QPointF(x, y)
        self.scene().addItem(peca)
        self.pecas[id] = peca
        return peca

    def adicionar_caixa(
        self, id: str, rotulo: str, x: float, y: float, lado: float, mostrar_rotulo: bool = True
    ) -> Caixa:
        caixa = Caixa(id, rotulo, "caixa", lado, self.perfil.contorno_px)
        caixa.mostrar_rotulo = mostrar_rotulo
        caixa.setPos(x, y)
        self.scene().addItem(caixa)
        self.caixas[id] = caixa
        return caixa

    def adicionar_figura(self, relativo: str, x: float, y: float, lado: float) -> None:
        """Figura SVG (não interativa), centrada em (x, y). Escala sem perder nitidez."""
        figura = QGraphicsSvgItem(str(caminhos.asset(relativo)))
        tamanho = figura.boundingRect()
        if tamanho.width() > 0:
            escala = lado / max(tamanho.width(), tamanho.height())
            figura.setScale(escala)
            figura.setPos(x - tamanho.width() * escala / 2, y - tamanho.height() * escala / 2)
        figura.setZValue(0)
        self.scene().addItem(figura)
        self.figura = figura

    def flutuar(self, velocidade: float, regiao: QRectF) -> None:
        """Peças livres andam devagar dentro da região (velocidade 0..1 do perfil x 40 px/s).
        Paradas com velocidade 0, "reduzir movimento" ou nos modos sem tela."""
        if velocidade <= 0 or self.perfil.reduzir_movimento or _sem_animacao():
            return
        self._velocidade_px_s = velocidade * PX_POR_S_NA_VELOCIDADE_1
        self._regiao_flutuar = regiao
        for i, peca in enumerate(self.pecas.values()):
            angulo = 0.7 + i * 2.1  # direções diferentes e repetíveis
            peca.direcao = QPointF(math.cos(angulo), math.sin(angulo))
        self._timer_flutuar.start()

    def _passo_flutuar(self) -> None:
        passo = self._velocidade_px_s * QUADRO_MS / 1000
        r = self._regiao_flutuar
        for peca in self.pecas_livres():
            pos = peca.pos() + peca.direcao * passo
            meio = peca.lado / 2
            if not r.left() + meio <= pos.x() <= r.right() - meio:
                peca.direcao.setX(-peca.direcao.x())
            if not r.top() + meio <= pos.y() <= r.bottom() - meio:
                peca.direcao.setY(-peca.direcao.y())
            pos = peca.pos() + peca.direcao * passo
            peca.setPos(pos)
            peca.origem = pos  # ao errar, a bolha volta para onde estava flutuando

    def parar_flutuar(self) -> None:
        self._timer_flutuar.stop()

    # --- consultas -----------------------------------------------------------

    @staticmethod
    def _area(figura: _Figura) -> Area:
        lado = figura.lado
        return Area(figura.id, figura.x() - lado / 2, figura.y() - lado / 2, lado, lado)

    def pecas_livres(self) -> list[Peca]:
        return [p for p in self.pecas.values() if not p.encaixada and p.id != self.segurada]

    def caixas_livres(self) -> list[Caixa]:
        return [c for c in self.caixas.values() if len(c.ocupantes) < c.capacidade]

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

    def _escolher(self, id: str) -> None:
        if id in self.pecas and not self.pecas[id].encaixada:
            self.escolheu.emit(id)

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
        caixa.ocupantes.append(peca_id)
        caixa.update()
        self._mover(peca, caixa.posicao_vaga(len(caixa.ocupantes) - 1))

    def esvaziar(self, caixa_id: str) -> None:
        """Devolve todas as peças da caixa ao lugar de origem."""
        caixa = self.caixas[caixa_id]
        for peca_id in caixa.ocupantes:
            self.pecas[peca_id].encaixada = False
            self._mover(self.pecas[peca_id], self.pecas[peca_id].origem)
        caixa.ocupantes = []
        caixa.update()

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
                    "quantidade": len(c.ocupantes),
                }
                for c in self.caixas.values()
            ],
            "segurando": self.segurada,
        }
