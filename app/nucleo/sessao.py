"""Quem está jogando agora e o perfil combinado dessa criança."""

from PySide6.QtCore import QObject, Signal

from app.nucleo.perfis import PADRAO, Perfil, combinar


class Sessao(QObject):
    mudou = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.aluno = None  # None = visitante
        self.perfis: list[str] = []
        self.perfil: Perfil = PADRAO

    def definir(self, aluno=None, perfis=None) -> None:
        """Aluno cadastrado usa os perfis dele; visitante usa `perfis` (padrão se vazio)."""
        self.aluno = aluno
        self.perfis = list(aluno.perfis if aluno else (perfis or []))
        self.perfil = combinar(self.perfis)
        self.mudou.emit()
