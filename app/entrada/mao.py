"""Lógica pura da mão: filtro One Euro, área ativa e pinça com histerese.

Não importa Qt nem OpenCV, para ser testada por completo. A permanência entra na Etapa 2.
Os pontos seguem a numeração do MediaPipe: 0 = punho, 4 = ponta do polegar,
8 = ponta do indicador, 9 = base do dedo médio.
"""

import math
from dataclasses import dataclass

PUNHO, POLEGAR, INDICADOR, BASE_MEDIO = 0, 4, 8, 9

PINCA_FECHA = 0.25
PINCA_ABRE = 0.40
AREA_ATIVA = 0.8
PROPORCAO_QUADRO = 640 / 480


class FiltroUmEuro:
    """Filtro One Euro (Casiez et al., 2012) para um valor escalar."""

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.02, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self._x: float | None = None
        self._dx = 0.0
        self._t: float | None = None

    @staticmethod
    def _alfa(cutoff: float, dt: float) -> float:
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def reiniciar(self) -> None:
        self._x, self._dx, self._t = None, 0.0, None

    def filtrar(self, x: float, t: float) -> float:
        if self._x is None or self._t is None or t <= self._t:
            self._x, self._t = x, t
            return x
        dt = t - self._t
        dx = (x - self._x) / dt
        self._dx += self._alfa(self.d_cutoff, dt) * (dx - self._dx)
        cutoff = self.min_cutoff + self.beta * abs(self._dx)
        self._x += self._alfa(cutoff, dt) * (x - self._x)
        self._t = t
        return self._x


class FiltroPonto:
    """Um filtro One Euro por eixo."""

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.02):
        self.x = FiltroUmEuro(min_cutoff, beta)
        self.y = FiltroUmEuro(min_cutoff, beta)

    def reiniciar(self) -> None:
        self.x.reiniciar()
        self.y.reiniciar()

    def filtrar(self, x: float, y: float, t: float) -> tuple[float, float]:
        return self.x.filtrar(x, t), self.y.filtrar(y, t)


def mapear_area_ativa(x: float, y: float, fracao: float = AREA_ATIVA) -> tuple[float, float]:
    """Mapeia a `fracao` central do quadro para 0..1, travando nas bordas.

    Assim a criança alcança os cantos da tela sem tirar a mão do quadro.
    """
    margem = (1 - fracao) / 2

    def mapear(v: float) -> float:
        return min(1.0, max(0.0, (v - margem) / fracao))

    return mapear(x), mapear(y)


def _distancia(a, b, proporcao: float) -> float:
    return math.hypot((a[0] - b[0]) * proporcao, a[1] - b[1])


def razao_pinca(pontos, proporcao: float = PROPORCAO_QUADRO) -> float:
    """Distância polegar–indicador dividida pelo tamanho da palma (punho até base do médio).

    Dividir pela palma deixa a medida igual com a mão perto ou longe da câmera.
    `proporcao` (largura/altura do quadro) desfaz a distorção das coordenadas normalizadas.
    """
    palma = _distancia(pontos[PUNHO], pontos[BASE_MEDIO], proporcao)
    if palma <= 1e-6:
        return math.inf
    return _distancia(pontos[POLEGAR], pontos[INDICADOR], proporcao) / palma


class DetectorPinca:
    """Pinça com histerese: fecha abaixo de `fecha` e só abre de novo acima de `abre`."""

    def __init__(self, fecha: float = PINCA_FECHA, abre: float = PINCA_ABRE):
        if fecha >= abre:
            raise ValueError("o limite de fechar precisa ser menor que o de abrir")
        self.fecha = fecha
        self.abre = abre
        self.fechada = False

    def atualizar(self, razao: float) -> bool:
        if self.fechada and razao > self.abre:
            self.fechada = False
        elif not self.fechada and razao < self.fecha:
            self.fechada = True
        return self.fechada

    def reiniciar(self) -> None:
        self.fechada = False


@dataclass(frozen=True)
class EstadoMao:
    presente: bool
    x: float = 0.0  # 0..1 na cena inteira
    y: float = 0.0
    razao: float = math.inf
    pinca_fechada: bool = False


class RastreadorMao:
    """Junta filtro, área ativa e pinça: recebe os pontos crus e devolve o estado da mão."""

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.02):
        self.filtro = FiltroPonto(min_cutoff, beta)
        self.pinca = DetectorPinca()

    def atualizar(self, pontos, presente: bool, t: float) -> EstadoMao:
        if not presente or not pontos:
            self.filtro.reiniciar()
            self.pinca.reiniciar()
            return EstadoMao(presente=False)
        ponta = pontos[INDICADOR]
        x, y = mapear_area_ativa(ponta[0], ponta[1])
        x, y = self.filtro.filtrar(x, y, t)
        razao = razao_pinca(pontos)
        return EstadoMao(True, x, y, razao, self.pinca.atualizar(razao))
