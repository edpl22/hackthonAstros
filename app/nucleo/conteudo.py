"""Leitura dos arquivos de `conteudo/`. Toda frase mostrada vem daqui, nunca do código."""

import json
from functools import cache

from app.nucleo import caminhos


@cache
def carregar(nome: str) -> dict:
    with caminhos.conteudo(nome).open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def texto(chave: str) -> str:
    """Busca uma frase em `frases.json` por chave pontuada, por exemplo `inicio.titulo`."""
    valor = carregar("frases.json")
    for parte in chave.split("."):
        valor = valor[parte]
    if not isinstance(valor, str):
        raise KeyError(f"'{chave}' não é uma frase")
    return valor
