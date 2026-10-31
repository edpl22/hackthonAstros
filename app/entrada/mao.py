"""Lógica pura da mão: filtro One Euro, área ativa, pinça com histerese, permanência e o
gesto de arminha com disparo (Tabuada Protetora).

Não importa Qt nem OpenCV, para ser testada por completo.
Os pontos seguem a numeração do MediaPipe: 0 = punho, 4 = ponta do polegar,
8 = ponta do indicador, 9 = base do dedo médio.
"""

import math
from dataclasses import dataclass

PUNHO, POLEGAR, INDICADOR, BASE_MEDIO = 0, 4, 8, 9
JUNTA_INDICADOR = 6
# (junta do meio, ponta) do médio, anelar e mínimo
DEDOS_DOBRADOS = ((10, 12), (14, 16), (18, 20))

DISPARO_SUBIDA = 0.12  # a ponta do indicador sobe 12% da altura da área ativa...
DISPARO_JANELA_S = 0.2  # ...em até 200 ms
DISPARO_INTERVALO_S = 0.6  # depois de um disparo, espera antes do próximo

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


def eh_arminha(pontos, proporcao: float = PROPORCAO_QUADRO) -> bool:
    """Indicador esticado e médio, anelar e mínimo dobrados (o polegar pode estar como for).

    Esticado: a ponta fica bem mais longe do punho que a junta do meio; dobrado: a ponta
    fica mais perto do punho que a junta do meio.
    """
    punho = pontos[PUNHO]

    def ate_punho(i):
        return _distancia(pontos[i], punho, proporcao)

    esticado = ate_punho(INDICADOR) > 1.1 * ate_punho(JUNTA_INDICADOR)
    dobrados = all(ate_punho(ponta) < ate_punho(junta) for junta, ponta in DEDOS_DOBRADOS)
    return esticado and dobrados


class DetectorDisparo:
    """Dispara quando, em arminha, a ponta do indicador sobe rápido (o "coice" do tiro).

    A mira é o ponto onde a mão estava antes do coice, para o tiro sair onde a criança mirou.
    """

    def __init__(
        self, subida: float = DISPARO_SUBIDA, janela_s: float = DISPARO_JANELA_S,
        intervalo_s: float = DISPARO_INTERVALO_S,
    ):
        self.subida, self.janela_s, self.intervalo_s = subida, janela_s, intervalo_s
        self._historico: list[tuple[float, float, float, float]] = []  # (t, y bruto, x, y)
        self._ultimo = -math.inf

    def reiniciar(self) -> None:
        self._historico = []

    def atualizar(
        self, t: float, y_bruto: float, mira: tuple[float, float], arminha: bool
    ) -> tuple[float, float] | None:
        """`y_bruto`: altura da ponta do indicador (0 = topo do quadro), sem filtro.
        Devolve a mira (x, y) quando dispara; senão None."""
        if not arminha:
            self.reiniciar()
            return None
        self._historico = [h for h in self._historico if t - h[0] <= self.janela_s]
        self._historico.append((t, y_bruto, *mira))
        if t - self._ultimo < self.intervalo_s:
            return None
        mais_baixo = max(self._historico, key=lambda h: h[1])
        if mais_baixo[1] - y_bruto >= self.subida and mais_baixo[0] < t:
            self._ultimo = t
            self.reiniciar()
            return mais_baixo[2], mais_baixo[3]
        return None


class DetectorPermanencia:
    """Dispara quando o cursor fica parado sobre um alvo (dentro da tolerância) pelo tempo dado.

    Depois de disparar, só dispara de novo quando o cursor sair da tolerância e voltar,
    para a criança não pegar e soltar sem querer.
    """

    def __init__(self, tolerancia_px: float, tempo_ms: float):
        self.tolerancia_px = tolerancia_px
        self.tempo_ms = tempo_ms
        self.progresso = 0.0  # 0..1, para o anel do cursor
        self._ancora: tuple[float, float] | None = None
        self._inicio = 0.0
        self._armado = True

    def reiniciar(self) -> None:
        self.progresso = 0.0
        self._ancora = None
        self._armado = True

    def atualizar(self, x: float, y: float, t: float, sobre_alvo: bool) -> bool:
        if not sobre_alvo:
            self.reiniciar()
            return False
        if self._ancora is None or math.dist(self._ancora, (x, y)) > self.tolerancia_px:
            self._ancora, self._inicio = (x, y), t
            self.progresso = 0.0
            self._armado = True
            return False
        if not self._armado:
            return False
        self.progresso = min(1.0, (t - self._inicio) * 1000 / self.tempo_ms)
        if self.progresso >= 1.0:
            self._armado = False
            return True
        return False


@dataclass(frozen=True)
class EstadoMao:
    presente: bool
    x: float = 0.0  # 0..1 na cena inteira
    y: float = 0.0
    razao: float = math.inf
    pinca_fechada: bool = False
    arminha: bool = False
    y_bruto: float = 0.0  # ponta do indicador sem filtro (para o disparo)


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
        _, y_bruto = mapear_area_ativa(ponta[0], ponta[1])
        return EstadoMao(
            True, x, y, razao, self.pinca.atualizar(razao), eh_arminha(pontos), y_bruto
        )
