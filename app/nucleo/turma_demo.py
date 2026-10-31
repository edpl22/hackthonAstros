"""Turma de demonstração: 6 alunos fictícios com tentativas geradas (sempre as mesmas).

Os dados são inventados para mostrar o painel e estão rotulados assim na tela
("Turma de demonstração"). Nada aqui vem de uma criança de verdade.
"""

import random

from app.nucleo.registro import Tentativa

NOME_TURMA = "Turma de demonstração"

# apelido, bicho, perfis e, por habilidade, (chance de acerto na 1ª tentativa, erro típico)
ALUNOS = [
    ("Ana", "gato", ["dislexia"], {
        "formar palavras com sílabas": (0.7, "ordem_trocada"),
        "somar frações de mesmo denominador": (0.25, "somou_denominadores"),
    }),
    ("Beto", "cachorro", [], {
        "formar palavras com sílabas": (0.95, "silaba_de_outra_palavra"),
        "somar e subtrair": (0.9, "um_a_mais_ou_menos"),
    }),
    ("Caio", "peixe", ["tdah"], {
        "formar palavras com sílabas": (0.3, "par_surdo_sonoro"),
        "somar e subtrair": (0.65, "chute"),
    }),
    ("Duda", "passaro", ["tea"], {
        "formar palavras com sílabas": (0.75, "ordem_trocada"),
        "comparar quantidades": (0.85, "comparacao_errada"),
    }),
    ("Edu", "sapo", ["baixa_visao"], {
        "somar e subtrair": (0.35, "digitos_invertidos"),
        "comparar quantidades": (0.7, "comparacao_errada"),
    }),
    ("Fê", "tartaruga", ["motor"], {
        "formar palavras com sílabas": (0.9, "ordem_trocada"),
        "somar frações de mesmo denominador": (0.85, "contou_fatias_errado"),
    }),
]
ATIVIDADE = {
    "formar palavras com sílabas": "silabas",
    "somar e subtrair": "quantidades",
    "comparar quantidades": "quantidades",
    "somar frações de mesmo denominador": "pizza",
}


def criar(registro, semente: int = 2026, itens: int = 10) -> None:
    """Cria os alunos e as tentativas da turma de demonstração no registro."""
    aleatorio = random.Random(semente)
    registro.salvar_config("nome_turma", NOME_TURMA)
    for apelido, bicho, perfis, habilidades in ALUNOS:
        registro.salvar_aluno(apelido, bicho, perfis)
        for habilidade, (chance, erro) in habilidades.items():
            for n in range(itens):
                item = f"{ATIVIDADE[habilidade]}-{n + 1}"
                pistas = 0
                while True:
                    acertou = aleatorio.random() < (chance if pistas == 0 else 0.6)
                    if not acertou:
                        pistas += 1
                    modelo = pistas >= 3
                    registro.salvar_tentativa(Tentativa(
                        aluno=apelido, atividade=ATIVIDADE[habilidade], habilidade=habilidade,
                        item=item, resposta="", correta=acertou or modelo,
                        tipo_erro=None if acertou else erro, pistas=pistas,
                        precisou_modelo=modelo, tempo_ms=aleatorio.randint(1800, 9000),
                        modo_entrada=aleatorio.choice(["mouse", "camera", "teclado"]),
                        perfis=perfis, ts="2026-10-30T10:00:00",
                    ))
                    if acertou or modelo:
                        break
