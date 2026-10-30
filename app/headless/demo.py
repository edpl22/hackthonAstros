"""`atlas demo`: executa roteiros sem tela e salva capturas, relatório e eventos.

Nesta etapa só existe o roteiro de navegação. Os roteiros das atividades entram
com cada atividade e passam a usar o barramento de eventos.
"""

import json
from collections.abc import Callable
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.entrada.camera import CameraNula
from app.headless.relatorio import Passo, escrever
from app.janela import JanelaPrincipal
from app.nucleo import tema
from app.nucleo.conteudo import texto


def _processar(app: QApplication, vezes: int = 3) -> None:
    for _ in range(vezes):
        app.processEvents()


def _roteiro_navegacao(janela: JanelaPrincipal) -> list[tuple[str, str, Callable[[], None]]]:
    """Cada passo: (nome, chave da frase narrada, ação)."""
    return [
        ("inicio", "demo.navegacao.inicio", lambda: None),
        ("materias", "demo.navegacao.materias", janela.inicio.botao_comecar.click),
        ("trilhas-portugues", "demo.navegacao.trilhas", janela.materias.botoes["portugues"].click),
        ("teste-mao", "demo.navegacao.teste_mao", lambda: janela.abrir_atividade("teste_camera")),
    ]


ROTEIROS = {"navegacao": _roteiro_navegacao}


def _ler_tamanho(tamanho: str) -> tuple[int, int]:
    largura, altura = (int(v) for v in tamanho.lower().split("x"))
    return largura, altura


def executar(roteiro: str, saida: str, tamanho: str = "1280x720") -> int:
    app = QApplication.instance() or QApplication([])
    tema.aplicar(app)
    pasta = Path(saida)
    pasta.mkdir(parents=True, exist_ok=True)

    nomes = list(ROTEIROS) if roteiro == "todas" else [roteiro]
    passos: list[Passo] = []
    eventos = []
    for nome_roteiro in nomes:
        janela = JanelaPrincipal(fabrica_camera=CameraNula)  # o demo nunca liga a webcam
        janela.resize(*_ler_tamanho(tamanho))
        janela.show()
        _processar(app)
        for nome_passo, chave_frase, acao in ROTEIROS[nome_roteiro](janela):
            acao()
            _processar(app)
            numero = len(passos) + 1
            arquivo = f"captura-{numero:02d}-{nome_passo}.png"
            janela.grab().save(str(pasta / arquivo))
            frase = texto(chave_frase)
            eventos.append(
                {"passo": numero, "roteiro": nome_roteiro, "evento": nome_passo, "frase": frase}
            )
            evento = f"{nome_roteiro}: {nome_passo}"
            passos.append(Passo(numero, nome_passo, evento, frase, arquivo))
        janela.close()

    escrever(pasta / "relatorio.md", texto("demo.titulo_relatorio"), passos)
    (pasta / "eventos.jsonl").write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in eventos), encoding="utf-8"
    )
    # Os registros de tentativas e de áudio entram com as atividades (Etapa 3).
    (pasta / "tentativas.json").write_text("[]\n", encoding="utf-8")
    (pasta / "audio.log").write_text("", encoding="utf-8")

    print(f"demo {roteiro}: {len(passos)} passos, {len(passos)} capturas")
    print(f"relatorio: {pasta / 'relatorio.md'}")
    return 0
