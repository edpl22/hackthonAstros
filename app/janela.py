"""Janela principal: uma pilha de telas e a navegação entre elas."""

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from app.atividades.base import AtividadeBase, Contexto
from app.atividades.quantidades.tela import TelaQuantidades
from app.atividades.silabas.tela import TelaSilabas
from app.atividades.teste_camera import TelaTesteCamera
from app.atividades.treino.tela import TelaTreino
from app.entrada.camera import fabrica_padrao
from app.nucleo import tema
from app.nucleo.audio import ServicoAudio
from app.nucleo.conteudo import texto
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao
from app.telas.adulto import TelaAdulto
from app.telas.inicio import TelaInicio
from app.telas.materias import TelaMaterias
from app.telas.trilhas import TelaTrilhas

MARGEM = 24


class JanelaPrincipal(QMainWindow):
    def __init__(self, fabrica_camera=None, registro=None, audio=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(texto("app.nome"))
        self.setMinimumSize(1024, 700)
        fabrica = fabrica_camera or fabrica_padrao()
        self.registro = registro or Registro()
        self.sessao = Sessao(self)
        volume = float(self.registro.ler_config("volume", "0.8"))
        self.audio = audio or ServicoAudio(volume=volume, parent=self)
        self.contexto = Contexto(self.registro, self.audio, self.sessao, fabrica)

        self.inicio = TelaInicio()
        self.adulto = TelaAdulto(self.registro, self.audio)
        self.materias = TelaMaterias()
        self.atividades = {
            "treino": TelaTreino(self.contexto),
            "silabas": TelaSilabas(self.contexto),
            "quantidades": TelaQuantidades(self.contexto),
            "teste_camera": TelaTesteCamera(fabrica),
        }
        self.trilhas = TelaTrilhas(self.atividades.keys())

        self.pilha = QStackedWidget()
        telas = (self.inicio, self.adulto, self.materias, self.trilhas, *self.atividades.values())
        for tela in telas:
            tela.layout().setContentsMargins(MARGEM, MARGEM, MARGEM, MARGEM)
            self.pilha.addWidget(tela)
        self.setCentralWidget(self.pilha)

        self.inicio.escolheu.connect(self.escolher_aluno)
        self.inicio.abrir_adulto.connect(lambda: self.ir_para(self.adulto))
        self.adulto.voltar.connect(self.abrir_inicio)
        self.materias.voltar.connect(self.abrir_inicio)
        self.materias.escolheu.connect(self.abrir_materia)
        self.trilhas.voltar.connect(lambda: self.ir_para(self.materias))
        self.trilhas.escolheu.connect(self.abrir_atividade)
        for atividade in self.atividades.values():
            atividade.voltar.connect(lambda: self.ir_para(self.trilhas))

        self.abrir_inicio()

    def ir_para(self, tela) -> None:
        atual = self.pilha.currentWidget()
        # A câmera só fica ligada dentro de uma atividade.
        if atual is not tela and atual in self.atividades.values():
            atual.parar()
        self.pilha.setCurrentWidget(tela)
        tela.focar()

    def abrir_inicio(self) -> None:
        self.sessao.definir(None)
        self._aplicar_tema()
        self.inicio.mostrar(self.registro.listar_alunos())
        self.ir_para(self.inicio)

    def escolher_aluno(self, aluno, perfis=None) -> None:
        """Aluno cadastrado usa os perfis dele; visitante usa `perfis` (padrão se vazio)."""
        self.sessao.definir(aluno, perfis)
        self._aplicar_tema()
        self.ir_para(self.materias)

    def _aplicar_tema(self) -> None:
        app = QApplication.instance()
        if app is not None:
            tema.aplicar(app, self.sessao.perfil)

    def abrir_materia(self, materia: str) -> None:
        self.trilhas.mostrar(materia, self.sessao.perfil.escala)
        self.ir_para(self.trilhas)

    def abrir_atividade(self, atividade_id: str, **opcoes) -> None:
        atividade = self.atividades[atividade_id]
        self.ir_para(atividade)
        atividade.iniciar(self.sessao.perfil, **opcoes)
        if isinstance(atividade, AtividadeBase):
            # O professor pode travar o nível (área do adulto).
            atividade.nivel.travado = self.registro.ler_config("travar_nivel", "0") == "1"
        atividade.focar()

    def closeEvent(self, evento):
        for atividade in self.atividades.values():
            atividade.parar()
        super().closeEvent(evento)
