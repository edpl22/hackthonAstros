"""Barramento de eventos: a única porta de entrada das atividades.

Mouse, toque, teclado, varredura, câmera, a mão simulada, o demo e o agente emitem estes
mesmos sinais. Nenhuma atividade sabe qual entrada foi usada.
"""

from PySide6.QtCore import QObject, Signal


class Barramento(QObject):
    apontar = Signal(float, float)  # coordenadas da cena
    pegar = Signal()  # pega o item sob o ponto apontado
    soltar = Signal()  # solta o item segurado no ponto apontado
    escolher = Signal(str)  # escolhe um item pelo id (cartões, botões de resposta)
    pausar = Signal()
    continuar = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.modo_entrada = "mouse"
        self.segurando = False  # mantido pela cena; as entradas consultam

    def usar(self, modo: str) -> "Barramento":
        """Registra qual entrada está agindo (vai para o registro das tentativas)."""
        self.modo_entrada = modo
        return self
