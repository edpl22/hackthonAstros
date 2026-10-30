"""Regras puras do treino de arrastar: cada peça com uma letra vai para a caixa da mesma letra."""

import random
from dataclasses import dataclass, field

LETRAS = "ABCD"


@dataclass
class Rodada:
    letras: list[str]  # letra de cada caixa, na ordem das caixas
    ordem_pecas: list[int]  # posição de cada peça na fila de cima (embaralhada)
    colocadas: set[str] = field(default_factory=set)

    @property
    def concluida(self) -> bool:
        return len(self.colocadas) == len(self.letras)

    def proxima_letra(self) -> str | None:
        return next((letra for letra in self.letras if letra not in self.colocadas), None)


def nova_rodada(max_itens: int, semente: int | None = None) -> Rodada:
    n = max(2, min(max_itens, len(LETRAS)))
    letras = list(LETRAS[:n])
    ordem = list(range(n))
    aleatorio = random.Random(semente)
    while ordem == sorted(ordem):  # nunca deixa cada peça já em cima da sua caixa
        aleatorio.shuffle(ordem)
    return Rodada(letras, ordem)


def id_peca(letra: str, indice: int) -> str:
    return f"peca-{letra.lower()}-{indice}"


def id_caixa(indice: int) -> str:
    return f"caixa-{indice + 1}"


def confere(letra_peca: str, letra_caixa: str) -> bool:
    return letra_peca == letra_caixa
