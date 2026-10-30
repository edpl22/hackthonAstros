"""Perfis de acessibilidade e a regra de combinação "a opção mais acessível vence".

Lógica pura (sem Qt). Cada perfil pronto é o perfil padrão com alguns campos trocados.
"""

from dataclasses import asdict, dataclass, fields, replace

ENTRADAS = ("ponteiro", "permanencia", "teclado")


@dataclass(frozen=True)
class Perfil:
    velocidade: float = 0.5  # 0 = itens parados; 1 = mais rápido
    max_itens: int = 4  # itens na tela ao mesmo tempo
    escala: float = 1.0  # 1.0 a 2.0
    alto_contraste: bool = False
    paleta_segura: bool = False  # hachuras e símbolos em toda distinção
    audio_auto: bool = False  # lê a instrução sem a criança pedir
    reduzir_movimento: bool = False  # animações com duração 0
    som_celebracao: bool = True
    modo_entrada_preferido: str = "ponteiro"  # ponteiro | permanencia | teclado
    tolerancia_alvo_px: int = 24
    tempo_permanencia_ms: int = 800
    espacamento_letras: float = 0.0  # em "em"
    um_passo_por_vez: bool = False
    rodada_itens: int = 10  # itens por rodada antes de uma pausa
    # Campos que só alguns perfis ligam.
    aviso_troca_atividade: bool = False
    contorno_px: int = 3
    silabas_alternadas: bool = False  # cor e sublinhado alternados
    resposta_por_escolha: bool = False
    varredura_disponivel: bool = False
    descrever_foco: bool = False
    miniatura_camera: bool = True

    def como_dict(self) -> dict:
        return asdict(self)


PADRAO = Perfil()

PERFIS: dict[str, Perfil] = {
    "padrao": PADRAO,
    "tea": replace(
        PADRAO,
        velocidade=0.0,
        max_itens=3,
        som_celebracao=False,
        aviso_troca_atividade=True,
        miniatura_camera=False,
    ),
    "tdah": replace(PADRAO, um_passo_por_vez=True, max_itens=3, rodada_itens=5),
    "dislexia": replace(
        PADRAO,
        audio_auto=True,
        espacamento_letras=0.12,
        escala=1.2,
        silabas_alternadas=True,
        resposta_por_escolha=True,
    ),
    "baixa_visao": replace(PADRAO, escala=1.75, alto_contraste=True, contorno_px=5, max_itens=3),
    "daltonismo": replace(PADRAO, paleta_segura=True),
    "motor": replace(
        PADRAO,
        modo_entrada_preferido="permanencia",
        tolerancia_alvo_px=60,
        tempo_permanencia_ms=1200,
        varredura_disponivel=True,
    ),
    "cegueira": replace(
        PADRAO, audio_auto=True, descrever_foco=True, modo_entrada_preferido="teclado"
    ),
}

# Como cada campo combina. "Mais acessível" = menos estímulo, mais tamanho, mais tempo, mais ajuda.
MENOR_VENCE = ("velocidade", "max_itens", "rodada_itens")
MAIOR_VENCE = (
    "escala",
    "tolerancia_alvo_px",
    "tempo_permanencia_ms",
    "espacamento_letras",
    "contorno_px",
)
FALSO_VENCE = ("som_celebracao", "miniatura_camera")  # desligar é o mais acessível
# Os demais campos booleanos: True vence.
# Entrada: teclado atende cegueira; permanência atende motor; ponteiro é o padrão.
PRIORIDADE_ENTRADA = ("teclado", "permanencia", "ponteiro")

REGRAS = {
    "menor vence": list(MENOR_VENCE),
    "maior vence": list(MAIOR_VENCE),
    "False vence": list(FALSO_VENCE),
    "True vence": [
        f.name
        for f in fields(Perfil)
        if f.type in (bool, "bool") and f.name not in FALSO_VENCE
    ],
    "modo_entrada_preferido": "primeiro da lista: " + ", ".join(PRIORIDADE_ENTRADA),
    "escala": "limitada entre 1.0 e 2.0",
}


def nomes_validos() -> list[str]:
    return list(PERFIS)


def ler_lista(texto: str | None) -> list[str]:
    """Converte "tea, dislexia" em ["tea", "dislexia"]; erro claro para nome desconhecido."""
    nomes = [n.strip() for n in (texto or "").split(",") if n.strip()]
    desconhecidos = [n for n in nomes if n not in PERFIS]
    if desconhecidos:
        raise ValueError(
            f"perfil desconhecido: {', '.join(desconhecidos)}. Validos: {', '.join(PERFIS)}"
        )
    return nomes


def combinar(nomes) -> Perfil:
    """Combina perfis pela regra "a opção mais acessível vence". Lista vazia = padrão."""
    perfis = [PERFIS[n] for n in nomes] or [PADRAO]
    valores = {}
    for campo in fields(Perfil):
        nome = campo.name
        lista = [getattr(p, nome) for p in perfis]
        if nome in MENOR_VENCE:
            valores[nome] = min(lista)
        elif nome in MAIOR_VENCE:
            valores[nome] = max(lista)
        elif nome in FALSO_VENCE:
            valores[nome] = all(lista)
        elif nome == "modo_entrada_preferido":
            valores[nome] = min(lista, key=PRIORIDADE_ENTRADA.index)
        else:
            valores[nome] = any(lista)
    valores["escala"] = min(2.0, max(1.0, valores["escala"]))
    return Perfil(**valores)
