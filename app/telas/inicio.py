"""Tela inicial "Quem vai jogar?": um botão por aluno (bicho + apelido) e o Visitante.

A área do adulto abre só segurando o botão por 2 s, para a criança não entrar sem querer.
O Teste da mão fica no canto inferior esquerdo: serve para qualquer matéria.
"""

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QToolButton, QVBoxLayout, QWidget

from app.nucleo import figuras
from app.nucleo.conteudo import texto
from app.telas.comum import botao, rotulo

COLUNAS = 4
TAMANHO_AVATAR = 96
TEMPO_SEGURAR_MS = 2000


class BotaoSegurar(QWidget):
    """Botão que só dispara depois de ficar pressionado por `tempo_ms` (mouse, toque ou Espaço)."""

    segurou = Signal()

    def __init__(self, rotulo_botao: str, tempo_ms: int = TEMPO_SEGURAR_MS, parent=None):
        super().__init__(parent)
        self.botao = botao(rotulo_botao)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(tempo_ms)
        self.timer.timeout.connect(self.segurou)
        self.botao.pressed.connect(self.timer.start)
        self.botao.released.connect(self.timer.stop)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.botao)


class TelaInicio(QWidget):
    escolheu = Signal(object)  # Aluno ou None (visitante)
    abrir_adulto = Signal()
    abrir_teste_mao = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.escala = 1.0
        self.botoes: list[QToolButton] = []
        self.grade = QGridLayout()
        self.grade.setSpacing(24)
        centro = QHBoxLayout()
        centro.addStretch()
        centro.addLayout(self.grade)
        centro.addStretch()

        self.adulto = BotaoSegurar(texto("inicio.adulto"))
        self.adulto.segurou.connect(self.abrir_adulto)
        self.teste_mao = botao(texto("inicio.teste_mao"))
        self.teste_mao.clicked.connect(self.abrir_teste_mao)
        rodape = QHBoxLayout()
        rodape.addWidget(self.teste_mao)
        rodape.addStretch()
        rodape.addWidget(self.adulto)

        layout = QVBoxLayout(self)
        layout.addStretch(1)
        layout.addWidget(rotulo(texto("inicio.quem_joga"), "titulo"))
        layout.addSpacing(32)
        layout.addLayout(centro)
        layout.addStretch(2)
        layout.addLayout(rodape)
        self.mostrar([])

    def _botao_aluno(self, apelido: str, avatar: str | None) -> QToolButton:
        b = QToolButton()
        b.setText(apelido)
        b.setAccessibleName(apelido)
        b.setCursor(Qt.PointingHandCursor)
        b.setFocusPolicy(Qt.StrongFocus)
        b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        lado = round(TAMANHO_AVATAR * self.escala)
        if avatar:
            b.setIcon(figuras.icone_avatar(avatar, lado))
            b.setIconSize(QSize(lado, lado))
        b.setFixedSize(lado + 96, lado + 96)
        return b

    def mostrar(self, alunos, escala: float = 1.0) -> None:
        self.escala = escala
        for b in self.botoes:
            self.grade.removeWidget(b)
            b.hide()  # some na hora; o deleteLater só roda no próximo ciclo de eventos
            b.deleteLater()
        self.botoes = []
        itens = [(a.apelido, a.avatar, a) for a in alunos]
        itens.append((texto("inicio.visitante"), None, None))
        anterior = None
        for i, (apelido, avatar, aluno) in enumerate(itens):
            b = self._botao_aluno(apelido, avatar)
            b.clicked.connect(lambda _=False, a=aluno: self.escolheu.emit(a))
            self.grade.addWidget(b, i // COLUNAS, i % COLUNAS)
            if anterior is not None:
                QWidget.setTabOrder(anterior, b)
            anterior = b
            self.botoes.append(b)
        if anterior is not None:
            QWidget.setTabOrder(anterior, self.teste_mao)
        QWidget.setTabOrder(self.teste_mao, self.adulto.botao)

    def focar(self) -> None:
        self.botoes[0].setFocus()
