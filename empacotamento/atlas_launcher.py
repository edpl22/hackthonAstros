"""Entrada do executável empacotado: sem argumentos abre a janela; com argumentos, a CLI.

No Windows o executável não tem console (para a criança não ver uma janela preta), então
`sys.stdout` vem vazio. A saída da CLI vai para `atlas-saida.txt` ao lado do executável,
e `atlas demo` continua gravando as evidências na pasta pedida.
"""

import os
import sys

if sys.stdout is None or sys.stderr is None:
    destino = os.path.join(os.path.dirname(sys.executable), "atlas-saida.txt")
    arquivo = open(destino, "w", encoding="utf-8")  # noqa: SIM115 - fica aberto até o fim
    sys.stdout = sys.stdout or arquivo
    sys.stderr = sys.stderr or arquivo

from app.cli import main  # noqa: E402

sys.exit(main())
