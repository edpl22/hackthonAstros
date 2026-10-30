"""Tela do treino de arrastar. Liga as entradas à cena e aplica as regras de `logica.py`."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from app.atividades.treino import logica
from app.entrada.camera import CameraNula
from app.entrada.mao_entrada import EntradaMao
from app.entrada.ponteiro import EntradaPonteiro
from app.entrada.teclado import EntradaTeclado
from app.entrada.varredura import EntradaVarredura
from app.nucleo import anuncio
from app.nucleo.conteudo import texto
from app.nucleo.eventos import Barramento
from app.nucleo.perfis import PADRAO
from app.telas.cena_itens import ALTURA, LARGURA, CenaItens
from app.telas.comum import botao_voltar, rotulo
from app.telas.indicador_camera import IndicadorCamera

LADO_PECA = 140
Y_PECAS, Y_CAIXAS = 0.28, 0.70  # centro das filas, em fração da altura da cena


class TelaTreino(QWidget):
    voltar = Signal()
    anunciou = Signal(str)

    def __init__(self, fabrica_camera=CameraNula, parent=None):
        super().__init__(parent)
        self.fabrica_camera = fabrica_camera
        self.barramento = Barramento(self)
        self.perfil = PADRAO
        self.cena: CenaItens | None = None
        self.rodada: logica.Rodada | None = None
        self.camera = None
        self.entrada_mao: EntradaMao | None = None
        self.entrada_teclado: EntradaTeclado | None = None
        self.ultimo_anuncio = ""

        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)
        self.instrucao = rotulo("", "instrucao")
        self.indicador = IndicadorCamera()
        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addSpacing(24)
        topo.addWidget(self.instrucao, 1)
        topo.addSpacing(24)
        topo.addWidget(self.indicador)

        self.legenda = rotulo("")  # o que aconteceu por último (também vira áudio na Etapa 3)
        self.legenda.setAccessibleName("Legenda")

        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.addLayout(topo)
        self.layout_principal.addStretch(1)  # trocado pela cena em iniciar()
        self.layout_principal.addWidget(self.legenda)

        self.barramento.pausar.connect(lambda: self._anunciar(anuncio.frase("pausou")))

    # --- ciclo de vida -------------------------------------------------------

    def iniciar(self, perfil=None, semente: int | None = None, varredura: bool = False) -> None:
        self.parar()
        self.perfil = perfil or PADRAO
        self.rodada = logica.nova_rodada(self.perfil.max_itens, semente)
        self._montar_cena()
        EntradaPonteiro(self.cena, self.barramento)
        if varredura:
            self.entrada_teclado = EntradaVarredura(self.cena, self.barramento)
            self.entrada_teclado.ligar()
        else:
            self.entrada_teclado = EntradaTeclado(self.cena, self.barramento)
        self.entrada_mao = EntradaMao(self.cena, self.barramento, self.perfil)
        self.camera = self.fabrica_camera(mostrar_miniatura=False)
        self.camera.pontos.connect(self.entrada_mao.receber)
        self.camera.estado.connect(self.indicador.mostrar)
        self.camera.start()
        self._atualizar_instrucao()
        self.legenda.clear()
        self.cena.setFocus()

    def parar(self) -> None:
        if self.camera is not None:
            camera, self.camera = self.camera, None
            camera.parar()
            camera.deleteLater()
        if isinstance(self.entrada_teclado, EntradaVarredura):
            self.entrada_teclado.desligar()
        self.indicador.mostrar("desligada")

    def focar(self) -> None:
        if self.cena is not None:
            self.cena.setFocus()

    def _montar_cena(self) -> None:
        if self.cena is not None:
            self.layout_principal.removeWidget(self.cena)
            self.cena.deleteLater()
        else:
            self.layout_principal.takeAt(1)  # o espaço reservado
        self.barramento.deleteLater()
        self.barramento = Barramento(self)
        self.barramento.pausar.connect(lambda: self._anunciar(anuncio.frase("pausou")))
        self.cena = CenaItens(self.barramento, self.perfil)
        self.layout_principal.insertWidget(1, self.cena, 1)

        letras = self.rodada.letras
        n = len(letras)
        # Escala do perfil, limitada para tudo caber na cena (largura e altura).
        lado = min(LADO_PECA * self.perfil.escala, (LARGURA - 80) / n - 40, ALTURA * 0.34)
        passo = LARGURA / n
        y_pecas, y_caixas = ALTURA * Y_PECAS, ALTURA * Y_CAIXAS
        for i, letra in enumerate(letras):
            coluna = self.rodada.ordem_pecas[i]
            self.cena.adicionar_peca(
                logica.id_peca(letra, i), letra, passo * (coluna + 0.5), y_pecas, lado
            )
            self.cena.adicionar_caixa(
                logica.id_caixa(i), letra, passo * (i + 0.5), y_caixas, lado + 24
            )

        self.cena.pegou.connect(self._ao_pegar)
        self.cena.soltou.connect(self._ao_soltar)
        self.cena.nada_para_pegar.connect(lambda: self._anunciar(anuncio.frase("nada_para_pegar")))

    # --- regras ----------------------------------------------------------------

    def _letra_da_peca(self, peca_id: str) -> str:
        return self.cena.pecas[peca_id].rotulo

    def _ao_pegar(self, peca_id: str) -> None:
        self._anunciar(anuncio.frase("pegou", item=self._letra_da_peca(peca_id)))

    def _ao_soltar(self, peca_id: str, caixa_id) -> None:
        letra = self._letra_da_peca(peca_id)
        if caixa_id is None:
            self.cena.devolver(peca_id)
            self._anunciar(anuncio.frase("soltou_fora", item=letra))
            return
        letra_caixa = self.cena.caixas[caixa_id].rotulo
        if logica.confere(letra, letra_caixa):
            self.cena.encaixar(peca_id, caixa_id)
            self.rodada.colocadas.add(letra)
            self._anunciar(anuncio.frase("encaixou", item=letra, alvo=letra_caixa))
        else:
            # Erro neutro: a peça volta e a frase convida a tentar de novo. Nada vermelho.
            self.cena.devolver(peca_id)
            self._anunciar(anuncio.frase("voltou", item=letra))
        self._atualizar_instrucao()

    def _atualizar_instrucao(self) -> None:
        if self.rodada.concluida:
            self.instrucao.setText(texto("treino.terminou"))
        else:
            self.instrucao.setText(
                texto("treino.instrucao").format(letra=self.rodada.proxima_letra())
            )

    def _anunciar(self, frase: str) -> None:
        self.ultimo_anuncio = frase
        self.legenda.setText(frase)
        self.anunciou.emit(frase)

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Escape:
            self.barramento.pausar.emit()
        else:
            super().keyPressEvent(evento)

    def estado(self) -> dict:
        return {
            "tela": "treino",
            "instrucao": self.instrucao.text(),
            **self.cena.estado(),
            "concluida": self.rodada.concluida,
            "anuncio": self.ultimo_anuncio,
            "modo_entrada": self.barramento.modo_entrada,
        }
