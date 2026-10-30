"""Garante que o app não salva imagens nem fala com a rede (seção 7 da especificação)."""

import re
from pathlib import Path

RAIZ_APP = Path(__file__).resolve().parent.parent / "app"

PROIBIDOS = {
    "salvar quadro da câmera": re.compile(r"\bimwrite\b|\bVideoWriter\b"),
    "módulo de rede": re.compile(
        r"^\s*(import|from)\s+(socket|urllib|http\.client|requests|httpx|aiohttp|ftplib|smtplib)\b",
        re.MULTILINE,
    ),
    "rede do Qt": re.compile(r"\bQtNetwork\b|\bQNetworkAccessManager\b"),
}


def _arquivos_do_app():
    return sorted(RAIZ_APP.rglob("*.py"))


def test_existe_codigo_do_app():
    assert _arquivos_do_app(), "a pasta app/ deveria ter arquivos .py"


def test_app_nao_salva_imagens_nem_usa_rede():
    violacoes = []
    for arquivo in _arquivos_do_app():
        texto = arquivo.read_text(encoding="utf-8")
        for motivo, padrao in PROIBIDOS.items():
            if padrao.search(texto):
                violacoes.append(f"{arquivo.relative_to(RAIZ_APP.parent)}: {motivo}")
    assert not violacoes, "\n".join(violacoes)
