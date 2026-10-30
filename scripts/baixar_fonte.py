"""Baixa a fonte Atkinson Hyperlegible (SIL OFL 1.1) para assets/fontes/."""

from _download import RAIZ, baixar

BASE = "https://github.com/google/fonts/raw/main/ofl/atkinsonhyperlegible/"
ARQUIVOS = {
    "AtkinsonHyperlegible-Regular.ttf": 10_000,
    "AtkinsonHyperlegible-Bold.ttf": 10_000,
    "OFL.txt": 1_000,
}


def main() -> None:
    for nome, tamanho_minimo in ARQUIVOS.items():
        baixar(BASE + nome, RAIZ / "assets" / "fontes" / nome, tamanho_minimo)


if __name__ == "__main__":
    main()
