"""Peças repetidas entre as telas."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from app.nucleo.conteudo import texto


def botao(rotulo: str, nome_objeto: str | None = None) -> QPushButton:
    b = QPushButton(rotulo)
    b.setAccessibleName(rotulo)
    b.setCursor(Qt.PointingHandCursor)
    b.setFocusPolicy(Qt.StrongFocus)
    if nome_objeto:
        b.setObjectName(nome_objeto)
    return b


def botao_voltar() -> QPushButton:
    return botao(texto("comum.voltar"))


def rotulo(conteudo: str, nome_objeto: str | None = None, centro: bool = True) -> QLabel:
    r = QLabel(conteudo)
    r.setWordWrap(True)
    if centro:
        r.setAlignment(Qt.AlignCenter)
    if nome_objeto:
        r.setObjectName(nome_objeto)
    return r
