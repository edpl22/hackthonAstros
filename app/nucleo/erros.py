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


# --- Pizza de Frações -----------------------------------------------------------------


def classificar_fracao(
    resposta: tuple[int, int], parcelas: list[tuple[int, int]]
) -> str | None:
    """Soma de frações de mesmo denominador. Frações como (numerador, denominador)."""
    denominador = parcelas[0][1]
    certo = (sum(n for n, _ in parcelas), denominador)
    if resposta == certo:
        return None
    if resposta == (sum(n for n, _ in parcelas), sum(d for _, d in parcelas)):
        return "somou_denominadores"
    if resposta == (certo[1], certo[0]):
        return "confundiu_numerador_denominador"
    if resposta[1] == denominador:
        return "contou_fatias_errado"
    if resposta[1] and Fraction(*resposta) == Fraction(*certo):
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
