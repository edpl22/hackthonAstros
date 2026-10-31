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
from app.nucleo.audio import ServicoAudio
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


PISTAS = {
    1: "1 - repetir a instrucao",
    2: "2 - realcar a peca e a caixa",
    3: "3 - mostrar o modelo",
}


class Execucao:
    def __init__(self, app, pasta: Path, perfis: list[str], entrada: str, tamanho):
        self.app, self.pasta, self.perfis, self.entrada = app, pasta, perfis, entrada
        self.tamanho = tamanho
        self.passos: list[Passo] = []
        self.eventos: list[dict] = []
        self.tentativas: list[dict] = []
        self.audio_log: list[str] = []

    def nova_janela(self) -> JanelaPrincipal:
        janela = JanelaPrincipal(
            fabrica_camera=CameraNula,  # o demo nunca liga a webcam
            registro=Registro(":memory:"),  # banco só desta execução
            audio=ServicoAudio(backend="nulo"),  # registra o que tocaria
        )
        janela.resize(*self.tamanho)
        janela.show()
        _processar(self.app)
        return janela

    def fechar(self, janela) -> None:
        self.tentativas.extend(janela.registro.listar_tentativas())
        self.audio_log.extend(janela.audio.log)
        janela.close()

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
    janela.abrir_inicio()
    janela.inicio.teste_mao.click()  # canto inferior esquerdo da tela inicial
    ex.capturar(janela, "teste-mao", "abrir Teste da mao", texto("demo.navegacao.teste_mao"))
    for nome in ("inicio", "adulto", "materias", "trilhas", "teste_mao"):
        ex.registrar("navegacao", evento=nome)
    ex.fechar(janela)


def _ultima_tentativa(janela) -> dict:
    return janela.registro.listar_tentativas()[-1]


def roteiro_treino(ex: Execucao) -> None:
    janela = ex.nova_janela()
    janela.escolher_aluno(None, ex.perfis)
    janela.abrir_materia("portugues")
    janela.abrir_atividade("treino", semente=SEMENTE, varredura=ex.entrada == "varredura")
    tela = janela.atividades["treino"]
    tela.anunciou.connect(
        lambda frase: ex.registrar("treino", entrada=tela.barramento.modo_entrada, anuncio=frase)
    )
    momento_1 = "momento 1: o que vamos fazer"
    ex.capturar(janela, "treino-apresentacao", momento_1, tela.instrucao.text())
    tela.comecar()
    ex.capturar(janela, "treino-atividade", "momento 2: comecar", tela.instrucao.text())

    letras = tela.rodada.letras
    jogar = JOGADAS[ex.entrada]
    peca_b, caixa_a = treino.id_peca(letras[1], 1), treino.id_caixa(0)
    # Erro proposital, duas vezes: a peça B vai para a caixa A.
    for n_pista, nome in ((1, "treino-erro-pista1"), (2, "treino-erro-pista2")):
        jogar(tela, peca_b, caixa_a, 0)
        tentativa = _ultima_tentativa(janela)
        ex.capturar(
            janela, nome, f"{ex.entrada}: peca B na caixa A", tela.ultimo_anuncio,
            tipo_erro=tentativa["tipo_erro"], pista=PISTAS[n_pista],
        )
    tela.pausar()
    ex.capturar(janela, "treino-pausa", "Pausa (Esc)", texto("base.pausado"))
    tela.continuar()
    for i, letra in enumerate(letras):
        jogar(tela, treino.id_peca(letra, i), treino.id_caixa(i), i + 1)
        if i == 0:
            ex.capturar(
                janela, "treino-acerto", f"{ex.entrada}: peca A na caixa A", tela.ultimo_anuncio
            )
    ex.capturar(janela, "treino-fim", "momento 3: terminou", tela.texto_fim_detalhe.text())
    estado = tela.estado()
    ex.registrar("treino", evento="estado_final", concluida=estado["concluida"])
    ex.fechar(janela)


def roteiro_silabas(ex: Execucao) -> None:
    janela = ex.nova_janela()
    janela.escolher_aluno(None, ex.perfis)
    janela.abrir_materia("portugues")
    varredura = ex.entrada == "varredura"
    janela.abrir_atividade("silabas", semente=SEMENTE, varredura=varredura, palavra="bola")
    tela = janela.atividades["silabas"]
    tela.anunciou.connect(
        lambda frase: ex.registrar("silabas", entrada=tela.barramento.modo_entrada, anuncio=frase)
    )

    def bolha(silaba):
        return next(b.id for b in tela.rodada.bolhas if b.silaba == silaba)

    ex.capturar(janela, "silabas-apresentacao", "momento 1: o que vamos fazer",
                tela.instrucao.text())
    tela.comecar()
    ex.capturar(janela, "silabas-bola", "nivel 1: BOLA", tela.instrucao.text())
    jogar = JOGADAS[ex.entrada]
    # Erros propositais: LA na primeira caixa (ordem trocada) e uma distratora.
    distratora = next(b.id for b in tela.rodada.bolhas if b.posicao is None)
    for n_pista, peca, nome in ((1, bolha("LA"), "ordem"), (2, distratora, "distratora")):
        jogar(tela, peca, "caixa-1", 0)
        tentativa = _ultima_tentativa(janela)
        ex.capturar(
            janela, f"silabas-erro-{nome}", f"{ex.entrada}: {tentativa['resposta']} na 1a caixa",
            tela.ultimo_anuncio, tipo_erro=tentativa["tipo_erro"], pista=PISTAS[n_pista],
        )
    jogar(tela, bolha("BO"), "caixa-1", 1)
    ex.capturar(janela, "silabas-acerto", f"{ex.entrada}: BO na 1a caixa", tela.ultimo_anuncio)
    jogar(tela, bolha("LA"), "caixa-2", 2)
    ex.capturar(janela, "silabas-fim", "palavra pronta: toca BOLA", tela.texto_fim_detalhe.text())

    # Nível 3: letra minúscula e distratora do par surdo/sonoro (PRA x BRA).
    janela.abrir_atividade("silabas", semente=SEMENTE, nivel=3, palavra="prato")
    tela.comecar()
    ex.capturar(janela, "silabas-nivel3", "nivel 3: PRATO em minusculas", tela.instrucao.text())

    # Nível 4: qual bolha é a mais forte? Primeiro erra (LA), depois acerta (BO).
    janela.abrir_atividade("silabas", semente=SEMENTE, nivel=4, palavra="bola")
    tela.comecar()
    tela.barramento.usar(ex.entrada).escolher.emit(bolha("LA"))
    tentativa = _ultima_tentativa(janela)
    ex.capturar(janela, "silabas-tonica-erro", "nivel 4: escolhe LA", tela.ultimo_anuncio,
                tipo_erro=tentativa["tipo_erro"], pista=PISTAS[1])
    tela.barramento.escolher.emit(bolha("BO"))
    ex.capturar(janela, "silabas-tonica-certa", "nivel 4: escolhe BO", tela.ultimo_anuncio)
    ex.registrar("silabas", evento="estado_final", concluida=tela.estado()["concluida"])
    ex.fechar(janela)


def _escolher(tela, ex, peca_id) -> None:
    """Escolhe um cartão com a entrada da execução (pegar um cartão já é escolher)."""
    cena = tela.cena
    if ex.entrada == "mouse":
        _mouse(cena, QEvent.MouseButtonPress, cena.centro(peca_id), Qt.LeftButton)
        _mouse(cena, QEvent.MouseButtonRelease, cena.centro(peca_id), Qt.NoButton)
    elif ex.entrada == "mao-simulada":
        mao_simulada.reproduzir(tela.entrada_mao, cena, passos=[
            {"ir_para": peca_id, "ms": 600}, {"esperar": 300},
            {"pinca": True, "ms": 300}, {"pinca": False, "ms": 300},
        ])
    else:
        tecla = Qt.Key_Return if ex.entrada == "teclado" else Qt.Key_A
        avancar = tela.entrada_teclado.avancar
        _focar_e_selecionar(tela, peca_id, avancar, lambda: QTest.keyClick(cena, tecla))


def roteiro_quantidades(ex: Execucao) -> None:
    from app.atividades.quantidades import logica as mesa

    janela = ex.nova_janela()
    janela.escolher_aluno(None, ex.perfis)
    janela.abrir_materia("matematica")
    tela = janela.atividades["quantidades"]
    jogar = JOGADAS[ex.entrada]
    varredura = ex.entrada == "varredura"

    def cartao(certo: bool) -> str:
        r = tela.rodada
        return next(c.id for c in r.cartoes if (c.valor == r.certo) == certo)

    # Montar: um objeto a mais (erro proposital), depois a quantidade certa.
    janela.abrir_atividade("quantidades", semente=SEMENTE, varredura=varredura, nivel=mesa.MONTAR)
    tela.anunciou.connect(
        lambda frase: ex.registrar(
            "quantidades", entrada=tela.barramento.modo_entrada, anuncio=frase
        )
    )
    ex.capturar(janela, "mesa-apresentacao", "momento 1: o que vamos fazer", tela.instrucao.text())
    tela.comecar()
    meta = tela.rodada.a

    def colocar(n):
        for _ in range(n):
            livre = next(p.id for p in tela.cena.pecas.values()
                         if p.tipo == "objeto" and not p.encaixada)
            jogar(tela, livre, "bandeja-a", 0)

    colocar(meta + 1)
    ex.capturar(janela, "mesa-montar", f"{ex.entrada}: {meta + 1} objetos na bandeja",
                tela.ultimo_anuncio)
    _escolher(tela, ex, "cartao-pronto")
    tentativa = _ultima_tentativa(janela)
    ex.capturar(janela, "mesa-montar-erro", "Pronto com um a mais", tela.ultimo_anuncio,
                tipo_erro=tentativa["tipo_erro"], pista=PISTAS[1])
    colocar(meta)
    _escolher(tela, ex, "cartao-pronto")
    ex.capturar(janela, "mesa-montar-fim", f"{meta} objetos e Pronto", tela.ultimo_anuncio)

    # Comparar: liga um a um, marca a sobra; escolhe errado e depois certo.
    janela.abrir_atividade("quantidades", semente=6, varredura=varredura, nivel=mesa.COMPARAR)
    tela.comecar()
    _escolher(tela, ex, cartao(False))
    tentativa = _ultima_tentativa(janela)
    ex.capturar(janela, "mesa-comparar-erro", "comparar: cartao errado", tela.ultimo_anuncio,
                tipo_erro=tentativa["tipo_erro"], pista=PISTAS[1])
    _escolher(tela, ex, cartao(True))

    # Resolver até 20: dois cartões errados (pista 1 e pista 2) e o certo.
    janela.abrir_atividade("quantidades", semente=SEMENTE, varredura=varredura, nivel=mesa.CONTAS)
    tela.comecar()
    ex.capturar(janela, "mesa-conta", f"conta: {tela.estado()['conta']}", tela.instrucao.text())
    errados = [c.id for c in tela.rodada.cartoes if c.valor != tela.rodada.certo]
    for n_pista, errado in enumerate(errados, start=1):
        _escolher(tela, ex, errado)
        tentativa = _ultima_tentativa(janela)
        ex.capturar(janela, f"mesa-conta-pista{n_pista}", f"cartao {tentativa['resposta']}",
                    tela.ultimo_anuncio, tipo_erro=tentativa["tipo_erro"], pista=PISTAS[n_pista])
    _escolher(tela, ex, cartao(True))
    ex.capturar(janela, "mesa-conta-fim", "cartao certo", tela.ultimo_anuncio)
    ex.registrar("quantidades", evento="estado_final", concluida=tela.estado()["concluida"])
    ex.fechar(janela)


def roteiro_pizza(ex: Execucao) -> None:
    from app.atividades.pizza import logica as pizza

    janela = ex.nova_janela()
    janela.escolher_aluno(None, ex.perfis)
    janela.abrir_materia("matematica")
    tela = janela.atividades["pizza"]
    varredura = ex.entrada == "varredura"

    def cartao(valor) -> str:
        return f"cartao-{valor[0]}-{valor[1]}"

    # Montar: "Pronto" com uma fatia a menos (erro proposital), depois a fração certa.
    janela.abrir_atividade("pizza", semente=SEMENTE, varredura=varredura, nivel=pizza.MONTAR)
    tela.anunciou.connect(
        lambda frase: ex.registrar("pizza", entrada=tela.barramento.modo_entrada, anuncio=frase)
    )
    ex.capturar(janela, "pizza-apresentacao", "momento 1: o que vamos fazer", tela.instrucao.text())
    tela.comecar()
    n = tela.rodada.certo[0]
    for i in range(n - 1):
        _escolher(tela, ex, f"fatia-a-{i}")
    _escolher(tela, ex, "cartao-pronto")
    tentativa = _ultima_tentativa(janela)
    ex.capturar(janela, "pizza-montar-erro", f"{ex.entrada}: {n - 1} fatias e Pronto",
                tela.ultimo_anuncio, tipo_erro=tentativa["tipo_erro"], pista=PISTAS[1])
    _escolher(tela, ex, f"fatia-a-{n - 1}")
    _escolher(tela, ex, "cartao-pronto")
    ex.capturar(janela, "pizza-montar-fim", f"{n} fatias e Pronto", tela.ultimo_anuncio)

    # Somar: soma os denominadores (pista 1), depois troca em cima e embaixo (pista 2).
    janela.abrir_atividade("pizza", semente=SEMENTE, varredura=varredura, nivel=pizza.SOMAR)
    tela.comecar()
    errados = [c.id for c in tela.rodada.cartoes if c.valor != tela.rodada.certo]
    errados.sort(key=lambda c: c != cartao((sum(p[0] for p in tela.rodada.parcelas),
                                            2 * tela.rodada.corte)))
    for n_pista, errado in enumerate(errados, start=1):
        _escolher(tela, ex, errado)
        tentativa = _ultima_tentativa(janela)
        ex.capturar(janela, f"pizza-somar-pista{n_pista}", f"cartao {tentativa['resposta']}",
                    tela.ultimo_anuncio, tipo_erro=tentativa["tipo_erro"], pista=PISTAS[n_pista])
    _escolher(tela, ex, cartao(tela.rodada.certo))

    # Desafio na barra de chocolate: a soma passa de uma barra inteira.
    janela.abrir_atividade("pizza", semente=SEMENTE, varredura=varredura, nivel=pizza.DESAFIO,
                           forma="barra")
    tela.comecar()
    _escolher(tela, ex, cartao(tela.rodada.certo))
    ex.capturar(janela, "pizza-desafio-barra", "desafio: fracao impropria", tela.ultimo_anuncio)
    ex.registrar("pizza", evento="estado_final", concluida=tela.estado()["concluida"])
    ex.fechar(janela)


def roteiro_painel(ex: Execucao) -> None:
    """Painel do professor com a Turma de demonstração (dados fictícios, rotulados assim)."""
    from app.nucleo import turma_demo

    janela = ex.nova_janela()
    turma_demo.criar(janela.registro)
    janela.abrir_painel()
    ex.capturar(janela, "painel", "painel do professor", texto("demo.painel"))
    janela.close()  # sem fechar(): as tentativas fictícias não entram no tentativas.json


ROTEIROS = {
    "navegacao": roteiro_navegacao,
    "treino": roteiro_treino,
    "silabas": roteiro_silabas,
    "quantidades": roteiro_quantidades,
    "pizza": roteiro_pizza,
    "painel": roteiro_painel,
}


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
    (pasta / "tentativas.json").write_text(
        json.dumps(ex.tentativas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (pasta / "audio.log").write_text("".join(f"{linha}\n" for linha in ex.audio_log), "utf-8")

    erros = sum(not t["correta"] for t in ex.tentativas)
    print(f"demo {roteiro}: {len(ex.passos)} capturas; perfil {perfis_txt}; entrada {entrada}")
    print(f"tentativas: {len(ex.tentativas)} ({erros} com erro); audio: {len(ex.audio_log)} falas")
    print(f"relatorio: {pasta / 'relatorio.md'}")
    return 0
