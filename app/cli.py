"""Comando `atlas`. Sem subcomando (ou com `gui`), abre a interface gráfica."""

import argparse
import json
import os
import sys

ROTEIROS = ("navegacao", "treino", "silabas", "quantidades", "pizza", "todas")
ENTRADAS = ("mouse", "teclado", "varredura", "mao-simulada")


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atlas",
        description="Atlas: portugues e matematica com o corpo, adaptado a cada aluno.",
    )
    sub = parser.add_subparsers(dest="comando", metavar="COMANDO")

    sub.add_parser("gui", help="abre a interface grafica (padrao)")
    verificar = sub.add_parser("verificar", help="confere o ambiente e diz se o Atlas esta pronto")
    verificar.add_argument(
        "--completo", action="store_true", help="tambem carrega o detector da mao (mais lento)"
    )

    demo = sub.add_parser("demo", help="executa um roteiro sem tela e salva evidencias")
    demo.add_argument("roteiro", nargs="?", default="todas", choices=ROTEIROS)
    demo.add_argument("--perfil", default="", help="perfis separados por virgula: tea,dislexia")
    demo.add_argument("--entrada", default="mouse", choices=ENTRADAS)
    demo.add_argument("--saida", default="saida", help="pasta de saida (padrao: ./saida)")
    demo.add_argument("--tamanho", default="1280x720", help="tamanho da janela, ex.: 1280x720")

    agente = sub.add_parser("agente", help="joga uma atividade por JSON Lines (stdin/stdout)")
    agente.add_argument("atividade", help="ex.: treino")
    agente.add_argument("--perfil", default="", help="perfis separados por virgula: tea,dislexia")
    agente.add_argument("--palavra", help="silabas: palavra inicial (padrao: bola)")

    perfis = sub.add_parser("perfis", help="mostra os perfis e as regras de combinacao em JSON")
    perfis.add_argument("--combinar", metavar="LISTA", help="ex.: tea,dislexia")
    return parser


def _modo_sem_tela() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _perfis(combinar: str | None) -> int:
    from app.nucleo import perfis

    if combinar is None:
        saida = {
            "perfis": {nome: p.como_dict() for nome, p in perfis.PERFIS.items()},
            "regras": perfis.REGRAS,
        }
    else:
        nomes = perfis.ler_lista(combinar)
        saida = {"combinacao": nomes, "resultado": perfis.combinar(nomes).como_dict()}
    print(json.dumps(saida, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _criar_parser()
    args = parser.parse_args(argv)

    if args.comando in (None, "gui"):
        from app.main import main as abrir_interface

        return abrir_interface()

    _modo_sem_tela()
    try:
        if args.comando == "perfis":
            return _perfis(args.combinar)
        if args.comando == "verificar":
            from app.headless.verificar import executar

            return executar(args.completo)
        if args.comando == "agente":
            from app.headless.agente import executar
            from app.nucleo.perfis import ler_lista

            return executar(args.atividade, ler_lista(args.perfil), palavra=args.palavra)
        if args.comando == "demo":
            from app.headless.demo import executar
            from app.nucleo.perfis import ler_lista

            perfis = ler_lista(args.perfil)
            return executar(args.roteiro, args.saida, args.tamanho, perfis, args.entrada)
    except ValueError as erro:
        parser.error(str(erro))
    return 2


if __name__ == "__main__":
    sys.exit(main())
