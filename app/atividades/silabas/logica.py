"""Regras puras do Ímã das Sílabas.

Níveis: 1 e 2 = palavras de 2 e 3 sílabas simples, distratoras de outras palavras;
3 = sílabas com encontro consonantal (BRA, PRA, VRO), distratoras do par surdo/sonoro
(B-P, T-D, F-V, C-G), em letra minúscula; 4 = "Qual bolha é a mais forte?" (sílaba tônica).
"""

import random
import unicodedata
from dataclasses import dataclass, field

from app.nucleo.conteudo import carregar
from app.nucleo.erros import PARES_SURDO_SONORO, classificar_silaba

NIVEL_MAXIMO = 4
NIVEL_TONICA = 4
NIVEL_MINUSCULA = 3


@dataclass(frozen=True)
class Palavra:
    id: str
    texto: str
    silabas: tuple[str, ...]
    fala_palavra: str
    fala_silabas: tuple[str, ...]
    tonica: int
    nivel: int
    figura: str


@dataclass(frozen=True)
class Bolha:
    id: str
    silaba: str
    posicao: int | None  # posição na palavra; None = distratora


@dataclass
class Rodada:
    palavra: Palavra
    nivel: int
    bolhas: list[Bolha]
    colocadas: dict[int, str] = field(default_factory=dict)  # posição -> sílaba
    tonica_escolhida: bool = False

    @property
    def tonica(self) -> bool:
        return self.nivel >= NIVEL_TONICA

    @property
    def concluida(self) -> bool:
        if self.tonica:
            return self.tonica_escolhida
        return len(self.colocadas) == len(self.palavra.silabas)

    def proxima_posicao(self) -> int | None:
        if self.tonica:
            return None if self.tonica_escolhida else self.palavra.tonica
        livres = [i for i in range(len(self.palavra.silabas)) if i not in self.colocadas]
        return livres[0] if livres else None

    def bolha_da_posicao(self, posicao: int) -> Bolha:
        return next(b for b in self.bolhas if b.posicao == posicao)


def carregar_palavras() -> list[Palavra]:
    return [
        Palavra(
            p["id"], p["texto"], tuple(p["silabas"]), p["fala"]["palavra"],
            tuple(p["fala"]["silabas"]), p["tonica"], p["nivel"], p["figura"],
        )
        for p in carregar("palavras.json")
    ]


def palavra(id_palavra: str) -> Palavra:
    return next(p for p in carregar_palavras() if p.id == id_palavra)


def palavras_do_nivel(nivel: int) -> list[Palavra]:
    todas = carregar_palavras()
    if nivel >= NIVEL_TONICA:
        return todas  # a tônica é perguntada nas mesmas palavras dos níveis 1 a 3
    return [p for p in todas if p.nivel == nivel]


def slug(silaba: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", silaba.lower()).encode("ascii", "ignore")
    return sem_acento.decode()


def trocar_par(silaba: str) -> str | None:
    """BO -> PO, PRA -> BRA, VRO -> FRO. None se a primeira letra não tem par."""
    par = PARES_SURDO_SONORO.get(silaba[:1].upper())
    return par + silaba[1:] if par else None


def distratoras(alvo: Palavra, quantidade: int, nivel: int, aleatorio: random.Random) -> list[str]:
    if quantidade <= 0:
        return []
    proprias = {s.upper() for s in alvo.silabas}
    candidatas: list[str] = []
    if nivel >= NIVEL_MINUSCULA:
        pares = [trocar_par(s) for s in alvo.silabas]
        candidatas += [p for p in pares if p and p.upper() not in proprias]
        aleatorio.shuffle(candidatas)
    outras = sorted(
        {s for p in carregar_palavras() if p.id != alvo.id for s in p.silabas}
        - proprias
        - set(candidatas)
    )
    aleatorio.shuffle(outras)
    candidatas += outras
    escolhidas: list[str] = []
    for c in candidatas:
        if c not in escolhidas:
            escolhidas.append(c)
        if len(escolhidas) == quantidade:
            break
    return escolhidas


def nova_rodada(
    nivel: int, max_itens: int, semente: int | None = None, id_palavra: str | None = None,
    anterior: str | None = None,
) -> Rodada:
    aleatorio = random.Random(semente)
    if id_palavra:
        alvo = palavra(id_palavra)
    else:
        opcoes = [p for p in palavras_do_nivel(nivel) if p.id != anterior]
        alvo = aleatorio.choice(opcoes)
    n = len(alvo.silabas)
    extras = 0 if nivel >= NIVEL_TONICA else max(0, max_itens - n)
    silabas = [(s, i) for i, s in enumerate(alvo.silabas)]
    silabas += [(s, None) for s in distratoras(alvo, extras, nivel, aleatorio)]
    ordem = list(range(len(silabas)))
    for _ in range(10):  # embaralha sem deixar a palavra já montada na ordem certa
        aleatorio.shuffle(ordem)
        if [silabas[k][1] for k in ordem][:n] != list(range(n)):
            break
    bolhas = [
        Bolha(f"bolha-{slug(silabas[k][0])}-{i}", silabas[k][0], silabas[k][1])
        for i, k in enumerate(ordem)
    ]
    return Rodada(alvo, nivel, bolhas)


def conferir(rodada: Rodada, posicao: int, silaba: str) -> str | None:
    """Tipo de erro ao soltar `silaba` na caixa `posicao` (None = certo)."""
    return classificar_silaba(list(rodada.palavra.silabas), posicao, silaba)


def conferir_tonica(rodada: Rodada, bolha: Bolha) -> str | None:
    return None if bolha.posicao == rodada.palavra.tonica else "tonica_errada"


def fala_distratora(silaba: str) -> str:
    """Como a voz lê uma sílaba que não é da palavra (sem acento de palavra): "PO" -> "po"."""
    return silaba.lower()


def fala_da_bolha(rodada: Rodada, bolha: Bolha) -> str:
    if bolha.posicao is None:
        return fala_distratora(bolha.silaba)
    return rodada.palavra.fala_silabas[bolha.posicao]


def rotulo(silaba: str, nivel: int) -> str:
    """Letra bastão nos níveis iniciais; minúscula a partir do nível 3."""
    return silaba.lower() if nivel == NIVEL_MINUSCULA else silaba


def id_caixa(posicao: int) -> str:
    return f"caixa-{posicao + 1}"
