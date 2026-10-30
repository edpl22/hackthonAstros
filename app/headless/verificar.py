"""`atlas verificar`: uma linha por checagem, com OK, -- (não essencial) ou FALHA.

A saída é só ASCII para ler bem em qualquer terminal, inclusive em logs de CI e Docker.
"""

import json
import os
import sqlite3
import sys
from dataclasses import dataclass

from app.nucleo import caminhos

OK, AVISO, FALHA = "OK", "--", "FALHA"


@dataclass(frozen=True)
class Checagem:
    situacao: str
    mensagem: str

    def __str__(self) -> str:
        return f"{self.situacao:<3} {self.mensagem}"


def checar_python() -> Checagem:
    versao = sys.version_info
    texto = f"python {versao.major}.{versao.minor}"
    if (versao.major, versao.minor) == (3, 11):
        return Checagem(OK, texto)
    if versao.major == 3 and 9 <= versao.minor <= 12:
        return Checagem(AVISO, f"{texto} (testado em 3.11)")
    return Checagem(FALHA, f"{texto}: use Python 3.11")


def checar_qt() -> Checagem:
    try:
        import PySide6
        from PySide6.QtWidgets import QApplication, QLabel

        app = QApplication.instance() or QApplication([])
        rotulo = QLabel("Atlas")
        rotulo.resize(64, 32)
        if rotulo.grab().isNull():
            return Checagem(FALHA, "qt: nao foi possivel desenhar uma tela")
        return Checagem(OK, f"qt {app.platformName()} (PySide6 {PySide6.__version__})")
    except Exception as erro:  # qualquer falha do Qt vira uma linha de FALHA
        return Checagem(FALHA, f"qt: {type(erro).__name__}: {erro}")


def checar_fonte() -> Checagem:
    from app.nucleo.tema import carregar_fonte

    familia = carregar_fonte()
    if familia.startswith("Atkinson Hyperlegible"):
        return Checagem(OK, f"fonte {familia}")
    return Checagem(AVISO, "fonte: Atkinson Hyperlegible ausente; usando a fonte do sistema")


def checar_conteudo() -> Checagem:
    try:
        partes = []
        frases = json.loads(caminhos.conteudo("frases.json").read_text(encoding="utf-8"))
        partes.append(f"{len(frases)} grupos de frases")
        trilhas = json.loads(caminhos.conteudo("trilhas.json").read_text(encoding="utf-8"))
        partes.append(f"{sum(len(t) for t in trilhas.values())} trilhas")
        palavras = caminhos.conteudo("palavras.json")
        if palavras.exists():
            partes.append(f"{len(json.loads(palavras.read_text(encoding='utf-8')))} palavras")
        return Checagem(OK, "conteudo: " + ", ".join(partes))
    except Exception as erro:
        return Checagem(FALHA, f"conteudo: {type(erro).__name__}: {erro}")


def checar_audio() -> Checagem:
    backend = os.environ.get("ATLAS_AUDIO", "qt")
    pasta = caminhos.asset("audio")
    quantidade = len(list(pasta.glob("*.wav"))) if pasta.is_dir() else 0
    if quantidade == 0:
        return Checagem(
            AVISO, f"audio: nenhum arquivo WAV ainda; frases como legenda; backend {backend}"
        )
    return Checagem(OK, f"audio: {quantidade} arquivos WAV; backend {backend}")


def checar_camera() -> Checagem:
    from app.entrada.camera import pacotes_disponiveis

    if not pacotes_disponiveis():
        return Checagem(
            AVISO, "camera: pacote opencv/mediapipe ausente; o modo mouse/toque sera usado"
        )
    if not caminhos.asset("modelos", "hand_landmarker.task").exists():
        return Checagem(AVISO, "camera: modelo da mao ausente; o modo mouse/toque sera usado")
    return Checagem(
        OK, "camera: opencv, mediapipe e modelo presentes; a webcam e aberta so dentro da atividade"
    )


def checar_banco() -> Checagem:
    pasta = caminhos.dados()
    try:
        pasta.mkdir(parents=True, exist_ok=True)
        conexao = sqlite3.connect(pasta / "atlas.db")
        conexao.execute("SELECT 1")
        conexao.close()
        return Checagem(OK, f"banco de dados: {pasta / 'atlas.db'}")
    except Exception as erro:
        return Checagem(FALHA, f"banco de dados em {pasta}: {erro}")


CHECAGENS = (
    checar_python,
    checar_qt,
    checar_fonte,
    checar_conteudo,
    checar_audio,
    checar_camera,
    checar_banco,
)


def executar() -> int:
    resultados = [checagem() for checagem in CHECAGENS]
    for resultado in resultados:
        print(resultado)
    falhou = any(r.situacao == FALHA for r in resultados)
    print("RESULTADO: " + ("com falhas" if falhou else "pronto"))
    return 1 if falhou else 0
