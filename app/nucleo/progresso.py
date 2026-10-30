"""Regras puras de progresso: pistas graduais e ajuste de nível (seção 6 da especificação).

Pistas, por item: 1ª = repetir a instrução com áudio; 2ª = realçar o que importa;
3ª = mostrar o modelo fazendo. Depois da 3ª, a atividade segue e a tentativa fica com
`precisou_modelo=True`.

Nível: 4 itens seguidos certos na 1ª tentativa -> oferece o próximo nível ("Quer um desafio?").
2 itens seguidos que precisaram do modelo -> volta um nível. O professor pode travar o nível.
"""

from dataclasses import dataclass, field

REPETIR_INSTRUCAO, REALCAR, MOSTRAR_MODELO = 1, 2, 3
ACERTOS_PARA_DESAFIO = 4
MODELOS_PARA_VOLTAR = 2

OFERECER_DESAFIO = "oferecer_desafio"
VOLTAR_NIVEL = "voltar_nivel"


@dataclass
class Pistas:
    """Contador de pistas de um item. Cada erro sobe uma pista, até mostrar o modelo."""

    nivel: int = 0

    def errar(self) -> int:
        self.nivel = min(self.nivel + 1, MOSTRAR_MODELO)
        return self.nivel

    @property
    def precisou_modelo(self) -> bool:
        return self.nivel >= MOSTRAR_MODELO

    @property
    def primeira_tentativa(self) -> bool:
        return self.nivel == 0


@dataclass
class ControleNivel:
    nivel: int = 1
    nivel_maximo: int = 1
    travado: bool = False
    _acertos_seguidos: int = field(default=0, repr=False)
    _modelos_seguidos: int = field(default=0, repr=False)

    def registrar_item(self, primeira_tentativa: bool, precisou_modelo: bool) -> str | None:
        """Chamado quando um item termina. Devolve a ação sugerida, se houver."""
        self._acertos_seguidos = self._acertos_seguidos + 1 if primeira_tentativa else 0
        self._modelos_seguidos = self._modelos_seguidos + 1 if precisou_modelo else 0
        if self.travado:
            return None
        if self._modelos_seguidos >= MODELOS_PARA_VOLTAR and self.nivel > 1:
            self.nivel -= 1
            self._modelos_seguidos = 0
            self._acertos_seguidos = 0
            return VOLTAR_NIVEL
        if self._acertos_seguidos >= ACERTOS_PARA_DESAFIO and self.nivel < self.nivel_maximo:
            self._acertos_seguidos = 0
            return OFERECER_DESAFIO
        return None

    def aceitar_desafio(self) -> int:
        if not self.travado and self.nivel < self.nivel_maximo:
            self.nivel += 1
        return self.nivel
