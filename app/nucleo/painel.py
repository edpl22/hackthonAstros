"""Regras puras do painel do professor.

Para cada aluno e habilidade, olha os últimos 10 itens (um item = as tentativas seguidas na
mesma pergunta):
- Domina: 80% ou mais dos itens certos na 1ª tentativa;
- Precisa de apoio: menos de 50% certos na 1ª tentativa, ou 2 ou mais itens com o modelo;
- Em progresso: o resto.
Para quem precisa de apoio, o tipo de erro mais frequente vira uma frase de recomendação.
"""

from collections import Counter
from dataclasses import dataclass

from app.nucleo.erros import frase_para_professor

DOMINA, EM_PROGRESSO, PRECISA_APOIO = "domina", "em_progresso", "precisa_apoio"
JANELA = 10


@dataclass(frozen=True)
class Situacao:
    estado: str
    itens: int
    certos_primeira: int
    modelos: int
    tipo_erro: str | None  # o mais frequente na janela
    vezes: int  # tentativas com esse erro
    tentativas: int  # tentativas na janela

    @property
    def taxa(self) -> float:
        return self.certos_primeira / self.itens if self.itens else 0.0


def agrupar_itens(tentativas: list[dict]) -> list[list[dict]]:
    """Tentativas seguidas no mesmo item formam um item."""
    itens: list[list[dict]] = []
    for t in tentativas:
        if itens and itens[-1][-1]["item"] == t["item"] and not itens[-1][-1]["correta"]:
            itens[-1].append(t)
        else:
            itens.append([t])
    return itens


def situacao(tentativas: list[dict]) -> Situacao:
    """Tentativas de um aluno numa habilidade, em ordem."""
    itens = agrupar_itens(tentativas)[-JANELA:]
    certos = sum(item[0]["correta"] for item in itens)
    modelos = sum(any(t["precisou_modelo"] for t in item) for item in itens)
    janela = [t for item in itens for t in item]
    erros = Counter(t["tipo_erro"] for t in janela if t["tipo_erro"])
    tipo, vezes = erros.most_common(1)[0] if erros else (None, 0)
    taxa = certos / len(itens) if itens else 0.0
    if taxa < 0.5 or modelos >= 2:
        estado = PRECISA_APOIO
    elif taxa >= 0.8:
        estado = DOMINA
    else:
        estado = EM_PROGRESSO
    return Situacao(estado, len(itens), certos, modelos, tipo, vezes, len(janela))


def grade(tentativas: list[dict]) -> tuple[list[str], list[str], dict]:
    """(alunos, habilidades, {(aluno, habilidade): Situacao}) na ordem em que aparecem."""
    alunos = list(dict.fromkeys(t["aluno"] for t in tentativas))
    habilidades = list(dict.fromkeys(t["habilidade"] for t in tentativas))
    celulas = {}
    for aluno in alunos:
        for habilidade in habilidades:
            lista = [t for t in tentativas if t["aluno"] == aluno and t["habilidade"] == habilidade]
            if lista:
                celulas[(aluno, habilidade)] = situacao(lista)
    return alunos, habilidades, celulas


def recomendacoes(celulas: dict) -> list[str]:
    frases = []
    for (aluno, habilidade), s in celulas.items():
        if s.estado == PRECISA_APOIO and s.tipo_erro:
            frase = frase_para_professor(aluno, s.tipo_erro, s.vezes, s.tentativas)
            frases.append(f"{habilidade.capitalize()}: {frase}")
    return frases
