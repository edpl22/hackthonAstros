"""Comando `atlas`. Sem subcomando (ou com `gui`), abre a interface gráfica."""

import argparse
import os
import sys

ROTEIROS = ("navegacao", "todas")


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Atlas: portugues e matematica com o corpo, adaptado a cada aluno.",
    )
    sub = parser.add_subparsers(dest="comando", metavar="COMANDO")

    sub.add_parser("gui", help="abre a interface grafica (padrao)")
    sub.add_parser("verificar", help="confere o ambiente e diz se o Atlas esta pronto")

    demo = sub.add_parser("demo", help="executa um roteiro sem tela e salva evidencias")
    demo.add_argument("roteiro", nargs="?", default="todas", choices=ROTEIROS)
    demo.add_argument("--saida", default="saida", help="pasta de saida (padrao: ./saida)")
    demo.add_argument("--tamanho", default="1280x720", help="tamanho da janela, ex.: 1280x720")
    return parser


def _modo_sem_tela() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def main(argv: list[str] | None = None) -> int:
    args = _criar_parser().parse_args(argv)

    if args.comando in (None, "gui"):
        from app.main import main as abrir_interface

        return abrir_interface()

    _modo_sem_tela()
    if args.comando == "verificar":
        from app.headless.verificar import executar

        return executar()
    if args.comando == "demo":
        from app.headless.demo import executar

        return executar(args.roteiro, args.saida, args.tamanho)
    return 2


if __name__ == "__main__":
    sys.exit(main())
