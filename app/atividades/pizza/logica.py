"""Regras puras da Pizza de Frações.

Níveis: 1 = Montar (pegar n fatias de uma pizza cortada em d e tocar em "Pronto");
2 = Somar frações de mesmo denominador, escolhendo entre 3 cartões (um errado é sempre o de
somar os denominadores); 3 = Operar: 2 ou 3 pratos com soma e subtração misturadas
(3/8 + 4/8 - 2/8); 4 = Desafio: a soma passa de uma pizza inteira (fração imprópria),
mostrada também como número misto (15/8 = 1 e 7/8).
"""

import random
from dataclasses import dataclass, field

from app.nucleo.erros import classificar_fracao, resultado_fracao

MONTAR, SOMAR, OPERAR, DESAFIO = 1, 2, 3, 4
NIVEL_MAXIMO = 4
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
    sinais: list[str] = field(default_factory=list)  # entre as parcelas: "+" ou "-"

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


def conta(rodada: Rodada) -> str:
    """"3/8 + 4/8 - 2/8" (o sinal de menos aparece como "−" na tela)."""
    partes = [texto(rodada.parcelas[0])]
    for sinal, parcela in zip(rodada.sinais, rodada.parcelas[1:], strict=True):
        partes += [sinal, texto(parcela)]
    return " ".join(partes)


def _operar(r: random.Random, n_pratos: int) -> tuple[int, list[Fracao], list[str]]:
    """Sorteia pratos de mesmo corte e sinais com pelo menos uma subtração; o resultado fica
    entre 1 fatia e uma pizza inteira e nenhuma conta parcial fica negativa."""
    while True:
        corte = r.choice((4, 6, 8))
        sinais = [r.choice("+-") for _ in range(n_pratos - 1)]
        if "-" not in sinais:
            sinais[r.randrange(len(sinais))] = "-"
        numeradores = [r.randint(1, corte - 1) for _ in range(n_pratos)]
        parcial, valido = numeradores[0], True
        for sinal, n in zip(sinais, numeradores[1:], strict=True):
            parcial += n if sinal == "+" else -n
            valido = valido and parcial >= 1
        if valido and parcial <= corte:
            return corte, [(n, corte) for n in numeradores], sinais


def nova_rodada(nivel: int, semente: int | None = None, max_itens: int = 4) -> Rodada:
    r = random.Random(semente)
    if nivel == MONTAR:
        corte = r.choice((2, 3, 4) if max_itens <= 3 else CORTES)
        n = r.randint(1, corte - 1)
        pronto = Cartao("cartao-pronto", "Pronto", None)
        return Rodada(nivel, corte, [(n, corte)], (n, corte), [pronto])
    if nivel == OPERAR:
        corte, parcelas, sinais = _operar(r, 3 if max_itens >= 4 else 2)
    elif nivel == SOMAR:
        corte = r.choice((3, 4, 6, 8))
        n1 = r.randint(1, corte - 2)
        n2 = r.randint(1, corte - 1 - n1)
        parcelas, sinais = [(n1, corte), (n2, corte)], ["+"]
    else:
        corte = r.choice((4, 6, 8))
        n1 = r.randint(2, corte)
        n2 = r.randint(corte - n1 + 1, corte)  # a soma passa de uma pizza inteira
        parcelas, sinais = [(n1, corte), (n2, corte)], ["+"]
    certo = resultado_fracao(parcelas, sinais)
    valores = [certo, *_distratores(certo, parcelas, sinais)]
    r.shuffle(valores)
    return Rodada(nivel, corte, parcelas, certo, [_cartao(v) for v in valores], sinais=sinais)


def _distratores(certo: Fracao, parcelas: list[Fracao], sinais: list[str]) -> list[Fracao]:
    """Dois cartões errados com erros comuns: somar os denominadores (só soma) ou trocar a
    operação (com subtração), e trocar numerador com denominador (ou uma fatia a mais)."""
    if "-" in sinais:
        primeiro = resultado_fracao(parcelas, ["+"] * len(sinais))
    else:
        primeiro = (certo[0], sum(d for _, d in parcelas))
    invertido = (certo[1], certo[0])
    segundo = invertido if invertido not in (certo, primeiro) else (certo[0] + 1, certo[1])
    return [primeiro, segundo]


def conferir_montar(rodada: Rodada, escolhidas: int) -> str | None:
    return None if escolhidas == rodada.certo[0] else "contou_fatias_errado"


def conferir_soma(rodada: Rodada, resposta: Fracao) -> str | None:
    return classificar_fracao(resposta, rodada.parcelas, rodada.sinais or None)
