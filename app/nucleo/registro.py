"""Registro em SQLite. Os alunos têm só apelido, avatar e perfis: nunca nome completo nem foto.

A tabela de tentativas entra na Etapa 3.
"""

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from app.nucleo import caminhos
from app.nucleo.perfis import ler_lista

AVATARES = ("gato", "cachorro", "peixe", "passaro", "sapo", "tartaruga")
TAMANHO_MAX_APELIDO = 20


@dataclass(frozen=True)
class Aluno:
    id: int
    apelido: str
    avatar: str
    perfis: list[str] = field(default_factory=list)


class Registro:
    def __init__(self, caminho: str | Path | None = None):
        if caminho is None:
            pasta = caminhos.dados()
            pasta.mkdir(parents=True, exist_ok=True)
            caminho = pasta / "atlas.db"
        self.conexao = sqlite3.connect(str(caminho))
        self.conexao.execute(
            """CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY,
                apelido TEXT NOT NULL UNIQUE,
                avatar TEXT NOT NULL,
                perfis TEXT NOT NULL DEFAULT ''
            )"""
        )
        self.conexao.commit()

    def fechar(self) -> None:
        self.conexao.close()

    def listar_alunos(self) -> list[Aluno]:
        linhas = self.conexao.execute(
            "SELECT id, apelido, avatar, perfis FROM alunos ORDER BY apelido COLLATE NOCASE"
        )
        return [Aluno(i, a, av, ler_lista(p)) for i, a, av, p in linhas]

    def salvar_aluno(self, apelido: str, avatar: str, perfis, id: int | None = None) -> Aluno:
        apelido = " ".join(apelido.split())
        if not apelido:
            raise ValueError("apelido vazio")
        if len(apelido) > TAMANHO_MAX_APELIDO:
            raise ValueError(f"apelido com mais de {TAMANHO_MAX_APELIDO} letras")
        if avatar not in AVATARES:
            raise ValueError(f"avatar desconhecido: {avatar}")
        perfis = ler_lista(",".join(perfis))
        texto_perfis = ",".join(perfis)
        try:
            if id is None:
                cursor = self.conexao.execute(
                    "INSERT INTO alunos (apelido, avatar, perfis) VALUES (?, ?, ?)",
                    (apelido, avatar, texto_perfis),
                )
                id = cursor.lastrowid
            else:
                self.conexao.execute(
                    "UPDATE alunos SET apelido = ?, avatar = ?, perfis = ? WHERE id = ?",
                    (apelido, avatar, texto_perfis, id),
                )
        except sqlite3.IntegrityError as erro:
            raise ValueError(f"já existe um aluno com o apelido {apelido}") from erro
        self.conexao.commit()
        return Aluno(id, apelido, avatar, perfis)

    def apagar_aluno(self, id: int) -> None:
        self.conexao.execute("DELETE FROM alunos WHERE id = ?", (id,))
        self.conexao.commit()
