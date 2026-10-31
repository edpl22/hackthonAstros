"""Regras puras da Pizza de Frações.

Níveis: 1 = Montar (pegar n fatias de uma pizza cortada em d e tocar em "Pronto");
2 = Somar frações de mesmo denominador, escolhendo entre 3 cartões (um errado é sempre o de
somar os denominadores); 3 = Desafio: a soma passa de uma pizza inteira (fração imprópria),
mostrada também como número misto (15/8 = 1 e 7/8).
"""

import random
from dataclasses import dataclass, field

from app.nucleo.erros import classificar_fracao

MONTAR, SOMAR, DESAFIO = 1, 2, 3
NIVEL_MAXIMO = 3
CORTES = (2, 3, 4, 6, 8)

Fracao = tuple[int, int]  # (numerador, denominador)


@dataclass(frozen=True)
class Cartao:
    id: str
    rotulo: str
    valor: Fracao | None  # None = "Pronto"


@dataclass
class Rodada:
    nivel: int
    corte: int
    parcelas: list[Fracao]
    certo: Fracao
    cartoes: list[Cartao] = field(default_factory=list)
    concluida: bool = False

    @property
    def montar(self) -> bool:
        return self.nivel == MONTAR


def texto(f: Fracao) -> str:
    return f"{f[0]}/{f[1]}"


def misto(f: Fracao) -> str:
    """15/8 -> "1 e 7/8"; 8/8 -> "1"; 3/4 -> "3/4"."""
    inteiros, resto = divmod(f[0], f[1])
    if inteiros == 0:
        return texto(f)
    return str(inteiros) if resto == 0 else f"{inteiros} e {resto}/{f[1]}"


def _cartao(f: Fracao) -> Cartao:
    return Cartao(f"cartao-{f[0]}-{f[1]}", texto(f), f)


def nova_rodada(nivel: int, semente: int | None = None, max_itens: int = 4) -> Rodada:
    r = random.Random(semente)
    if nivel == MONTAR:
        corte = r.choice((2, 3, 4) if max_itens <= 3 else CORTES)
        n = r.randint(1, corte - 1)
        pronto = Cartao("cartao-pronto", "Pronto", None)
        return Rodada(nivel, corte, [(n, corte)], (n, corte), [pronto])
    if nivel == SOMAR:
        corte = r.choice((3, 4, 6, 8))
        n1 = r.randint(1, corte - 2)
        n2 = r.randint(1, corte - 1 - n1)
    else:
        corte = r.choice((4, 6, 8))
        n1 = r.randint(2, corte)
        n2 = r.randint(corte - n1 + 1, corte)  # a soma passa de uma pizza inteira
    certo = (n1 + n2, corte)
    somou_denominadores = (n1 + n2, 2 * corte)
    terceiro = (corte, n1 + n2) if corte != n1 + n2 else (n1 + n2 + 1, corte)
    valores = [certo, somou_denominadores, terceiro]
    r.shuffle(valores)
    return Rodada(nivel, corte, [(n1, corte), (n2, corte)], certo, [_cartao(v) for v in valores])


def conferir_montar(rodada: Rodada, escolhidas: int) -> str | None:
    return None if escolhidas == rodada.certo[0] else "contou_fatias_errado"


def conferir_soma(rodada: Rodada, resposta: Fracao) -> str | None:
    return classificar_fracao(resposta, rodada.parcelas)
