"""Classificadores de erro (puros) e a tabela erro -> recomendação para o professor.

Cada função recebe a resposta da criança e o que era esperado e devolve o tipo de erro,
ou None quando a resposta está certa.
"""

from fractions import Fraction

from app.nucleo.conteudo import carregar

LIMITE_CHUTE_MS = 1500
PARES_SURDO_SONORO = {
    "B": "P", "P": "B", "T": "D", "D": "T", "F": "V", "V": "F", "C": "G", "G": "C",
}

# --- treino de arrastar --------------------------------------------------------


def classificar_treino(letra_peca: str, letra_caixa: str) -> str | None:
    return None if letra_peca.upper() == letra_caixa.upper() else "letra_trocada"


# --- Ímã das Sílabas ---------------------------------------------------------------


def eh_par_surdo_sonoro(silaba_a: str, silaba_b: str) -> bool:
    """BO e PO, TA e DA...: mesma sílaba, trocando só a consoante pelo seu par surdo/sonoro."""
    a, b = silaba_a.upper(), silaba_b.upper()
    return (
        len(a) == len(b)
        and a[1:] == b[1:]
        and PARES_SURDO_SONORO.get(a[:1]) == b[:1]
    )


def classificar_silaba(silabas: list[str], posicao: int, colocada: str) -> str | None:
    """`silabas` da palavra, `posicao` da caixa (0 = primeira) e a sílaba que a criança soltou."""
    certa = silabas[posicao]
    if colocada.upper() == certa.upper():
        return None
    if colocada.upper() in (s.upper() for s in silabas):
        return "ordem_trocada"
    if eh_par_surdo_sonoro(colocada, certa):
        return "par_surdo_sonoro"
    return "silaba_de_outra_palavra"


# --- Mesa de Quantidades -------------------------------------------------------------


def classificar_quantidade(
    resposta: int, certo: int, a: int, b: int, operacao: str, tempo_ms: int
) -> str | None:
    """`operacao` é "+" ou "-". Padrões específicos têm prioridade sobre o chute."""
    if resposta == certo:
        return None
    trocada = a - b if operacao == "+" else a + b
    if resposta == trocada:
        return "operacao_trocada"
    if certo >= 10 and str(resposta) == str(certo)[::-1]:
        return "digitos_invertidos"
    if abs(resposta - certo) == 1:
        return "um_a_mais_ou_menos"
    if tempo_ms < LIMITE_CHUTE_MS:
        return "chute"
    return "outro"


# --- Tabuada Protetora ---------------------------------------------------------------


def classificar_tabuada(resposta: int, a: int, b: int) -> str | None:
    """Monstrinho acertado (`resposta`) para a conta a x b."""
    if resposta == a * b:
        return None
    if resposta == a + b:
        return "somou_em_vez_de_multiplicar"
    if resposta in (a * (b + 1), a * (b - 1), (a + 1) * b, (a - 1) * b):
        return "vizinho_na_tabuada"
    return "outro"


# --- Jogo Dourado ---------------------------------------------------------------------


def classificar_dourado(na_mesa: dict[str, int], certo: dict[str, int]) -> str | None:
    """Peças por ordem (milhar, centena, dezena, unidade) na mesa e as do número."""
    if na_mesa == certo:
        return None
    if sorted(na_mesa.values()) == sorted(certo.values()):
        return "trocou_as_ordens"  # 352 montado como 2 centenas, 5 dezenas e 3 unidades
    diferencas = [abs(na_mesa[o] - certo[o]) for o in certo]
    if sorted(diferencas)[-2:] == [0, 1]:
        return "contou_pecas_errado"  # uma ordem com uma peça a mais ou a menos
    return "outro"


# --- Pizza de Frações -----------------------------------------------------------------


def resultado_fracao(parcelas: list[tuple[int, int]], sinais=None) -> tuple[int, int]:
    """Faz a conta com frações de mesmo denominador: sinais[i] liga a parcela i e a i+1."""
    sinais = sinais if sinais is not None else ["+"] * (len(parcelas) - 1)
    numerador = parcelas[0][0]
    for sinal, (n, _) in zip(sinais, parcelas[1:], strict=True):
        numerador += n if sinal == "+" else -n
    return numerador, parcelas[0][1]


def classificar_fracao(
    resposta: tuple[int, int], parcelas: list[tuple[int, int]], sinais=None
) -> str | None:
    """Conta com frações de mesmo denominador (soma e subtração). Frações como (num, den)."""
    sinais = sinais if sinais is not None else ["+"] * (len(parcelas) - 1)
    certo = resultado_fracao(parcelas, sinais)
    denominador = certo[1]
    if resposta == certo:
        return None
    if "+" in sinais and "-" not in sinais and resposta == (
        certo[0], sum(d for _, d in parcelas)
    ):
        return "somou_denominadores"
    if "-" in sinais and resposta == resultado_fracao(parcelas, ["+"] * len(sinais)):
        return "operacao_trocada"
    if resposta == (certo[1], certo[0]):
        return "confundiu_numerador_denominador"
    if resposta[1] == denominador:
        return "contou_fatias_errado"
    if resposta[1] and certo[1] and Fraction(*resposta) == Fraction(*certo):
        return None  # fração equivalente também está certa
    return "outro"


# --- recomendações -----------------------------------------------------------------


def recomendacao(tipo_erro: str) -> dict:
    """{"descricao": "...", "sugestao": "..."} de `conteudo/recomendacoes.json`."""
    tabela = carregar("recomendacoes.json")
    return tabela.get(tipo_erro, tabela["outro"])


def frase_para_professor(apelido: str, tipo_erro: str, vezes: int, total: int) -> str:
    rec = recomendacao(tipo_erro)
    return (
        f"{apelido} {rec['descricao']} em {vezes} de {total} tentativas. "
        f"Sugestão: {rec['sugestao']}"
    )
