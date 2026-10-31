"""Gera os WAV das frases (PCM 16 bits, 22 050 Hz, mono) e o `conteudo/manifesto_audio.json`.

Provedores:
- google: Cloud Text-to-Speech, voz pt-BR Neural2/WaveNet
  (precisa de GOOGLE_APPLICATION_CREDENTIALS).
- espeak: espeak-ng, offline (voz sintética, mais robótica).

Sem credencial do Google, rode o espeak dentro de um contêiner (não precisa instalar nada):
    docker run --rm -v "$PWD:/w" -w /w python:3.11-slim-bookworm sh -c \
      "apt-get update -qq && apt-get install -y -qq espeak-ng >/dev/null && \
       python scripts/gerar_audio.py --provedor espeak"
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
import wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app.nucleo.conteudo import carregar  # noqa: E402

PASTA_AUDIO = RAIZ / "assets" / "audio"
MANIFESTO = RAIZ / "conteudo" / "manifesto_audio.json"
TAXA = 22050


def coletar_textos() -> list[tuple[str, str]]:
    """Pares (texto que o app pede para falar, texto que a voz lê).

    A voz só existe no português: a letra pega no treino ("B", lida "bê"), a sílaba pega no
    Ímã das Sílabas e a palavra pronta. Instruções e retornos ficam só na legenda.
    """
    from app.atividades.silabas import logica as silabas
    from app.atividades.treino import logica as treino

    frases = carregar("frases.json")
    pares: list[tuple[str, str]] = []

    def mesmo(texto: str) -> None:
        pares.append((texto, texto))

    nomes = frases["treino"]["nomes_letras"].split(",")
    pares += list(zip(treino.ALFABETO, nomes, strict=True))
    for palavra in silabas.carregar_palavras():
        mesmo(palavra.fala_palavra)
        for fala in palavra.fala_silabas:
            mesmo(fala)
    # Som de cada sílaba que pode virar bolha distratora (de outra palavra ou par surdo/sonoro).
    for palavra in silabas.carregar_palavras():
        for silaba in palavra.silabas:
            for candidata in (silaba, silabas.trocar_par(silaba)):
                if candidata:
                    mesmo(silabas.fala_distratora(candidata))
    return list(dict.fromkeys(pares))  # sem repetir, na ordem


def nome_arquivo(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")[:40] or "frase"
    resumo = hashlib.sha1(texto.encode("utf-8")).hexdigest()[:6]
    return f"{base}_{resumo}.wav"


def falar_espeak(texto: str, destino: Path) -> None:
    subprocess.run(
        ["espeak-ng", "-v", "pt-br", "-s", "140", "-w", str(destino), texto],
        check=True,
    )


def falar_google(texto: str, destino: Path) -> None:
    from google.cloud import texttospeech  # só com credencial; não é dependência do app

    cliente = texttospeech.TextToSpeechClient()
    resposta = cliente.synthesize_speech(
        input=texttospeech.SynthesisInput(text=texto),
        voice=texttospeech.VoiceSelectionParams(language_code="pt-BR", name="pt-BR-Neural2-A"),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16, sample_rate_hertz=TAXA
        ),
    )
    destino.write_bytes(resposta.audio_content)


def conferir_formato(caminho: Path) -> None:
    with wave.open(str(caminho), "rb") as w:
        formato = (w.getframerate(), w.getnchannels(), w.getsampwidth())
    if formato != (TAXA, 1, 2):
        raise RuntimeError(f"{caminho.name}: formato {formato}, esperado ({TAXA}, 1, 2)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    padrao = "google" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "espeak"
    parser.add_argument("--provedor", choices=("google", "espeak"), default=padrao)
    parser.add_argument("--refazer", action="store_true", help="gera de novo os que já existem")
    args = parser.parse_args()
    falar = falar_google if args.provedor == "google" else falar_espeak

    PASTA_AUDIO.mkdir(parents=True, exist_ok=True)
    manifesto = {}
    for texto, fala in coletar_textos():
        if texto in manifesto:
            continue
        arquivo = nome_arquivo(fala)
        destino = PASTA_AUDIO / arquivo
        if args.refazer or not destino.exists():
            falar(fala, destino)
        conferir_formato(destino)
        manifesto[texto] = arquivo

    usados = set(manifesto.values())
    for velho in PASTA_AUDIO.glob("*.wav"):
        if velho.name not in usados:
            velho.unlink()
    MANIFESTO.write_text(
        json.dumps(
            {"provedor": args.provedor, "formato": "PCM 16 bits, 22050 Hz, mono",
             "frases": manifesto},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{len(manifesto)} frases com audio ({args.provedor}) em {PASTA_AUDIO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
