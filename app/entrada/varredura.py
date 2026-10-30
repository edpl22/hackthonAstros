"""Varredura: o foco avança sozinho a cada 1,5 s e qualquer tecla seleciona.

Pensada para quem usa um único acionador (uma tecla grande, um botão adaptado).
"""

from PySide6.QtCore import Qt, QTimer

from app.entrada.teclado import EntradaTeclado

INTERVALO_MS = 1500


class EntradaVarredura(EntradaTeclado):
    modo = "varredura"

    def __init__(self, cena, barramento, parent=None, intervalo_ms: int = INTERVALO_MS):
        super().__init__(cena, barramento, parent)
        self.timer = QTimer(self)
        self.timer.setInterval(intervalo_ms)
        self.timer.timeout.connect(self.avancar)

    def ligar(self) -> None:
        self.avancar()
        self.timer.start()

    def desligar(self) -> None:
        self.timer.stop()

    def tratar_tecla(self, tecla) -> bool:
        if tecla == Qt.Key_Escape:
            self.barramento.pausar.emit()
        else:
            self.selecionar()
            self.timer.start()  # recomeça a contagem depois de cada escolha
        return True
