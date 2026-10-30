"""Área do adulto: cadastrar alunos (apelido + bicho) e escolher os perfis de apoio."""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.nucleo import figuras
from app.nucleo.conteudo import texto
from app.nucleo.perfis import PERFIS
from app.nucleo.registro import AVATARES
from app.telas.comum import botao, botao_voltar, rotulo

TAMANHO_AVATAR = 56


class TelaAdulto(QWidget):
    voltar = Signal()
    alunos_mudaram = Signal()

    def __init__(self, registro, parent=None):
        super().__init__(parent)
        self.registro = registro
        self.id_editando: int | None = None

        self.botao_voltar = botao_voltar()
        self.botao_voltar.clicked.connect(self.voltar)
        topo = QHBoxLayout()
        topo.addWidget(self.botao_voltar)
        topo.addSpacing(24)
        topo.addWidget(rotulo(texto("adulto.titulo"), "instrucao", centro=False), 1)

        # Coluna da esquerda: lista de alunos.
        self.lista = QListWidget()
        self.lista.setAccessibleName(texto("adulto.alunos"))
        self.lista.setIconSize(QSize(40, 40))
        self.lista.currentItemChanged.connect(self._ao_escolher_na_lista)
        self.botao_novo = botao(texto("adulto.novo"))
        self.botao_novo.clicked.connect(self.limpar)
        esquerda = QVBoxLayout()
        esquerda.addWidget(rotulo(texto("adulto.alunos"), centro=False))
        esquerda.addWidget(self.lista, 1)
        esquerda.addWidget(self.botao_novo)

        # Coluna da direita: formulário.
        self.apelido = QLineEdit()
        self.apelido.setMaxLength(20)
        self.apelido.setAccessibleName(texto("adulto.apelido"))

        self.grupo_avatar = QButtonGroup(self)
        self.grupo_avatar.setExclusive(True)
        linha_avatar = QHBoxLayout()
        self.botoes_avatar = {}
        for avatar in AVATARES:
            b = QToolButton()
            b.setCheckable(True)
            b.setIcon(figuras.icone_avatar(avatar, TAMANHO_AVATAR))
            b.setIconSize(QSize(TAMANHO_AVATAR, TAMANHO_AVATAR))
            b.setAccessibleName(texto(f"avatares.{avatar}"))
            b.setToolTip(texto(f"avatares.{avatar}"))
            self.grupo_avatar.addButton(b)
            self.botoes_avatar[avatar] = b
            linha_avatar.addWidget(b)
        linha_avatar.addStretch()

        self.caixas_perfil = {}
        grade_perfis = QGridLayout()
        for i, nome in enumerate(n for n in PERFIS if n != "padrao"):
            caixa = QCheckBox(texto(f"perfis.{nome}"))
            caixa.setAccessibleName(texto(f"perfis.{nome}"))
            self.caixas_perfil[nome] = caixa
            grade_perfis.addWidget(caixa, i // 2, i % 2)

        self.botao_salvar = botao(texto("adulto.salvar"))
        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_apagar = botao(texto("adulto.apagar_aluno"))
        self.botao_apagar.clicked.connect(self.apagar)
        self.aviso = rotulo("", centro=False)
        botoes = QHBoxLayout()
        botoes.addWidget(self.botao_salvar)
        botoes.addWidget(self.botao_apagar)
        botoes.addStretch()

        direita = QVBoxLayout()
        direita.addWidget(rotulo(texto("adulto.apelido"), centro=False))
        direita.addWidget(self.apelido)
        direita.addWidget(rotulo(texto("adulto.avatar"), centro=False))
        direita.addLayout(linha_avatar)
        direita.addWidget(rotulo(texto("adulto.perfis"), centro=False))
        direita.addLayout(grade_perfis)
        direita.addStretch()
        direita.addLayout(botoes)
        direita.addWidget(self.aviso)

        conteudo = QWidget()
        corpo = QHBoxLayout(conteudo)
        corpo.setSpacing(48)
        corpo.addLayout(esquerda, 1)
        corpo.addLayout(direita, 2)
        # Com rolagem: o formulário cabe em qualquer altura de janela e em qualquer escala.
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QScrollArea.NoFrame)
        rolagem.setWidget(conteudo)
        self.lista.setMinimumHeight(240)

        layout = QVBoxLayout(self)
        layout.addLayout(topo)
        layout.addSpacing(16)
        layout.addWidget(rolagem, 1)
        self.recarregar()

    # --- dados ---------------------------------------------------------------

    def recarregar(self) -> None:
        self.lista.blockSignals(True)
        self.lista.clear()
        for aluno in self.registro.listar_alunos():
            item = QListWidgetItem(figuras.icone_avatar(aluno.avatar, 40), aluno.apelido)
            item.setData(Qt.UserRole, aluno)
            self.lista.addItem(item)
        self.lista.blockSignals(False)
        self.limpar()

    def limpar(self) -> None:
        self.id_editando = None
        self.apelido.clear()
        self.botoes_avatar[AVATARES[0]].setChecked(True)
        for caixa in self.caixas_perfil.values():
            caixa.setChecked(False)
        self.botao_apagar.setEnabled(False)
        self.lista.clearSelection()

    def _ao_escolher_na_lista(self, item, _anterior=None) -> None:
        if item is None:
            return
        aluno = item.data(Qt.UserRole)
        self.id_editando = aluno.id
        self.apelido.setText(aluno.apelido)
        self.botoes_avatar[aluno.avatar].setChecked(True)
        for nome, caixa in self.caixas_perfil.items():
            caixa.setChecked(nome in aluno.perfis)
        self.botao_apagar.setEnabled(True)
        self.aviso.clear()

    def avatar_escolhido(self) -> str:
        for avatar, b in self.botoes_avatar.items():
            if b.isChecked():
                return avatar
        return AVATARES[0]

    def salvar(self) -> None:
        perfis = [nome for nome, caixa in self.caixas_perfil.items() if caixa.isChecked()]
        if not self.apelido.text().strip():
            self.aviso.setText(texto("adulto.erro_apelido"))
            return
        try:
            self.registro.salvar_aluno(
                self.apelido.text(), self.avatar_escolhido(), perfis, self.id_editando
            )
        except ValueError as erro:
            self.aviso.setText(str(erro))
            return
        self.recarregar()
        self.aviso.setText(texto("adulto.salvo"))
        self.alunos_mudaram.emit()

    def apagar(self) -> None:
        if self.id_editando is None:
            return
        self.registro.apagar_aluno(self.id_editando)
        self.recarregar()
        self.aviso.setText(texto("adulto.apagado"))
        self.alunos_mudaram.emit()

    def focar(self) -> None:
        self.apelido.setFocus()
