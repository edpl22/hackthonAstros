"""AtividadeBase: o que toda atividade do Atlas cumpre (seção 6 da especificação).

- Roteiro fixo em 3 momentos: "O que vamos fazer" -> atividade -> "Terminou!" + Próximo,
  com a faixa Agora / Depois sempre no topo.
- Uma instrução por vez, com botão "Ouvir"; som só depois de uma ação da criança.
- Erro neutro com pistas graduais (repetir, realçar, mostrar o modelo).
- Ajuste de nível ("Quer um desafio?" / voltar um nível), que o professor pode travar.
- Pausa sempre visível (e Esc): congela, cobre a tela e silencia.
- Cada resposta vira uma tentativa no registro; `estado()` descreve a tela em JSON.

A subclasse cria a cena e aplica as regras dela; as entradas são ligadas aqui.
"""

import time
from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.entrada.camera import CameraNula
from app.entrada.mao_entrada import EntradaMao
from app.entrada.ponteiro import EntradaPonteiro
from app.entrada.teclado import EntradaTeclado
from app.entrada.varredura import EntradaVarredura
from app.nucleo import anuncio, progresso
from app.nucleo.conteudo import texto
from app.nucleo.eventos import Barramento
from app.nucleo.perfis import PADRAO
from app.nucleo.progresso import ControleNivel, Pistas
from app.nucleo.registro import Tentativa
from app.nucleo.tema import paleta_atual
from app.telas import icones
from app.telas.comum import botao, botao_voltar, rotulo
from app.telas.indicador_camera import IndicadorCamera

APRESENTACAO, ATIVIDADE, FIM = "apresentacao", "atividade", "fim"
PROXIMO_MOMENTO = {APRESENTACAO: ATIVIDADE, ATIVIDADE: FIM, FIM: "nova_rodada"}
NOME_MOMENTO = {
    APRESENTACAO: "base.momento_apresentacao",
    ATIVIDADE: "base.momento_atividade",
    FIM: "base.momento_fim",
    "nova_rodada": "base.momento_nova_rodada",
}


@dataclass
class Contexto:
    """O que a atividade recebe da janela: registro, áudio, sessão e a fábrica de câmera."""

    registro: object
    audio: object
    sessao: object
    fabrica_camera: object = CameraNula


class FaixaAgoraDepois(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.icone_agora = icones.Pictograma(APRESENTACAO)
        self.icone_depois = icones.Pictograma(ATIVIDADE)
        self.texto_agora = QLabel()
        self.texto_depois = QLabel()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        for rotulo_fixo, icone, rotulo_var in (
            (texto("base.agora"), self.icone_agora, self.texto_agora),
            (texto("base.depois"), self.icone_depois, self.texto_depois),
        ):
            fixo = QLabel(f"<b>{rotulo_fixo}:</b>")
            layout.addWidget(fixo)
            layout.addWidget(icone)
            layout.addWidget(rotulo_var)
            layout.addSpacing(24)
        layout.addStretch()

    def mostrar(self, agora: str, depois: str) -> None:
        self.icone_agora.definir(agora)
        self.icone_depois.definir(depois)
        self.texto_agora.setText(texto(NOME_MOMENTO[agora]))
        self.texto_depois.setText(texto(NOME_MOMENTO[depois]))
        self.setAccessibleName(
            f"{texto('base.agora')}: {self.texto_agora.text()}. "
            f"{texto('base.depois')}: {self.texto_depois.text()}."
        )


class CamadaPausa(QWidget):
    """Cobre a atividade com o fundo a 85% e mostra só o botão Continuar."""

    continuar = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.mensagem = rotulo(texto("base.pausado"), "instrucao")
        self.botao_continuar = botao(texto("base.continuar"), "grande")
        self.botao_continuar.clicked.connect(self.continuar)
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.mensagem)
        layout.addSpacing(24)
        layout.addWidget(self.botao_continuar, alignment=Qt.AlignHCenter)
        layout.addStretch()
        self.hide()

    def paintEvent(self, _evento):
        cor = QColor(paleta_atual().fundo)
        cor.setAlphaF(0.85)
        QPainter(self).fillRect(self.rect(), cor)

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Escape:
            self.continuar.emit()
        else:
            super().keyPressEvent(evento)


class AtividadeBase(QWidget):
    voltar = Signal()
    anunciou = Signal(str)

    id_atividade = "base"
    nivel_maximo = 1

    def __init__(self, contexto: Contexto, parent=None):
        super().__init__(parent)
        self.ctx = contexto
        self.perfil = PADRAO
        self.barramento = Barramento(self)
        self.area = None
        self.camera = None
        self.entrada_mao: EntradaMao | None = None
        self.entrada_teclado: EntradaTeclado | None = None
        self.nivel = ControleNivel(nivel_maximo=self.nivel_maximo)
        self.pistas: dict[str, Pistas] = {}
        self.momento = APRESENTACAO
        self.pausada = False
        self.oferece_desafio = False
        self.ultimo_anuncio = ""
        self.relogio = time.monotonic
        self._inicio_item = 0.0
        self._acao_nivel: str | None = None
        self._montar_interface()

    # --- interface -------------------------------------------------------------

    def _montar_interface(self) -> None:
        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)
        self.faixa = FaixaAgoraDepois()
        self.indicador = IndicadorCamera()
        self.botao_pausa = botao(texto("base.pausa"))
        self.botao_pausa.setIcon(icones.icone("pausa"))
        self.botao_pausa.setIconSize(QSize(28, 28))
        self.botao_pausa.clicked.connect(self.pausar)
        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addSpacing(16)
        topo.addWidget(self.faixa, 1)
        topo.addWidget(self.botao_pausa)

        self.instrucao = rotulo("", "instrucao")
        self.botao_ouvir = botao(texto("base.ouvir_curto"))
        self.botao_ouvir.setAccessibleName(texto("base.ouvir"))
        self.botao_ouvir.setToolTip(texto("base.ouvir"))
        self.botao_ouvir.setIcon(icones.icone("ouvir"))
        self.botao_ouvir.setIconSize(QSize(28, 28))
        self.botao_ouvir.clicked.connect(self.ouvir)
        self.botao_ouvir.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        linha_instrucao = QHBoxLayout()
        linha_instrucao.addWidget(self.botao_ouvir)
        linha_instrucao.addWidget(self.instrucao, 1)
        linha_instrucao.addStretch()  # segura o lugar quando a instrução some
        linha_instrucao.addWidget(self.indicador)

        # Momento 1: o que vamos fazer.
        self.pagina_apresentacao = QWidget()
        self.texto_apresentacao_rotulo = rotulo("", "instrucao")
        self.botao_comecar = botao(texto("base.comecar"), "grande")
        self.botao_comecar.clicked.connect(self.comecar)
        lay = QVBoxLayout(self.pagina_apresentacao)
        lay.addStretch()
        lay.addWidget(icones.Pictograma(APRESENTACAO, 96), alignment=Qt.AlignHCenter)
        lay.addWidget(self.texto_apresentacao_rotulo)
        lay.addSpacing(24)
        lay.addWidget(self.botao_comecar, alignment=Qt.AlignHCenter)
        lay.addStretch()

        # Momento 2: a atividade (a subclasse coloca a cena aqui).
        self.pagina_atividade = QWidget()
        self.layout_atividade = QVBoxLayout(self.pagina_atividade)
        self.layout_atividade.setContentsMargins(0, 0, 0, 0)

        # Momento 3: terminou.
        self.pagina_fim = QWidget()
        self.texto_fim = rotulo(texto("base.terminou"), "titulo")
        self.texto_fim_detalhe = rotulo("", "instrucao")
        self.pergunta_desafio = rotulo(texto("base.desafio"), "instrucao")
        self.botao_sim = botao(texto("base.sim"), "grande")
        self.botao_nao = botao(texto("base.nao"), "grande")
        self.botao_sim.clicked.connect(lambda: self.responder_desafio(True))
        self.botao_nao.clicked.connect(lambda: self.responder_desafio(False))
        self.botao_proximo = botao(texto("base.proximo"), "grande")
        self.botao_proximo.setIcon(icones.icone("nova_rodada"))
        self.botao_proximo.setIconSize(QSize(36, 36))
        self.botao_proximo.clicked.connect(self.proximo)
        linha_desafio = QHBoxLayout()
        linha_desafio.addStretch()
        linha_desafio.addWidget(self.botao_sim)
        linha_desafio.addSpacing(32)
        linha_desafio.addWidget(self.botao_nao)
        linha_desafio.addStretch()
        lay = QVBoxLayout(self.pagina_fim)
        lay.addStretch()
        lay.addWidget(self.texto_fim)
        lay.addWidget(self.texto_fim_detalhe)
        lay.addSpacing(24)
        lay.addWidget(self.pergunta_desafio)
        lay.addLayout(linha_desafio)
        lay.addWidget(self.botao_proximo, alignment=Qt.AlignHCenter)
        lay.addStretch()

        self.paginas = QStackedWidget()
        for pagina in (self.pagina_apresentacao, self.pagina_atividade, self.pagina_fim):
            self.paginas.addWidget(pagina)

        self.legenda = rotulo("")
        self.legenda.setAccessibleName("Legenda")

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addLayout(linha_instrucao)
        layout.addWidget(self.paginas, 1)
        layout.addWidget(self.legenda)

        self.camada_pausa = CamadaPausa(self)
        self.camada_pausa.continuar.connect(self.continuar)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.camada_pausa.setGeometry(self.rect())

    # --- ganchos da subclasse ------------------------------------------------------

    def preparar_rodada(self, semente: int | None) -> None:
        raise NotImplementedError

    def criar_area(self):
        """Devolve a cena (com ids_foco, centro, marcar_foco, alvo_em, cursor)."""
        raise NotImplementedError

    def texto_apresentacao(self) -> str:
        return texto(f"{self.id_atividade}.apresentacao")

    def instrucao_atual(self) -> str:
        raise NotImplementedError

    def item_atual(self) -> str | None:
        return None

    def realcar(self, item: str) -> None:
        """Pista 2: realçar o que importa."""

    def mostrar_modelo(self, item: str) -> None:
        """Pista 3: fazer a jogada certa pela criança."""

    def estado_area(self) -> dict:
        return {}

    # --- ciclo de vida -------------------------------------------------------------

    def iniciar(self, perfil=None, semente: int | None = None, varredura: bool = False) -> None:
        self.parar()
        self.perfil = perfil or PADRAO
        self.semente = semente
        self.varredura = varredura
        self.nivel = ControleNivel(nivel_maximo=self.nivel_maximo)
        self._nova_rodada()
        self._ir_para(APRESENTACAO)
        self.texto_apresentacao_rotulo.setText(self.texto_apresentacao())
        if self.perfil.audio_auto:
            self.falar(self.texto_apresentacao())
        self.camera = self.ctx.fabrica_camera(mostrar_miniatura=False)
        self.camera.pontos.connect(self._receber_pontos)
        self.camera.estado.connect(self.indicador.mostrar)
        self.camera.start()

    def parar(self) -> None:
        if self.camera is not None:
            camera, self.camera = self.camera, None
            camera.parar()
            camera.deleteLater()
        if isinstance(self.entrada_teclado, EntradaVarredura):
            self.entrada_teclado.desligar()
        if self.pausada:
            self.continuar()
        self.indicador.mostrar("desligada")

    def focar(self) -> None:
        alvo = {APRESENTACAO: self.botao_comecar, FIM: self.botao_proximo}.get(self.momento)
        (alvo or self.area or self).setFocus()

    def _receber_pontos(self, pontos, presente) -> None:
        if self.entrada_mao is not None and self.momento == ATIVIDADE and not self.pausada:
            self.entrada_mao.receber(pontos, presente)

    def _nova_rodada(self) -> None:
        self.pistas = {}
        self.oferece_desafio = False
        self.preparar_rodada(self.semente)
        if self.area is not None:
            self.layout_atividade.removeWidget(self.area)
            self.area.hide()
            self.area.deleteLater()
        self.barramento = Barramento(self)
        self.barramento.pausar.connect(self.pausar)
        self.barramento.continuar.connect(self.continuar)
        self.area = self.criar_area()
        self.layout_atividade.addWidget(self.area)
        EntradaPonteiro(self.area, self.barramento)
        if self.varredura:
            self.entrada_teclado = EntradaVarredura(self.area, self.barramento)
        else:
            self.entrada_teclado = EntradaTeclado(self.area, self.barramento)
        self.entrada_mao = EntradaMao(self.area, self.barramento, self.perfil)
        self._inicio_item = self.relogio()

    def _ir_para(self, momento: str) -> None:
        self.momento = momento
        self.paginas.setCurrentIndex((APRESENTACAO, ATIVIDADE, FIM).index(momento))
        self.faixa.mostrar(momento, PROXIMO_MOMENTO[momento])
        self.atualizar_instrucao()
        # Fora da atividade a frase já está no centro da tela; não repetir em cima.
        self.instrucao.setVisible(momento == ATIVIDADE)
        if isinstance(self.entrada_teclado, EntradaVarredura):
            if momento == ATIVIDADE:
                self.entrada_teclado.ligar()
            else:
                self.entrada_teclado.desligar()
        self.focar()

    def comecar(self) -> None:
        if self.momento != APRESENTACAO:
            return
        self._ir_para(ATIVIDADE)
        self._inicio_item = self.relogio()
        if self.perfil.audio_auto:
            self.falar(self.instrucao_atual())

    def concluir(self) -> None:
        """A subclasse chama quando a rodada termina."""
        self._ir_para(FIM)
        self.texto_fim_detalhe.setText(texto(f"{self.id_atividade}.terminou"))
        if self.perfil.aviso_troca_atividade:
            self.texto_fim_detalhe.setText(
                self.texto_fim_detalhe.text() + " " + texto("base.aviso_troca")
            )
        self.oferece_desafio = self._acao_nivel == progresso.OFERECER_DESAFIO
        for widget in (self.pergunta_desafio, self.botao_sim, self.botao_nao):
            widget.setVisible(self.oferece_desafio)
        self.botao_proximo.setVisible(not self.oferece_desafio)
        if self._acao_nivel == progresso.VOLTAR_NIVEL:
            self._anunciar(texto("base.nivel_voltou"))
        elif self.perfil.som_celebracao:
            self.falar(texto("base.terminou"))
        self._acao_nivel = None
        (self.botao_sim if self.oferece_desafio else self.botao_proximo).setFocus()

    def responder_desafio(self, aceitou: bool) -> None:
        if not self.oferece_desafio:
            return
        if aceitou:
            nivel = self.nivel.aceitar_desafio()
            self._anunciar(texto("base.nivel_subiu").format(nivel=nivel))
        self.oferece_desafio = False
        self.proximo()

    def proximo(self) -> None:
        if self.momento != FIM or self.oferece_desafio:
            return
        self._nova_rodada()
        self._ir_para(ATIVIDADE)

    def pausar(self) -> None:
        if self.pausada:
            return
        self.pausada = True
        self.barramento.blockSignals(True)  # congela: nenhuma entrada chega à cena
        if isinstance(self.entrada_teclado, EntradaVarredura):
            self.entrada_teclado.desligar()
        self.ctx.audio.silenciar(True)
        self.camada_pausa.setGeometry(self.rect())
        self.camada_pausa.show()
        self.camada_pausa.raise_()
        self.camada_pausa.botao_continuar.setFocus()
        self._anunciar(anuncio.frase("pausou"), falar=False)

    def continuar(self) -> None:
        if not self.pausada:
            return
        self.pausada = False
        self.barramento.blockSignals(False)
        self.ctx.audio.silenciar(False)
        self.camada_pausa.hide()
        if isinstance(self.entrada_teclado, EntradaVarredura) and self.momento == ATIVIDADE:
            self.entrada_teclado.ligar()
        self._anunciar(anuncio.frase("continuou"), falar=False)
        self.focar()

    def keyPressEvent(self, evento):
        if evento.key() == Qt.Key_Escape:
            self.pausar()
        else:
            super().keyPressEvent(evento)

    # --- respostas, pistas e registro ----------------------------------------------

    def atualizar_instrucao(self) -> None:
        if self.momento == ATIVIDADE:
            self.instrucao.setText(self.instrucao_atual())
        elif self.momento == APRESENTACAO:
            self.instrucao.setText(self.texto_apresentacao())
        else:
            self.instrucao.setText(texto(f"{self.id_atividade}.terminou"))

    def ouvir(self) -> None:
        self.falar(self.instrucao.text())

    def falar(self, frase: str) -> None:
        self.ctx.audio.falar(frase)

    def _anunciar(self, frase: str, falar: bool = True) -> None:
        self.ultimo_anuncio = frase
        self.legenda.setText(frase)
        if falar:
            self.falar(frase)
        self.anunciou.emit(frase)

    def pistas_de(self, item: str) -> Pistas:
        return self.pistas.setdefault(item, Pistas())

    def registrar_resposta(
        self, item: str, resposta: str, correta: bool, tipo_erro: str | None, frase: str
    ) -> int:
        """Registra a tentativa e, se errou, dá a próxima pista. Devolve o nível da pista."""
        pistas = self.pistas_de(item)
        nivel_pista = 0 if correta else pistas.errar()
        self._salvar_tentativa(item, resposta, correta, tipo_erro, pistas)
        if correta:
            self._finalizar_item(pistas)
            self._anunciar(frase)
            return 0
        if nivel_pista == progresso.REPETIR_INSTRUCAO:
            self._anunciar(f"{frase} {self.instrucao_atual()}")
        elif nivel_pista == progresso.REALCAR:
            self._anunciar(f"{frase} {texto('base.pista_realce')}")
            self.realcar(item)
        else:
            self._anunciar(f"{frase} {texto('base.pista_modelo')}")
            self.mostrar_modelo(item)
            self._finalizar_item(pistas)
        return nivel_pista

    def _finalizar_item(self, pistas: Pistas) -> None:
        acao = self.nivel.registrar_item(pistas.primeira_tentativa, pistas.precisou_modelo)
        self._acao_nivel = acao or self._acao_nivel
        self._inicio_item = self.relogio()

    def _salvar_tentativa(self, item, resposta, correta, tipo_erro, pistas: Pistas) -> None:
        sessao = self.ctx.sessao
        self.ctx.registro.salvar_tentativa(
            Tentativa(
                aluno=sessao.aluno.apelido if sessao.aluno else "visitante",
                atividade=self.id_atividade,
                habilidade=texto(f"{self.id_atividade}.habilidade"),
                item=item,
                resposta=resposta,
                correta=correta,
                tipo_erro=tipo_erro,
                pistas=pistas.nivel,
                precisou_modelo=pistas.precisou_modelo,
                tempo_ms=int((self.relogio() - self._inicio_item) * 1000),
                modo_entrada=self.barramento.modo_entrada,
                perfis=list(sessao.perfis),
            )
        )

    # --- estado para o demo e o agente --------------------------------------------------

    def estado(self) -> dict:
        item = self.item_atual()
        return {
            "tela": self.id_atividade,
            "momento": self.momento,
            "nivel": self.nivel.nivel,
            "instrucao": self.instrucao.text(),
            **self.estado_area(),
            "pista_nivel": self.pistas_de(item).nivel if item else 0,
            "pausada": self.pausada,
            "oferece_desafio": self.oferece_desafio,
            "concluida": self.momento == FIM,
            "anuncio": self.ultimo_anuncio,
            "modo_entrada": self.barramento.modo_entrada,
        }
