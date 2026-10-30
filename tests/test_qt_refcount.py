"""Regressão: o PySide6 6.12.0 no Linux tirava uma referência do None a cada setPos/setVisible
de um item de cena. Com a mão (milhares de quadros) o Python abortava ao finalizar.
Ver docs/DECISOES.md. Este teste falha se uma versão com esse bug voltar a ser instalada.
"""

import sys

from PySide6.QtWidgets import QGraphicsEllipseItem


def test_setpos_e_setvisible_nao_vazam_referencias(qapp):
    item = QGraphicsEllipseItem()
    antes_none, antes_true = sys.getrefcount(None), sys.getrefcount(True)
    for _ in range(200):
        item.setPos(1.0, 2.0)
        item.setVisible(True)
    # Pequena folga para objetos criados pelo próprio laço.
    assert abs(sys.getrefcount(None) - antes_none) < 20
    assert abs(sys.getrefcount(True) - antes_true) < 20
