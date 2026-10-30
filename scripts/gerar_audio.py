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
LETRAS = "ABCD"

# Seções de frases.json lidas em voz alta (as demais são da área do adulto ou técnicas).
SECOES_FALADAS = ("base", "treino")
CHAVES_SEM_VOZ = {"habilidade", "instrucao", "nivel_subiu", "agora", "depois", "ouvir_curto"}


def coletar_textos() -> list[str]:
    frases = carregar("frases.json")
    textos: list[str] = []
    for secao in SECOES_FALADAS:
        for chave, valor in frases[secao].items():
            if chave not in CHAVES_SEM_VOZ and "{" not in valor:
                textos.append(valor)
    # Frases com letra: uma por letra do treino.
    for letra in LETRAS:
        textos.append(frases["treino"]["instrucao"].format(letra=letra))
        for chave in ("pegou", "voltou", "soltou_fora"):
            textos.append(frases["anuncio"][chave].format(item=letra))
        textos.append(frases["anuncio"]["encaixou"].format(item=letra, alvo=letra))
    for n in (1, 2, 3, 4):
        textos.append(frases["base"]["nivel_subiu"].format(nivel=n))
    for chave in ("nada_para_pegar", "pausou", "continuou"):
        textos.append(frases["anuncio"][chave])
    # Palavras e sílabas do Ímã das Sílabas (quando existir).
    try:
        for palavra in carregar("palavras.json"):
            textos.append(palavra["fala"]["palavra"])
            textos.extend(palavra["fala"]["silabas"])
    except FileNotFoundError:
        pass
    return list(dict.fromkeys(textos))  # sem repetir, na ordem


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
    for texto in coletar_textos():
        arquivo = nome_arquivo(texto)
        destino = PASTA_AUDIO / arquivo
        if args.refazer or not destino.exists():
            falar(texto, destino)
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
