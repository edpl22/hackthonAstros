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

# Seções de frases.json lidas em voz alta (as demais são da área do adulto ou técnicas).
SECOES_FALADAS = ("base", "treino", "silabas", "quantidades", "pizza")
CHAVES_SEM_VOZ = {
    "habilidade", "habilidade_tonica", "instrucao", "nivel_subiu", "agora", "depois",
    "ouvir_curto", "ordinais", "habilidade_montar", "habilidade_comparar", "habilidade_contas",
    "sobrou", "tirar", "bandeja-a", "bandeja-b", "habilidade_somar", "nomes_letras",
}


def coletar_textos() -> list[tuple[str, str]]:
    """Pares (texto como aparece na tela, texto que a voz lê).

    Na tela aparece "Pegue a bolha BO."; a voz lê "Pegue a bolha bó." para não soletrar
    a sílaba em maiúsculas e para soar como dentro da palavra.
    """
    from app.atividades.silabas import logica as silabas

    frases = carregar("frases.json")
    pares: list[tuple[str, str]] = []

    def mesmo(texto: str) -> None:
        pares.append((texto, texto))

    for secao in SECOES_FALADAS:
        for chave, valor in frases[secao].items():
            if chave not in CHAVES_SEM_VOZ and "{" not in valor:
                mesmo(valor)
    # Treino: frases com letra, uma por letra do alfabeto. A voz lê o nome ("bê"), não "B";
    # no nível 2 a peça é minúscula, então pegou/voltou também saem com a letra minúscula.
    from app.atividades.treino import logica as treino

    a = frases["anuncio"]
    nomes = dict(zip(treino.ALFABETO, frases["treino"]["nomes_letras"].split(","), strict=True))
    for letra, nome in nomes.items():
        pares.append((
            frases["treino"]["instrucao"].format(letra=letra),
            frases["treino"]["instrucao"].format(letra=nome),
        ))
        for item in (letra, letra.lower()):
            for chave in ("pegou", "voltou", "soltou_fora"):
                pares.append((a[chave].format(item=item), a[chave].format(item=nome)))
            pares.append((
                a["encaixou"].format(item=item, alvo=letra),
                a["encaixou"].format(item=nome, alvo=nome),
            ))
    for n in (1, 2, 3, 4):
        mesmo(frases["base"]["nivel_subiu"].format(nivel=n))
    for chave in ("nada_para_pegar", "pausou", "continuou"):
        mesmo(frases["anuncio"][chave])

    # Ímã das Sílabas.
    s = frases["silabas"]
    ordinais = s["ordinais"].split(",")
    for palavra in silabas.carregar_palavras():
        mesmo(palavra.fala_palavra)
        for fala in palavra.fala_silabas:
            mesmo(fala)
        for pos, silaba in enumerate(palavra.silabas):
            fala = palavra.fala_silabas[pos]
            na_tela = silabas.rotulo(silaba, palavra.nivel)
            pares.append((
                s["instrucao"].format(silaba=na_tela, ordinal=ordinais[pos]),
                s["instrucao"].format(silaba=fala, ordinal=ordinais[pos]),
            ))
        pares.append((
            s["instrucao_tonica"].format(palavra=palavra.texto),
            s["instrucao_tonica"].format(palavra=palavra.fala_palavra),
        ))
        tonica = palavra.silabas[palavra.tonica]
        pares.append((
            s["tonica_certa"].format(silaba=tonica, palavra=palavra.texto),
            s["tonica_certa"].format(
                silaba=palavra.fala_silabas[palavra.tonica], palavra=palavra.fala_palavra
            ),
        ))
    # Som de cada sílaba que pode virar bolha distratora (de outra palavra ou par surdo/sonoro).
    for palavra in silabas.carregar_palavras():
        for silaba in palavra.silabas:
            for candidata in (silaba, silabas.trocar_par(silaba)):
                if candidata:
                    mesmo(silabas.fala_distratora(candidata))
    # Mesa de Quantidades.
    from app.atividades.quantidades import logica as mesa

    q = frases["quantidades"]
    for c in mesa.conjuntos():
        for n in range(0, 13):
            mesmo(mesa.quantidade(n, c))  # "três maçãs", falado a cada objeto
        for n in range(2, 8):
            nome = c.singular if n == 1 else c.plural
            mesmo(q["instrucao_montar"].format(n=n, objetos=nome))
            mesmo(q["certo_montar"].format(quantidade=mesa.quantidade(n, c)))
    for a in range(1, 6):
        for b in range(1, 6):
            pares.append((
                q["instrucao_conta"].format(a=a, sinal="+", b=b),
                q["instrucao_conta"].format(
                    a=mesa.numero_por_extenso(a), sinal="mais", b=mesa.numero_por_extenso(b)
                ),
            ))
    for resposta in [str(n) for n in range(0, 21)] + list(mesa.COMPARACOES):
        mesmo(q["certo"].format(resposta=resposta))
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
