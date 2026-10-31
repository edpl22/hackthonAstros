"""Painel do professor: grade aluno x habilidade e recomendações para quem precisa de apoio.

Cada estado tem ícone, texto e cor (nunca só cor): Domina (círculo com visto), Em progresso
(meio círculo), Precisa de apoio (triângulo com "!"). Vermelho não é usado.
"""

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.nucleo import painel
from app.nucleo.conteudo import texto
from app.nucleo.tema import paleta_atual
from app.telas.comum import botao_voltar, rotulo


class IconeEstado(QWidget):
    def __init__(self, estado: str, lado: int = 28, parent=None):
        super().__init__(parent)
        self.estado = estado
        self.setFixedSize(lado, lado)

    def paintEvent(self, _evento):
        p = paleta_atual()
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        r = QRectF(3, 3, self.width() - 6, self.height() - 6)
        pintor.setPen(QPen(QColor(p.texto), 2.5))
        if self.estado == painel.DOMINA:
            pintor.setBrush(QColor(p.primaria))
            pintor.drawEllipse(r)
            pintor.setPen(QPen(QColor(p.superficie), 3))
            pintor.drawPolyline(QPolygonF([
                QPointF(r.left() + r.width() * 0.25, r.center().y()),
                QPointF(r.left() + r.width() * 0.45, r.bottom() - r.height() * 0.25),
                QPointF(r.right() - r.width() * 0.2, r.top() + r.height() * 0.25),
            ]))
        elif self.estado == painel.EM_PROGRESSO:
            pintor.setBrush(Qt.NoBrush)
            pintor.drawEllipse(r)
            pintor.setBrush(QColor(p.apoio))
            pintor.drawPie(r, 90 * 16, 180 * 16)
        else:
            pintor.setBrush(QColor(p.destaque))
            pintor.drawPolygon(QPolygonF([
                QPointF(r.center().x(), r.top()), QPointF(r.right(), r.bottom()),
                QPointF(r.left(), r.bottom()),
            ]))
            pintor.drawLine(QPointF(r.center().x(), r.top() + r.height() * 0.35),
                            QPointF(r.center().x(), r.bottom() - r.height() * 0.3))
            pintor.drawPoint(QPointF(r.center().x(), r.bottom() - r.height() * 0.15))


class TelaPainel(QWidget):
    voltar = Signal()

    def __init__(self, registro, parent=None):
        super().__init__(parent)
        self.registro = registro
        self.celulas: dict = {}
        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)
        self.titulo = rotulo("", "instrucao", centro=False)
        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addSpacing(24)
        topo.addWidget(self.titulo, 1)

        legenda = QHBoxLayout()
        for estado in (painel.DOMINA, painel.EM_PROGRESSO, painel.PRECISA_APOIO):
            legenda.addWidget(IconeEstado(estado))
            legenda.addWidget(QLabel(texto(f"painel.{estado}")))
            legenda.addSpacing(24)
        legenda.addStretch()
        legenda.addWidget(QLabel(texto("painel.regra")))

        self.conteudo = QWidget()
        self.layout_conteudo = QVBoxLayout(self.conteudo)
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QScrollArea.NoFrame)
        rolagem.setWidget(self.conteudo)

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addLayout(legenda)
        layout.addWidget(rolagem, 1)

    def mostrar(self) -> None:
        while self.layout_conteudo.count():
            item = self.layout_conteudo.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
            elif item.layout():
                _esvaziar(item.layout())
        turma = self.registro.ler_config("nome_turma", texto("painel.sua_turma"))
        self.titulo.setText(f"{texto('painel.titulo')}: {turma}")
        alunos, habilidades, self.celulas = painel.grade(self.registro.listar_tentativas())
        if not alunos:
            self.layout_conteudo.addWidget(rotulo(texto("painel.sem_dados"), centro=False))
            self.layout_conteudo.addStretch()
            return

        grade = QGridLayout()
        grade.setHorizontalSpacing(24)
        grade.setVerticalSpacing(8)
        for j, habilidade in enumerate(habilidades, start=1):
            cabecalho = QLabel(f"<b>{habilidade.capitalize()}</b>")
            cabecalho.setWordWrap(True)
            grade.addWidget(cabecalho, 0, j)
        for i, aluno in enumerate(alunos, start=1):
            grade.addWidget(QLabel(f"<b>{aluno}</b>"), i, 0)
            for j, habilidade in enumerate(habilidades, start=1):
                s = self.celulas.get((aluno, habilidade))
                if s is not None:
                    grade.addWidget(self._celula(aluno, habilidade, s), i, j)
        caixa = QWidget()
        caixa.setLayout(grade)
        self.layout_conteudo.addWidget(caixa)

        self.layout_conteudo.addSpacing(16)
        self.layout_conteudo.addWidget(rotulo(texto("painel.recomendacoes"), "instrucao", False))
        frases = painel.recomendacoes(self.celulas) or [texto("painel.sem_recomendacoes")]
        for frase in frases:
            linha = QHBoxLayout()
            linha.addWidget(IconeEstado(painel.PRECISA_APOIO), alignment=Qt.AlignTop)
            texto_frase = rotulo(frase, centro=False)
            linha.addWidget(texto_frase, 1)
            self.layout_conteudo.addLayout(linha)
        self.layout_conteudo.addStretch()

    def _celula(self, aluno: str, habilidade: str, s: painel.Situacao) -> QWidget:
        celula = QWidget()
        linha = QHBoxLayout(celula)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.addWidget(IconeEstado(s.estado))
        nome = texto(f"painel.{s.estado}")
        linha.addWidget(QLabel(f"{nome} <small>({s.certos_primeira}/{s.itens})</small>"))
        linha.addStretch()
        celula.setAccessibleName(
            f"{aluno}, {habilidade}: {nome}, {s.certos_primeira} de {s.itens} na primeira tentativa"
        )
        return celula

    def focar(self) -> None:
        self.botao_voltar.setFocus()


def _esvaziar(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().hide()
            item.widget().deleteLater()
        elif item.layout():
            _esvaziar(item.layout())
