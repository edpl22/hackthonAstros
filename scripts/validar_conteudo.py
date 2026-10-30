"""Confere o conteúdo: JSON válidos, áudios do manifesto e regras das palavras.

Para cada palavra de `conteudo/palavras.json`: as sílabas juntas formam o texto, a figura
existe, os áudios da palavra e das sílabas existem e `tonica` é um índice válido.
Sai com código 1 se encontrar algum problema.
"""

import json
import sys
import wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TAXA = 22050


def _json(nome: str):
    return json.loads((RAIZ / "conteudo" / nome).read_text(encoding="utf-8"))


def validar() -> list[str]:
    problemas: list[str] = []
    for arquivo in sorted((RAIZ / "conteudo").glob("*.json")):
        try:
            json.loads(arquivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erro:
            problemas.append(f"{arquivo.name}: JSON invalido ({erro})")
    if problemas:
        return problemas

    frases_com_audio = _json("manifesto_audio.json")["frases"]
    for texto, nome in frases_com_audio.items():
        caminho = RAIZ / "assets" / "audio" / nome
        if not caminho.exists():
            problemas.append(f"audio ausente para '{texto}': {nome}")
            continue
        with wave.open(str(caminho), "rb") as w:
            formato = (w.getframerate(), w.getnchannels(), w.getsampwidth())
        if formato != (TAXA, 1, 2):
            problemas.append(f"{nome}: formato {formato}, esperado (22050 Hz, mono, 16 bits)")

    caminho_palavras = RAIZ / "conteudo" / "palavras.json"
    if caminho_palavras.exists():
        for p in _json("palavras.json"):
            id_ = p["id"]
            if "".join(p["silabas"]) != p["texto"]:
                problemas.append(f"{id_}: silabas {p['silabas']} nao formam {p['texto']}")
            if not 0 <= p["tonica"] < len(p["silabas"]):
                problemas.append(f"{id_}: tonica {p['tonica']} fora das silabas")
            if len(p["fala"]["silabas"]) != len(p["silabas"]):
                problemas.append(f"{id_}: fala.silabas tem tamanho diferente de silabas")
            if not (RAIZ / "assets" / p["figura"]).exists():
                problemas.append(f"{id_}: figura ausente {p['figura']}")
            for texto in [p["fala"]["palavra"], *p["fala"]["silabas"]]:
                if texto not in frases_com_audio:
                    problemas.append(f"{id_}: sem audio para '{texto}'")
    return problemas


def main() -> int:
    problemas = validar()
    for problema in problemas:
        print(f"FALHA  {problema}")
    print("conteudo ok" if not problemas else f"{len(problemas)} problema(s)")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
