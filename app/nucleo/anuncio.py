"""Frase que narra cada evento ("Peça A colocada na caixa A."): legenda, demo e agente."""

from app.nucleo.conteudo import carregar


def frase(chave: str, **dados) -> str:
    return carregar("frases.json")["anuncio"][chave].format(**dados)
