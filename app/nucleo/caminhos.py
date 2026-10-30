"""Caminhos de arquivos, iguais rodando do código, instalado com pip, no Docker ou empacotado."""

import os
import sys
from pathlib import Path

_CODIGO = Path(__file__).resolve().parent.parent.parent


def _tem_conteudo(pasta: Path) -> bool:
    return (pasta / "conteudo").is_dir() and (pasta / "assets").is_dir()


def raiz() -> Path:
    """Pasta que contém `assets/` e `conteudo/`.

    Ordem: PyInstaller, variável `ATLAS_RAIZ`, pasta do código-fonte e, por último, a pasta atual
    (caso de `pip install .` seguido de `atlas` dentro do clone).
    """
    empacotado = getattr(sys, "_MEIPASS", None)
    if empacotado:
        return Path(empacotado)
    if os.environ.get("ATLAS_RAIZ"):
        return Path(os.environ["ATLAS_RAIZ"])
    for candidata in (_CODIGO, Path.cwd()):
        if _tem_conteudo(candidata):
            return candidata
    return _CODIGO


def asset(*partes: str) -> Path:
    return raiz().joinpath("assets", *partes)


def conteudo(*partes: str) -> Path:
    return raiz().joinpath("conteudo", *partes)


def dados() -> Path:
    """Pasta do banco SQLite: `ATLAS_DADOS` ou a pasta de dados do usuário de cada sistema."""
    if os.environ.get("ATLAS_DADOS"):
        return Path(os.environ["ATLAS_DADOS"])
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "Atlas"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Atlas"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "atlas"
