"""Regras puras do Jogo Dourado.

Um número aparece na tela e a criança o representa com as peças do material dourado:
cubo grande = milhar (1000), placa = centena (100), barra = dezena (10) e cubinho = unidade (1).
Nível 1: até 99 (barras e cubinhos); nível 2: até 999 (+ placas); nível 3: até 9999 (+ cubo).
Cada pilha tem 9 peças, então a única representação certa é a de cada algarismo.
"""

import random
from dataclasses import dataclass, field

ORDENS = ("milhar", "centena", "dezena", "unidade")  # da maior para a menor
VALOR = {"milhar": 1000, "centena": 100, "dezena": 10, "unidade": 1}
PECAS_POR_PILHA = 9
NIVEL_MAXIMO = 3
FAIXAS = {1: (11, 99), 2: (101, 999), 3: (1001, 9999)}


@dataclass
class Rodada:
    nivel: int
    numero: int
    na_mesa: dict[str, int] = field(default_factory=lambda: dict.fromkeys(ORDENS, 0))
    concluida: bool = False

    @property
    def ordens(self) -> tuple[str, ...]:
        """Pilhas que aparecem no nível: dezena e unidade; depois centena; depois milhar."""
        return ORDENS[3 - self.nivel:]

    @property
    def total(self) -> int:
        return valor(self.na_mesa)


def algarismos(numero: int) -> dict[str, int]:
    """1234 -> {"milhar": 1, "centena": 2, "dezena": 3, "unidade": 4}."""
    return {ordem: numero // VALOR[ordem] % 10 for ordem in ORDENS}


def valor(contagem: dict[str, int]) -> int:
    return sum(VALOR[o] * n for o, n in contagem.items())


def texto_numero(numero: int) -> str:
    """Separador de milhar como na escola: 1234 -> "1.234"."""
    return f"{numero:,}".replace(",", ".")


def nova_rodada(nivel: int, semente: int | None = None, anterior: int | None = None) -> Rodada:
    """Sorteia um número da faixa do nível sem algarismo zero no meio dos primeiros níveis,
    para cada pilha ser usada pelo menos uma vez; o nível 3 aceita zeros (1.050)."""
    r = random.Random(semente)
    menor, maior = FAIXAS[nivel]
    while True:
        numero = r.randint(menor, maior)
        tem_zero = 0 in [algarismos(numero)[o] for o in ORDENS[3 - nivel:]]
        if numero != anterior and (nivel == 3 or not tem_zero):
            return Rodada(nivel, numero)


def ordens_erradas(rodada: Rodada) -> list[str]:
    certo = algarismos(rodada.numero)
    return [o for o in ORDENS if rodada.na_mesa[o] != certo[o]]
