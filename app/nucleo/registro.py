"""Registro em SQLite. Os alunos têm só apelido, avatar e perfis: nunca nome completo nem foto.

Cada jogada da criança vira uma linha em `tentativas`; o painel do professor lê daqui.
"""

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from app.nucleo import caminhos
from app.nucleo.perfis import ler_lista

AVATARES = ("gato", "cachorro", "peixe", "passaro", "sapo", "tartaruga")
TAMANHO_MAX_APELIDO = 20
VISITANTE = "visitante"  # nome gravado nas tentativas de quem joga sem cadastro


@dataclass(frozen=True)
class Aluno:
    id: int
    apelido: str
    avatar: str
    perfis: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Tentativa:
    aluno: str  # apelido, ou "visitante"
    atividade: str
    habilidade: str
    item: str
    resposta: str
    correta: bool
    tipo_erro: str | None
    pistas: int
    precisou_modelo: bool
    tempo_ms: int
    modo_entrada: str
    perfis: list[str]
    ts: str = ""


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
        self.conexao.execute(
            """CREATE TABLE IF NOT EXISTS tentativas (
                id INTEGER PRIMARY KEY,
                aluno TEXT NOT NULL,
                atividade TEXT NOT NULL,
                habilidade TEXT NOT NULL,
                item TEXT NOT NULL,
                resposta TEXT NOT NULL,
                correta INTEGER NOT NULL,
                tipo_erro TEXT,
                pistas INTEGER NOT NULL,
                precisou_modelo INTEGER NOT NULL,
                tempo_ms INTEGER NOT NULL,
                modo_entrada TEXT NOT NULL,
                perfis TEXT NOT NULL,
                ts TEXT NOT NULL
            )"""
        )
        self.conexao.execute(
            "CREATE TABLE IF NOT EXISTS config (chave TEXT PRIMARY KEY, valor TEXT NOT NULL)"
        )
        self.conexao.commit()

    def fechar(self) -> None:
        self.conexao.close()

    # --- tentativas ----------------------------------------------------------------

    def salvar_tentativa(self, t: "Tentativa") -> None:
        dados = asdict(t)
        dados["perfis"] = ",".join(t.perfis)
        dados["ts"] = t.ts or datetime.now().isoformat(timespec="seconds")
        colunas = ", ".join(dados)
        marcas = ", ".join("?" for _ in dados)
        self.conexao.execute(
            f"INSERT INTO tentativas ({colunas}) VALUES ({marcas})", tuple(dados.values())
        )
        self.conexao.commit()

    def listar_tentativas(self, aluno: str | None = None) -> list[dict]:
        sql = "SELECT * FROM tentativas"
        args: tuple = ()
        if aluno is not None:
            sql += " WHERE aluno = ?"
            args = (aluno,)
        cursor = self.conexao.execute(sql + " ORDER BY id", args)
        nomes = [c[0] for c in cursor.description]
        linhas = []
        for valores in cursor:
            linha = dict(zip(nomes, valores, strict=True))
            linha["correta"] = bool(linha["correta"])
            linha["precisou_modelo"] = bool(linha["precisou_modelo"])
            linha["perfis"] = [p for p in linha["perfis"].split(",") if p]
            linhas.append(linha)
        return linhas

    # --- configurações ------------------------------------------------------------

    def ler_config(self, chave: str, padrao: str) -> str:
        sql = "SELECT valor FROM config WHERE chave = ?"
        linha = self.conexao.execute(sql, (chave,)).fetchone()
        return linha[0] if linha else padrao

    def salvar_config(self, chave: str, valor: str) -> None:
        self.conexao.execute(
            "INSERT INTO config (chave, valor) VALUES (?, ?) "
            "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
            (chave, valor),
        )
        self.conexao.commit()

    # --- exportar e apagar -------------------------------------------------------

    def exportar(self) -> dict:
        return {
            "alunos": [asdict(a) for a in self.listar_alunos()],
            "tentativas": self.listar_tentativas(),
        }

    def exportar_json(self, destino: str | Path) -> Path:
        destino = Path(destino)
        destino.write_text(
            json.dumps(self.exportar(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return destino

    def apagar_tudo(self) -> None:
        """Apaga alunos, tentativas e configurações. Não tem volta."""
        for tabela in ("tentativas", "alunos", "config"):
            self.conexao.execute(f"DELETE FROM {tabela}")
        self.conexao.commit()

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
        if apelido.casefold() == VISITANTE:  # misturaria o histórico com o do visitante
            raise ValueError(f"o apelido {apelido} é reservado")
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
                antigo = self._apelido_de(id)
                self.conexao.execute(
                    "UPDATE alunos SET apelido = ?, avatar = ?, perfis = ? WHERE id = ?",
                    (apelido, avatar, texto_perfis, id),
                )
                # As tentativas guardam o apelido: trocar o apelido leva o histórico junto.
                if antigo is not None and antigo != apelido:
                    self.conexao.execute(
                        "UPDATE tentativas SET aluno = ? WHERE aluno = ?", (apelido, antigo)
                    )
        except sqlite3.IntegrityError as erro:
            self.conexao.rollback()
            raise ValueError(f"já existe um aluno com o apelido {apelido}") from erro
        self.conexao.commit()
        return Aluno(id, apelido, avatar, perfis)

    def _apelido_de(self, id: int) -> str | None:
        linha = self.conexao.execute("SELECT apelido FROM alunos WHERE id = ?", (id,)).fetchone()
        return linha[0] if linha else None

    def apagar_aluno(self, id: int) -> None:
        """Apaga o aluno e as tentativas dele: senão o painel seguiria mostrando quem foi
        apagado, e um aluno novo com o mesmo apelido herdaria esse histórico."""
        apelido = self._apelido_de(id)
        if apelido is not None:
            self.conexao.execute("DELETE FROM tentativas WHERE aluno = ?", (apelido,))
        self.conexao.execute("DELETE FROM alunos WHERE id = ?", (id,))
        self.conexao.commit()
