"""Regras puras da Tabuada Protetora.

Cada conta da tabuada vem com monstrinhos numerados: um com o resultado certo e os outros com
erros comuns (somar em vez de multiplicar, vizinho na tabuada). Acertar o certo vale +1 ponto,
acertar um errado vale -1 e não acertar nenhum não muda nada. A partida dura 1 minuto.
"""

import random
from dataclasses import dataclass, field

DURACAO_S = 60
NIVEL_MAXIMO = 2
FATORES = {1: range(1, 6), 2: range(1, 11)}  # nível 1: tabuada do 1 ao 5; nível 2: do 1 ao 10
SEGUNDO_FATOR = range(1, 11)


@dataclass(frozen=True)
class Monstro:
    id: str
    valor: int


@dataclass
class Conta:
    a: int
    b: int
    monstros: list[Monstro]

    @property
    def certo(self) -> int:
        return self.a * self.b

    @property
    def id(self) -> str:
        return f"{self.a}x{self.b}"

    @property
    def texto(self) -> str:
        return f"{self.a} × {self.b}"


@dataclass
class Partida:
    nivel: int
    aleatorio: random.Random
    n_monstros: int
    conta: Conta | None = None
    pontos: int = 0
    restante_s: int = DURACAO_S
    contas_feitas: int = 0
    feitas: set = field(default_factory=set)

    @property
    def acabou(self) -> bool:
        return self.restante_s <= 0


def distratores(a: int, b: int, n: int, aleatorio: random.Random) -> list[int]:
    """Valores errados, primeiro os erros comuns e depois outros da mesma tabuada."""
    certo = a * b
    comuns = [a + b, a * (b + 1), a * (b - 1), (a + 1) * b, (a - 1) * b]
    outros = [a * k for k in range(1, 11)]
    aleatorio.shuffle(outros)
    valores = []
    for v in comuns + outros:
        if v > 0 and v != certo and v not in valores:
            valores.append(v)
    return valores[:n]


def nova_conta(partida: Partida) -> Conta:
    """Sorteia uma conta que ainda não saiu nesta partida (repete só se acabarem)."""
    r = partida.aleatorio
    opcoes = [(a, b) for a in FATORES[partida.nivel] for b in SEGUNDO_FATOR]
    novas = [c for c in opcoes if c not in partida.feitas] or opcoes
    a, b = r.choice(novas)
    partida.feitas.add((a, b))
    valores = [a * b, *distratores(a, b, partida.n_monstros - 1, r)]
    r.shuffle(valores)
    n = partida.contas_feitas
    monstros = [Monstro(f"monstro-{n}-{i}", v) for i, v in enumerate(valores)]
    partida.conta = Conta(a, b, monstros)
    partida.contas_feitas += 1
    return partida.conta


def nova_partida(nivel: int, n_monstros: int, semente: int | None = None) -> Partida:
    partida = Partida(nivel, random.Random(semente), max(2, n_monstros))
    nova_conta(partida)
    return partida


def acertar(partida: Partida, valor: int) -> int:
    """Pontos depois de acertar o monstro com `valor`: +1 se é o resultado, -1 se não é."""
    partida.pontos += 1 if valor == partida.conta.certo else -1
    return partida.pontos


def passar_segundo(partida: Partida) -> bool:
    """Desconta um segundo; devolve True quando o tempo acaba."""
    partida.restante_s = max(0, partida.restante_s - 1)
    return partida.acabou


def relogio(restante_s: int) -> str:
    return f"{restante_s // 60}:{restante_s % 60:02d}"
