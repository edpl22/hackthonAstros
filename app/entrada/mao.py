"""Lógica pura da mão: filtro One Euro, área ativa, pinça com histerese, permanência e o
gesto de arminha com gatilho no dedão (Tabuada Protetora).

Não importa Qt nem OpenCV, para ser testada por completo.
Os pontos seguem a numeração do MediaPipe: 0 = punho, 4 = ponta do polegar,
8 = ponta do indicador, 9 = base do dedo médio.
"""

import math
from dataclasses import dataclass

PUNHO, POLEGAR, INDICADOR, BASE_MEDIO = 0, 4, 8, 9
BASE_INDICADOR, JUNTA_INDICADOR, JUNTA_MEDIO = 5, 6, 10
# (junta do meio, ponta) do médio, anelar e mínimo
DEDOS_DOBRADOS = ((10, 12), (14, 16), (18, 20))

# Gatilho: distância da ponta do dedão até a lateral do indicador, em palmas.
GATILHO_ARMA = 0.5  # dedão levantado (arma engatilhada)
GATILHO_QUEDA = 0.55  # dispara quando cai para 55% do ponto mais alto desde que engatilhou
GATILHO_INTERVALO_S = 0.4  # depois de um tiro, espera antes do próximo
GATILHO_MIRA_S = 0.15  # a mira é onde o indicador estava um pouco antes do dedão descer

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


def _distancia_3d(a, b, proporcao: float) -> float:
    """Como `_distancia`, mas com a profundidade (z do MediaPipe, na escala do x).

    Com o indicador apontado para a tela, ele aparece curto na imagem; a profundidade
    mostra que ele continua esticado.
    """
    za = a[2] if len(a) > 2 else 0.0
    zb = b[2] if len(b) > 2 else 0.0
    return math.hypot((a[0] - b[0]) * proporcao, a[1] - b[1], (za - zb) * proporcao)


def eh_arminha(pontos, proporcao: float = PROPORCAO_QUADRO) -> bool:
    """Indicador esticado e médio, anelar e mínimo dobrados (o polegar pode estar como for).

    Esticado: a ponta fica bem mais longe do punho que a junta do meio; dobrado: a ponta
    fica mais perto do punho que a junta do meio.
    """
    punho = pontos[PUNHO]

    def ate_punho(i):
        return _distancia_3d(pontos[i], punho, proporcao)

    esticado = ate_punho(INDICADOR) > 1.1 * ate_punho(JUNTA_INDICADOR)
    dobrados = all(ate_punho(ponta) < ate_punho(junta) for junta, ponta in DEDOS_DOBRADOS)
    return esticado and dobrados


def razao_gatilho(pontos, proporcao: float = PROPORCAO_QUADRO) -> float:
    """Distância da ponta do dedão até a lateral da mão (base e junta do indicador, base e
    junta do médio), em palmas. Dedão levantado: grande; dedão abaixado: pequena."""
    palma = _distancia_3d(pontos[PUNHO], pontos[BASE_MEDIO], proporcao)
    if palma <= 1e-6:
        return 0.0
    lateral = (BASE_INDICADOR, JUNTA_INDICADOR, BASE_MEDIO, JUNTA_MEDIO)
    dedao = pontos[POLEGAR]
    return min(_distancia_3d(dedao, pontos[i], proporcao) for i in lateral) / palma


class DetectorGatilho:
    """Arminha com gatilho no dedão: engatilha com o dedão levantado e atira quando ele desce.

    Só engatilha em arminha; depois de engatilhado, o tiro sai mesmo que a pose oscile num
    quadro. A queda é medida em relação ao ponto mais alto do dedão, para servir a mãos e
    ângulos de câmera diferentes. O indicador não precisa se mexer, então a mira fica firme.
    """

    def __init__(
        self, arma: float = GATILHO_ARMA, queda: float = GATILHO_QUEDA,
        intervalo_s: float = GATILHO_INTERVALO_S, mira_s: float = GATILHO_MIRA_S,
    ):
        self.arma, self.queda, self.intervalo_s, self.mira_s = arma, queda, intervalo_s, mira_s
        self.pico: float | None = None  # None = desengatilhado
        self._miras: list[tuple[float, float, float]] = []  # (t, x, y) recentes
        self._ultimo = -math.inf

    @property
    def engatilhado(self) -> bool:
        return self.pico is not None

    def reiniciar(self) -> None:
        self.pico = None
        self._miras = []

    def atualizar(
        self, t: float, razao: float, mira: tuple[float, float], arminha: bool
    ) -> tuple[float, float] | None:
        """`razao`: `razao_gatilho` do quadro. Devolve a mira (x, y) quando atira; senão None."""
        self._miras = [m for m in self._miras if t - m[0] <= self.mira_s]
        self._miras.append((t, *mira))
        if razao >= self.arma and (arminha or self.engatilhado):
            self.pico = max(self.pico or 0.0, razao)
        if not self.engatilhado or t - self._ultimo < self.intervalo_s:
            return None
        if razao <= self.pico * self.queda:
            self._ultimo = t
            self.pico = None
            _, x, y = self._miras[0]
            return x, y
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
    gatilho: float = 0.0  # `razao_gatilho`: dedão levantado (grande) ou abaixado (pequena)


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
        return EstadoMao(
            True, x, y, razao, self.pinca.atualizar(razao), eh_arminha(pontos),
            razao_gatilho(pontos),
        )
