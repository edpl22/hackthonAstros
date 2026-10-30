"""Lógica pura de alvos: qual item está sob o ponto (com tolerância) e o ciclo de foco."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Area:
    id: str
    x: float  # canto superior esquerdo, coordenadas da cena
    y: float
    largura: float
    altura: float

    @property
    def centro(self) -> tuple[float, float]:
        return self.x + self.largura / 2, self.y + self.altura / 2


def distancia_ate(area: Area, x: float, y: float) -> float:
    """0 dentro da área; fora, a distância até a borda mais próxima."""
    dx = max(area.x - x, 0.0, x - (area.x + area.largura))
    dy = max(area.y - y, 0.0, y - (area.y + area.altura))
    return math.hypot(dx, dy)


def mais_proximo(areas, x: float, y: float, tolerancia: float) -> str | None:
    """Id da área mais próxima do ponto, se estiver dentro da tolerância (área expandida)."""
    melhor, menor = None, math.inf
    for area in areas:
        d = distancia_ate(area, x, y)
        if d <= tolerancia and d < menor:
            melhor, menor = area.id, d
    return melhor


class CicloFoco:
    """Foco que anda em círculo por uma lista de ids (Tab, setas e varredura)."""

    def __init__(self):
        self.ids: list[str] = []
        self.indice = -1

    @property
    def atual(self) -> str | None:
        return self.ids[self.indice] if 0 <= self.indice < len(self.ids) else None

    def definir(self, ids) -> None:
        """Troca a lista mantendo o foco no mesmo id, se ele continuar existindo."""
        anterior = self.atual
        self.ids = list(ids)
        self.indice = self.ids.index(anterior) if anterior in self.ids else -1

    def avancar(self) -> str | None:
        if self.ids:
            self.indice = (self.indice + 1) % len(self.ids)
        return self.atual

    def voltar(self) -> str | None:
        if self.ids:
            n = len(self.ids)
            self.indice = (self.indice - 1) % n if self.indice >= 0 else n - 1
        return self.atual
