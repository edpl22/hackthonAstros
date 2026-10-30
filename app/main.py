"""Entrada do Atlas: `python -m app.main`."""

import sys

from PySide6.QtWidgets import QApplication

from app.janela import JanelaPrincipal
from app.nucleo import tema
from app.nucleo.conteudo import texto


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(texto("app.nome"))
    tema.aplicar(app)
    janela = JanelaPrincipal()
    janela.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
