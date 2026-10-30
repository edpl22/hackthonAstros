"""Figuras SVG renderizadas uma vez por tamanho e guardadas no QPixmapCache."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap, QPixmapCache
from PySide6.QtSvg import QSvgRenderer

from app.nucleo import caminhos


def pixmap(relativo: str, tamanho: int) -> QPixmap:
    """`relativo` é relativo a `assets/`, por exemplo `figuras/avatares/gato.svg`."""
    chave = f"{relativo}@{tamanho}"
    em_cache = QPixmap()
    if QPixmapCache.find(chave, em_cache):
        return em_cache
    imagem = QPixmap(tamanho, tamanho)
    imagem.fill(Qt.transparent)
    renderizador = QSvgRenderer(str(caminhos.asset(relativo)))
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing)
    renderizador.render(pintor)
    pintor.end()
    QPixmapCache.insert(chave, imagem)
    return imagem


def icone_avatar(avatar: str, tamanho: int) -> QIcon:
    return QIcon(pixmap(f"figuras/avatares/{avatar}.svg", tamanho))
