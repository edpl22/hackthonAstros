"""Regras puras da Mesa de Quantidades.

Níveis (o objetivo é o mesmo, muda a pergunta):
1 = Montar: colocar N objetos na bandeja e tocar em "Pronto";
2 = Comparar: as duas bandejas ligadas uma a uma; a da esquerda é maior, menor ou igual?
3 = Resolver: soma até 10, escolhendo entre 3 cartões;
4 = Resolver: soma ou subtração até 20.
"""

import random
from dataclasses import dataclass, field

from app.nucleo.conteudo import carregar
from app.nucleo.erros import classificar_quantidade

MONTAR, COMPARAR, SOMA, CONTAS = 1, 2, 3, 4
NIVEL_MAXIMO = 4
COMPARACOES = ("maior", "menor", "igual")

NUMEROS = (
    "zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
    "onze", "doze", "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito",
    "dezenove", "vinte",
)


@dataclass(frozen=True)
class Conjunto:
    id: str
    singular: str
    plural: str
    feminino: bool
    figura: str


@dataclass(frozen=True)
class Cartao:
    id: str
    rotulo: str
    valor: str  # número ("7") ou comparação ("maior")


@dataclass
class Rodada:
    nivel: int
    a: int  # bandeja da esquerda (ou meta, no Montar)
    b: int  # bandeja da direita
    operacao: str | None  # "+", "-" ou None
    certo: str
    cartoes: list[Cartao] = field(default_factory=list)
    concluida: bool = False

    @property
    def montar(self) -> bool:
        return self.nivel == MONTAR


def conjuntos() -> list[Conjunto]:
    return [Conjunto(**c) for c in carregar("objetos.json")]


def conjunto(id_conjunto: str) -> Conjunto:
    return next(c for c in conjuntos() if c.id == id_conjunto)


def numero_por_extenso(n: int, feminino: bool = False) -> str:
    if feminino and n in (1, 2):
        return ("uma", "duas")[n - 1]
    return NUMEROS[n]


def quantidade(n: int, c: Conjunto) -> str:
    """"três maçãs", "um peixe", "nenhuma bolinha de gude"."""
    if n == 0:
        return f"{'nenhuma' if c.feminino else 'nenhum'} {c.singular}"
    return f"{numero_por_extenso(n, c.feminino)} {c.singular if n == 1 else c.plural}"


def comparar(a: int, b: int) -> str:
    return "maior" if a > b else "menor" if a < b else "igual"


def _cartoes_de_conta(a: int, b: int, operacao: str, certo: int, r: random.Random) -> list[int]:
    """O certo e dois errados que dizem algo: operação trocada, dígitos invertidos, um a mais."""
    opcoes = [certo]
    trocada = a - b if operacao == "+" else a + b
    invertido = int(str(certo)[::-1]) if certo >= 10 else None
    for candidato in (trocada, invertido, certo + 1, certo - 1, certo + 2):
        if candidato is not None and 0 <= candidato <= 99 and candidato not in opcoes:
            opcoes.append(candidato)
        if len(opcoes) == 3:
            break
    r.shuffle(opcoes)
    return opcoes


def nova_rodada(nivel: int, semente: int | None = None, max_itens: int = 4) -> Rodada:
    r = random.Random(semente)
    pequeno = max_itens <= 3  # perfis com menos itens: quantidades menores
    if nivel == MONTAR:
        meta = r.randint(2, 5 if pequeno else 7)
        pronto = Cartao("cartao-pronto", "Pronto", "pronto")
        return Rodada(nivel, meta, 0, None, str(meta), [pronto])
    if nivel == COMPARAR:
        a, b = r.randint(1, 5 if pequeno else 7), r.randint(1, 5 if pequeno else 7)
        cartoes = [Cartao(f"cartao-{c}", c, c) for c in COMPARACOES]
        return Rodada(nivel, a, b, None, comparar(a, b), cartoes)
    if nivel == SOMA:
        a, b = r.randint(1, 5), r.randint(1, 5)
        operacao = "+"
    else:
        operacao = r.choice("+-")
        if operacao == "+":
            a, b = r.randint(3, 10), r.randint(3, 10)
        else:
            a = r.randint(5, 12)
            b = r.randint(1, a - 1)
    certo = a + b if operacao == "+" else a - b
    valores = _cartoes_de_conta(a, b, operacao, certo, r)
    cartoes = [Cartao(f"cartao-{v}", str(v), str(v)) for v in valores]
    return Rodada(nivel, a, b, operacao, str(certo), cartoes)


def conferir(rodada: Rodada, resposta: str, tempo_ms: int, contados: int = 0) -> str | None:
    """Tipo de erro da resposta (None = certo). No Montar, a resposta é a quantidade posta."""
    if rodada.montar:
        return classificar_quantidade(contados, rodada.a, rodada.a, 0, "+", tempo_ms)
    if rodada.nivel == COMPARAR:
        return None if resposta == rodada.certo else "comparacao_errada"
    return classificar_quantidade(
        int(resposta), int(rodada.certo), rodada.a, rodada.b, rodada.operacao, tempo_ms
    )


def sinal(operacao: str) -> str:
    return "−" if operacao == "-" else "+"
