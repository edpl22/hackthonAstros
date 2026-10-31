"""Cria a "Turma de demonstração" (6 alunos fictícios com tentativas) no banco do Atlas.

Uso: python scripts/seed_demo.py   (o banco fica em ATLAS_DADOS ou na pasta de dados do usuário)
Os dados são inventados e aparecem rotulados como "Turma de demonstração" no painel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.nucleo import turma_demo  # noqa: E402
from app.nucleo.registro import Registro  # noqa: E402

if __name__ == "__main__":
    registro = Registro()
    if any(a.apelido == turma_demo.ALUNOS[0][0] for a in registro.listar_alunos()):
        print("a turma de demonstracao ja existe neste banco")
    else:
        turma_demo.criar(registro)
        print(f"{turma_demo.NOME_TURMA}: {len(turma_demo.ALUNOS)} alunos criados")
