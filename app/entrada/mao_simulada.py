"""Mão simulada: reproduz `conteudo/simulacao_mao.json` sem webcam.

O roteiro diz para onde a mão vai e quando faz a pinça. Daqui saem os 21 pontos sintéticos no
mesmo formato do MediaPipe, que passam pelo `mao.py` real (filtro, área ativa, pinça).
Assim o caminho da câmera é demonstrado e testado sem câmera.
"""

from app.entrada.mao import (
    AREA_ATIVA,
    BASE_MEDIO,
    DEDOS_DOBRADOS,
    INDICADOR,
    JUNTA_INDICADOR,
    POLEGAR,
    PUNHO,
)
from app.nucleo.conteudo import carregar

FPS = 30


def pontos_sinteticos(
    x_cena: float, y_cena: float, pinca: bool, arminha: bool = False, dedao_abaixado=False
) -> list[tuple]:
    """21 pontos de uma mão apontando, com a ponta do indicador sobre (x_cena, y_cena) 0..1.
    Com `arminha`, médio, anelar e mínimo ficam dobrados (ponta perto da palma) e o dedão fica
    levantado, ou encostado na lateral do indicador com `dedao_abaixado` (o tiro)."""
    margem = (1 - AREA_ATIVA) / 2
    fx = margem + x_cena * AREA_ATIVA  # inverso da área ativa
    fy = margem + y_cena * AREA_ATIVA
    pontos = [(fx, fy + 0.20, 0.0)] * 21
    pontos[PUNHO] = (fx, fy + 0.30, 0.0)
    pontos[BASE_MEDIO] = (fx, fy + 0.15, 0.0)
    pontos[INDICADOR] = (fx, fy, 0.0)
    pontos[POLEGAR] = (fx + 0.005, fy + 0.005, 0.0) if pinca else (fx - 0.08, fy + 0.06, 0.0)
    if arminha:
        pontos[JUNTA_INDICADOR] = (fx, fy + 0.08, 0.0)
        for junta, ponta in DEDOS_DOBRADOS:
            pontos[junta] = (fx + 0.02, fy + 0.12, 0.0)
            pontos[ponta] = (fx + 0.02, fy + 0.20, 0.0)
        pontos[POLEGAR] = (fx - 0.01, fy + 0.09, 0.0) if dedao_abaixado else (fx - 0.10, fy, 0.0)
    return pontos


def quadros(passos, centro_normalizado, x0: float = 0.5, y0: float = 0.5):
    """Gera (t, pontos) a 30 quadros/s a partir dos passos do roteiro.

    Passos: {"ir_para": "<id>", "ms": 600}, {"pinca": true|false, "ms": 200}, {"esperar": 300},
    {"arminha": true} (forma a arminha, dedão levantado) e {"disparar": true} (abaixa o dedão
    por 100 ms e levanta de novo).
    `centro_normalizado(id)` devolve o centro do item ou alvo em 0..1 da cena.
    """
    x, y, pinca, arminha, t = x0, y0, False, False, 0.0
    passo_t = 1 / FPS
    for passo in passos:
        if "arminha" in passo:
            arminha = bool(passo["arminha"])
            continue
        if "disparar" in passo:  # o indicador fica parado; só o dedão desce e sobe
            for abaixado in (True, True, True, False, False, False):
                t += passo_t
                yield t, pontos_sinteticos(x, y, pinca, arminha, abaixado)
            continue
        if "ir_para" in passo:
            destino = centro_normalizado(passo["ir_para"])
            n = max(1, round(passo.get("ms", 600) / 1000 * FPS))
            x_ini, y_ini = x, y
            for i in range(1, n + 1):
                f = i / n
                x, y = x_ini + (destino[0] - x_ini) * f, y_ini + (destino[1] - y_ini) * f
                t += passo_t
                yield t, pontos_sinteticos(x, y, pinca, arminha)
        else:
            if "pinca" in passo:
                pinca = bool(passo["pinca"])
            n = max(1, round(passo.get("ms", passo.get("esperar", 200)) / 1000 * FPS))
            for _ in range(n):
                t += passo_t
                yield t, pontos_sinteticos(x, y, pinca, arminha)


def roteiro(nome: str) -> list[dict]:
    return carregar("simulacao_mao.json")[nome]


_relogio = {"t": 0.0}  # o tempo só anda para frente entre reproduções


def reproduzir(entrada_mao, cena, nome_roteiro: str | None = None, passos=None) -> int:
    """Executa um roteiro (pelo nome no JSON ou pela lista de passos) na hora, sem esperar
    o relógio. Devolve o número de quadros."""
    area = cena.sceneRect()

    def centro_normalizado(id_alvo):
        cx, cy = cena.centro(id_alvo)
        return (cx - area.left()) / area.width(), (cy - area.top()) / area.height()

    estado = entrada_mao.ultimo_estado
    x0, y0 = (estado.x, estado.y) if estado is not None and estado.presente else (0.5, 0.5)
    inicio = _relogio["t"]
    total = 0
    for t, pontos in quadros(passos or roteiro(nome_roteiro), centro_normalizado, x0, y0):
        entrada_mao.receber(pontos, True, inicio + t)
        _relogio["t"] = inicio + t
        total += 1
    return total
