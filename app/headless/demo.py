"""`atlas demo`: executa roteiros sem tela e salva capturas, relatório e eventos.

Cada entrada percorre o caminho real: eventos de mouse no viewport, teclas na cena, a
varredura avançando e pontos sintéticos da mão passando pelo `mao.py`. O roteiro do treino
inclui um erro proposital (peça B na caixa A) para mostrar a resposta neutra.
"""

import json
import os
from pathlib import Path

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from app.atividades.treino import logica as treino
from app.entrada import mao_simulada
from app.entrada.camera import CameraNula
from app.headless.relatorio import Passo, escrever
from app.janela import JanelaPrincipal
from app.nucleo import tema
from app.nucleo.conteudo import texto
from app.nucleo.registro import Registro

SEMENTE = 7  # posições das peças iguais em toda execução


def _processar(app: QApplication, vezes: int = 3) -> None:
    for _ in range(vezes):
        app.processEvents()


# --- entradas do treino ------------------------------------------------------


def _mouse(cena, tipo, ponto, botoes) -> None:
    local = QPointF(cena.mapFromScene(QPointF(*ponto)))
    botao = Qt.NoButton if tipo == QEvent.MouseMove else Qt.LeftButton
    evento = QMouseEvent(
        tipo, local, cena.viewport().mapToGlobal(local), botao, botoes, Qt.NoModifier
    )
    QApplication.sendEvent(cena.viewport(), evento)


def _jogar_mouse(tela, peca, caixa, n_jogada) -> None:
    cena = tela.cena
    origem, destino = cena.centro(peca), cena.centro(caixa)
    if n_jogada % 2 == 0:  # arrastar e soltar
        _mouse(cena, QEvent.MouseButtonPress, origem, Qt.LeftButton)
        meio = ((origem[0] + destino[0]) / 2, (origem[1] + destino[1]) / 2)
        _mouse(cena, QEvent.MouseMove, meio, Qt.LeftButton)
        _mouse(cena, QEvent.MouseMove, destino, Qt.LeftButton)
        _mouse(cena, QEvent.MouseButtonRelease, destino, Qt.NoButton)
    else:  # clique na peça, clique na caixa
        for ponto in (origem, destino):
            _mouse(cena, QEvent.MouseButtonPress, ponto, Qt.LeftButton)
            _mouse(cena, QEvent.MouseButtonRelease, ponto, Qt.NoButton)


def _focar_e_selecionar(tela, alvo, avancar, selecionar) -> None:
    for _ in range(20):
        if tela.entrada_teclado.foco.atual == alvo:
            break
        avancar()
    selecionar()


def _jogar_teclado(tela, peca, caixa, _n) -> None:
    def tecla(k):
        return lambda: QTest.keyClick(tela.cena, k)

    for alvo in (peca, caixa):
        _focar_e_selecionar(tela, alvo, tecla(Qt.Key_Tab), tecla(Qt.Key_Return))


def _jogar_varredura(tela, peca, caixa, _n) -> None:
    # Cada `avancar` é um tique de 1,5 s do relógio da varredura; qualquer tecla seleciona.
    for alvo in (peca, caixa):
        _focar_e_selecionar(
            tela, alvo, tela.entrada_teclado.avancar, lambda: QTest.keyClick(tela.cena, Qt.Key_A)
        )


def _jogar_mao(tela, peca, caixa, _n) -> None:
    passos = [
        {"ir_para": peca, "ms": 600},
        {"esperar": 300},
        {"pinca": True, "ms": 300},
        {"ir_para": caixa, "ms": 600},
        {"esperar": 300},
        {"pinca": False, "ms": 300},
    ]
    mao_simulada.reproduzir(tela.entrada_mao, tela.cena, passos=passos)


JOGADAS = {
    "mouse": _jogar_mouse,
    "teclado": _jogar_teclado,
    "varredura": _jogar_varredura,
    "mao-simulada": _jogar_mao,
}


# --- roteiros ------------------------------------------------------------------


class Execucao:
    def __init__(self, app, pasta: Path, perfis: list[str], entrada: str, tamanho):
        self.app, self.pasta, self.perfis, self.entrada = app, pasta, perfis, entrada
        self.tamanho = tamanho
        self.passos: list[Passo] = []
        self.eventos: list[dict] = []

    def nova_janela(self) -> JanelaPrincipal:
        janela = JanelaPrincipal(fabrica_camera=CameraNula, registro=Registro(":memory:"))
        janela.resize(*self.tamanho)
        janela.show()
        _processar(self.app)
        return janela

    def capturar(self, janela, nome, evento, frase, tipo_erro="", pista="") -> None:
        _processar(self.app)
        numero = len(self.passos) + 1
        arquivo = f"captura-{numero:02d}-{nome}.png"
        janela.grab().save(str(self.pasta / arquivo))
        self.passos.append(Passo(numero, nome, evento, frase, arquivo, tipo_erro, pista))

    def registrar(self, roteiro: str, **dados) -> None:
        self.eventos.append({"n": len(self.eventos) + 1, "roteiro": roteiro, **dados})


def roteiro_navegacao(ex: Execucao) -> None:
    janela = ex.nova_janela()
    ex.capturar(janela, "inicio", "abrir", texto("demo.navegacao.inicio"))
    # Cadastro pelo formulário real da área do adulto (banco em memória, aluno de exemplo).
    janela.ir_para(janela.adulto)
    adulto = janela.adulto
    adulto.apelido.setText(texto("demo.navegacao.aluno_exemplo"))
    adulto.botoes_avatar["sapo"].setChecked(True)
    adulto.caixas_perfil["tea"].setChecked(True)
    adulto.caixas_perfil["dislexia"].setChecked(True)
    ex.capturar(janela, "adulto", "preencher cadastro", texto("demo.navegacao.adulto"))
    adulto.botao_salvar.click()
    janela.abrir_inicio()
    ex.capturar(janela, "inicio-com-aluno", "salvar aluno", texto("demo.navegacao.inicio_aluno"))
    janela.escolher_aluno(None, ex.perfis)  # o mesmo que clicar em Visitante
    ex.capturar(janela, "materias", "escolher visitante", texto("demo.navegacao.materias"))
    janela.materias.botoes["portugues"].click()
    ex.capturar(janela, "trilhas-portugues", "escolher Portugues", texto("demo.navegacao.trilhas"))
    janela.abrir_atividade("teste_camera")
    ex.capturar(janela, "teste-mao", "abrir Teste da mao", texto("demo.navegacao.teste_mao"))
    for nome in ("inicio", "materias", "trilhas", "teste_mao"):
        ex.registrar("navegacao", evento=nome)
    janela.close()


def roteiro_treino(ex: Execucao) -> None:
    janela = ex.nova_janela()
    janela.escolher_aluno(None, ex.perfis)
    janela.abrir_materia("portugues")
    janela.abrir_atividade("treino", semente=SEMENTE, varredura=ex.entrada == "varredura")
    tela = janela.atividades["treino"]
    tela.anunciou.connect(
        lambda frase: ex.registrar(
            "treino", entrada=tela.barramento.modo_entrada, anuncio=frase
        )
    )
    ex.capturar(janela, "treino-inicio", "abrir Treino de arrastar", texto("demo.treino_inicio"))

    letras = tela.rodada.letras
    jogar = JOGADAS[ex.entrada]
    # Erro proposital: a peça B vai para a caixa A.
    jogar(tela, treino.id_peca(letras[1], 1), treino.id_caixa(0), 0)
    ex.capturar(
        janela, "treino-erro", f"{ex.entrada}: peca B na caixa A", tela.ultimo_anuncio,
        tipo_erro="troca de letra (B no lugar de A)", pista="a peca volta; instrucao repetida",
    )
    for i, letra in enumerate(letras):
        jogar(tela, treino.id_peca(letra, i), treino.id_caixa(i), i + 1)
        if i == 0:
            ex.capturar(
                janela, "treino-acerto", f"{ex.entrada}: peca A na caixa A", tela.ultimo_anuncio
            )
    ex.capturar(
        janela, "treino-fim", f"{ex.entrada}: todas as pecas colocadas", tela.instrucao.text()
    )
    estado = tela.estado()
    ex.registrar("treino", evento="estado_final", concluida=estado["concluida"])
    janela.close()


ROTEIROS = {"navegacao": roteiro_navegacao, "treino": roteiro_treino}


def _ler_tamanho(tamanho: str) -> tuple[int, int]:
    largura, altura = (int(v) for v in tamanho.lower().split("x"))
    return largura, altura


def executar(
    roteiro: str,
    saida: str,
    tamanho: str = "1280x720",
    perfis: list[str] | None = None,
    entrada: str = "mouse",
) -> int:
    os.environ["ATLAS_SEM_ANIMACAO"] = "1"  # capturas determinísticas
    app = QApplication.instance() or QApplication([])
    tema.aplicar(app)
    pasta = Path(saida)
    pasta.mkdir(parents=True, exist_ok=True)

    ex = Execucao(app, pasta, perfis or [], entrada, _ler_tamanho(tamanho))
    nomes = list(ROTEIROS) if roteiro == "todas" else [roteiro]
    for nome in nomes:
        ROTEIROS[nome](ex)

    perfis_txt = ",".join(ex.perfis) or "padrao"
    titulo = f"{texto('demo.titulo_relatorio')} (perfil: {perfis_txt}; entrada: {entrada})"
    escrever(pasta / "relatorio.md", titulo, ex.passos)
    (pasta / "eventos.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in ex.eventos), encoding="utf-8"
    )
    # Os registros de tentativas e de áudio entram com o núcleo das atividades (Etapa 3).
    (pasta / "tentativas.json").write_text("[]\n", encoding="utf-8")
    (pasta / "audio.log").write_text("", encoding="utf-8")

    print(f"demo {roteiro}: {len(ex.passos)} capturas; perfil {perfis_txt}; entrada {entrada}")
    print(f"relatorio: {pasta / 'relatorio.md'}")
    return 0
