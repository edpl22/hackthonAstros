"""Teclado: setas e Tab movem o foco; Enter ou Espaço pega e solta; Esc pausa.

A cena informa quais ids podem receber foco (itens livres ou, com um item na mão, os alvos),
o centro de cada um e desenha o contorno de foco.
"""

from PySide6.QtCore import QEvent, QObject, Qt

from app.entrada.alvos import CicloFoco

AVANCAR = (Qt.Key_Tab, Qt.Key_Right, Qt.Key_Down)
VOLTAR = (Qt.Key_Backtab, Qt.Key_Left, Qt.Key_Up)
SELECIONAR = (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space)


class EntradaTeclado(QObject):
    modo = "teclado"

    def __init__(self, cena, barramento, parent=None):
        super().__init__(parent or cena)
        self.cena = cena
        self.barramento = barramento
        self.foco = CicloFoco()
        cena.setFocusPolicy(Qt.StrongFocus)
        cena.installEventFilter(self)

    def _atualizar_lista(self) -> None:
        self.foco.definir(self.cena.ids_foco())

    def avancar(self) -> str | None:
        self._atualizar_lista()
        atual = self.foco.avancar()
        self.cena.marcar_foco(atual)
        return atual

    def voltar(self) -> str | None:
        self._atualizar_lista()
        atual = self.foco.voltar()
        self.cena.marcar_foco(atual)
        return atual

    def selecionar(self) -> None:
        self._atualizar_lista()
        alvo = self.foco.atual
        if alvo is None:
            alvo = self.avancar()
            if alvo is None:
                return
        x, y = self.cena.centro(alvo)
        self.barramento.usar(self.modo)
        self.barramento.apontar.emit(x, y)
        if self.barramento.segurando:
            self.barramento.soltar.emit()
        else:
            self.barramento.pegar.emit()
        # Depois de pegar, o foco passa para os alvos; depois de soltar, volta aos itens.
        self.foco = CicloFoco()
        self.cena.marcar_foco(None)
        self.avancar()

    def tratar_tecla(self, tecla) -> bool:
        if tecla == Qt.Key_Escape:
            self.barramento.pausar.emit()
        elif tecla in AVANCAR:
            self.avancar()
        elif tecla in VOLTAR:
            self.voltar()
        elif tecla in SELECIONAR:
            self.selecionar()
        else:
            return False
        return True

    def eventFilter(self, _obj, evento):
        if evento.type() == QEvent.KeyPress and not evento.isAutoRepeat():
            return self.tratar_tecla(evento.key())
        # Tab precisa ser interceptado antes de o Qt trocar o foco de widget.
        tab = (Qt.Key_Tab, Qt.Key_Backtab)
        if evento.type() == QEvent.ShortcutOverride and evento.key() in tab:
            evento.accept()
            return True
        return False
