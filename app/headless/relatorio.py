"""Gera o `relatorio.md` de uma execução do `atlas demo`."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Passo:
    numero: int
    nome: str
    evento: str
    frase: str
    captura: str
    tipo_erro: str = ""
    pista: str = ""


def _celula(valor: str) -> str:
    return (valor or "—").replace("|", "\\|")


def escrever(destino: Path, titulo: str, passos: list[Passo]) -> None:
    linhas = [
        f"# {titulo}",
        "",
        "| Passo | Evento | Frase narrada | Captura | Tipo de erro | Pista |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for p in passos:
        captura = f"[{p.captura}]({p.captura})"
        linhas.append(
            f"| {p.numero:02d} {_celula(p.nome)} | {_celula(p.evento)} | {_celula(p.frase)} "
            f"| {captura} | {_celula(p.tipo_erro)} | {_celula(p.pista)} |"
        )
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
