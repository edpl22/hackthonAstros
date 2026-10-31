"""Tabuada Protetora sobre a AtividadeBase.

Uma conta da tabuada, um relógio de 1 minuto e monstrinhos com números. Acertar o monstrinho
com o resultado vale +1 ponto; acertar um com número errado vale -1; errar o tiro não muda.
Com a câmera desligada, tudo é pelo mouse (ou toque e teclado). Com a câmera ligada, a mão faz
uma "arminha" e dispara com um movimento rápido para cima; a pinça fica desligada aqui.
"""

import os

from PySide6.QtCore import QRectF, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QGraphicsSimpleTextItem

from app.atividades.base import ATIVIDADE, AtividadeBase
from app.atividades.tabuada import logica
from app.nucleo import erros
from app.nucleo.conteudo import texto
from app.nucleo.tema import paleta_atual
from app.telas.cena_itens import ALTURA, LARGURA, CenaItens

LADO_MONSTRO = 120
Y_CONTA = 50
REGIAO_MONSTROS = QRectF(40, 130, LARGURA - 80, ALTURA - 140)
ESPERA_MODELO_MS = 1500


def _frase(chave: str, **dados) -> str:
    return texto(f"tabuada.{chave}").format(**dados)


def _sem_animacao() -> bool:
    return os.environ.get("ATLAS_SEM_ANIMACAO") == "1"


class TelaTabuada(AtividadeBase):
    id_atividade = "tabuada"
    nivel_maximo = logica.NIVEL_MAXIMO
    gesto_mao = "arminha"

    def __init__(self, contexto, parent=None):
        self.partida: logica.Partida | None = None
        self._rodadas = 0
        super().__init__(contexto, parent)
        self.relogio_partida = QTimer(self)
        self.relogio_partida.setInterval(1000)
        self.relogio_partida.timeout.connect(self.passar_segundo)

    # --- partida ------------------------------------------------------------------------

    def iniciar(self, *args, **kwargs) -> None:
        self._rodadas = 0  # a mesma semente dá as mesmas partidas a cada abertura
        super().iniciar(*args, **kwargs)

    def preparar_rodada(self, semente: int | None) -> None:
        semente_rodada = None if semente is None else semente + self._rodadas
        self._rodadas += 1
        self.partida = logica.nova_partida(self.nivel.nivel, self.perfil.max_itens, semente_rodada)

    @property
    def cena(self) -> CenaItens:
        return self.area

    @property
    def conta(self) -> logica.Conta:
        return self.partida.conta

    def _ir_para(self, momento: str) -> None:
        super()._ir_para(momento)
        if momento == ATIVIDADE:  # o relógio só anda durante a atividade
            self.relogio_partida.start()
        else:
            self.relogio_partida.stop()

    def parar(self) -> None:
        self.relogio_partida.stop()
        super().parar()

    def passar_segundo(self) -> None:
        if self.momento != ATIVIDADE or self.pausada or self.partida.acabou:
            return
        acabou = logica.passar_segundo(self.partida)
        self.texto_relogio.setText(logica.relogio(self.partida.restante_s))
        if acabou:
            self.cena.parar_flutuar()
            self.concluir()

    def passar_tempo(self, segundos: int) -> None:
        """Avança o relógio sem esperar (demo, agente e testes)."""
        for _ in range(segundos):
            self.passar_segundo()

    def concluir(self) -> None:
        super().concluir()
        pontos = _frase("pontos_final", pontos=self.partida.pontos)
        self.texto_fim_detalhe.setText(f"{self.texto_fim_detalhe.text()} {pontos}")

    # --- cena ---------------------------------------------------------------------------

    def _texto(self, cena, conteudo: str, x: float, y: float, tamanho: int, centro=True):
        item = QGraphicsSimpleTextItem(conteudo)
        fonte = QFont(self.font())
        fonte.setPixelSize(tamanho)
        fonte.setBold(True)
        item.setFont(fonte)
        item.setBrush(QColor(paleta_atual().texto))
        largura = item.boundingRect().width() if centro else 0
        item.setPos(x - largura / 2, y - item.boundingRect().height() / 2)
        cena.scene().addItem(item)
        return item

    def criar_area(self) -> CenaItens:
        cena = CenaItens(self.barramento, self.perfil)
        self.area = cena
        self.texto_conta = self._texto(cena, self.conta.texto, LARGURA / 2, Y_CONTA, 72)
        self.texto_pontos = self._texto(
            cena, _frase("pontos", pontos=self.partida.pontos), 40, Y_CONTA, 36, centro=False
        )
        self.texto_relogio = self._texto(
            cena, logica.relogio(self.partida.restante_s), LARGURA - 140, Y_CONTA, 48, centro=False
        )
        self._mostrar_monstros()
        cena.pegou.connect(self._ao_pegar)
        cena.escolheu.connect(self._acertar)
        return cena

    def _mostrar_monstros(self) -> None:
        cena = self.cena
        for id_monstro in [i for i, p in cena.pecas.items() if p.tipo == "monstro"]:
            cena.remover_peca(id_monstro)
        monstros = self.conta.monstros
        n = len(monstros)
        largura = REGIAO_MONSTROS.width() / n
        for i, monstro in enumerate(monstros):
            x = REGIAO_MONSTROS.left() + largura * (i + 0.5)
            y = REGIAO_MONSTROS.top() + REGIAO_MONSTROS.height() * (0.35 if i % 2 else 0.65)
            cena.adicionar_peca(monstro.id, str(monstro.valor), x, y, LADO_MONSTRO, tipo="monstro")
        self.texto_conta.setText(self.conta.texto)
        self.texto_conta.setPos(LARGURA / 2 - self.texto_conta.boundingRect().width() / 2,
                                Y_CONTA - self.texto_conta.boundingRect().height() / 2)
        cena.flutuar(self.perfil.velocidade, REGIAO_MONSTROS)

    def _proxima_conta(self) -> None:
        if self.partida.acabou or self.momento != ATIVIDADE:
            return
        logica.nova_conta(self.partida)
        self._mostrar_monstros()
        self.atualizar_instrucao()

    def instrucao_atual(self) -> str:
        return _frase("instrucao", conta=self.conta.texto)

    def item_atual(self) -> str | None:
        return self.conta.id

    # --- jogadas ------------------------------------------------------------------------

    def _ao_pegar(self, id_monstro: str) -> None:
        """Clique, toque, tecla ou disparo da arminha: pegar um monstrinho é acertá-lo."""
        self.barramento.soltar.emit()
        self._acertar(id_monstro)

    def _acertar(self, id_monstro: str) -> None:
        conta = self.conta
        monstro = next((m for m in conta.monstros if m.id == id_monstro), None)
        if monstro is None or self.momento != ATIVIDADE or self.partida.acabou:
            return
        tipo_erro = erros.classificar_tabuada(monstro.valor, conta.a, conta.b)
        pontos = logica.acertar(self.partida, monstro.valor)
        self.texto_pontos.setText(_frase("pontos", pontos=pontos))
        dados = {"conta": conta.texto, "valor": monstro.valor, "resultado": conta.certo}
        if tipo_erro is None:
            frase = _frase("certo", **dados)
            self.registrar_resposta(conta.id, str(monstro.valor), True, None, frase)
            self._proxima_conta()
            return
        self.cena.remover_peca(id_monstro)
        conta.monstros.remove(monstro)
        frase = _frase("errado", **dados)
        self.registrar_resposta(conta.id, str(monstro.valor), False, tipo_erro, frase)

    # --- pistas -------------------------------------------------------------------------

    def _id_certo(self) -> str:
        return next(m.id for m in self.conta.monstros if m.valor == self.conta.certo)

    def realcar(self, item: str) -> None:
        self.cena.realcar([self._id_certo()])

    def mostrar_modelo(self, item: str) -> None:
        """Realça o certo, mostra a conta pronta na legenda e passa para a próxima conta."""
        self.cena.realcar([self._id_certo()])
        modelo = f"{self.conta.texto} = {self.conta.certo}."
        self._anunciar(f"{self.ultimo_anuncio} {modelo}")
        if _sem_animacao():
            self._proxima_conta()
        else:
            QTimer.singleShot(ESPERA_MODELO_MS, self._proxima_conta)

    def estado_area(self) -> dict:
        return {
            "conta": self.conta.texto,
            "pontos": self.partida.pontos,
            "tempo_restante": self.partida.restante_s,
            **self.cena.estado(),
        }
