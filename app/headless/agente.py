"""`atlas agente <atividade>`: joga uma atividade por JSON Lines (stdin -> stdout), sem tela.

É um adaptador fino: cada pedido vira um evento do barramento (o mesmo que o mouse ou a mão
emitiriam) e a resposta traz a frase narrada e o `estado()` da atividade. Nenhuma regra é
reimplementada aqui.

Pedidos (um JSON por linha):
    {"acao": "estado"}
    {"acao": "pegar", "id": "peca-a-0"}
    {"acao": "soltar", "alvo": "caixa-1"}
    {"acao": "escolher", "id": "cartao-7"}
    {"acao": "apontar", "x": 640, "y": 360}
    {"acao": "pausar"} / {"acao": "continuar"}
    {"acao": "proximo"}          # "Começar", "Próximo" ou responde ao desafio com {"sim": true}
    {"acao": "captura", "arquivo": "passo1.png"}
    {"acao": "sair"}
"""

import json
import os
import sys

from PySide6.QtWidgets import QApplication

from app.entrada.camera import CameraNula
from app.janela import JanelaPrincipal
from app.nucleo import tema
from app.nucleo.audio import ServicoAudio
from app.nucleo.registro import Registro

ACOES = [
    "estado", "apontar", "pegar", "soltar", "escolher",
    "pausar", "continuar", "captura", "proximo", "sair",
]


class Erro(Exception):
    def __init__(self, erro: str, dica: str = ""):
        super().__init__(erro)
        self.erro, self.dica = erro, dica


class Agente:
    def __init__(
        self, atividade: str, perfis: list[str], semente: int | None = 7, palavra: str | None = None
    ):
        self.app = QApplication.instance() or QApplication([])
        tema.aplicar(self.app)
        self.janela = JanelaPrincipal(
            fabrica_camera=CameraNula,
            registro=Registro(":memory:"),
            audio=ServicoAudio(backend="nulo"),
        )
        self.janela.resize(1280, 720)
        self.janela.show()
        disponiveis = list(self.janela.atividades)
        if atividade not in disponiveis or atividade == "teste_camera":
            jogaveis = [a for a in disponiveis if a != "teste_camera"]
            raise Erro(f"atividade inexistente: {atividade}", f"disponiveis: {', '.join(jogaveis)}")
        self.janela.escolher_aluno(None, perfis)
        opcoes = {}
        if atividade == "silabas":
            opcoes["palavra"] = palavra or "bola"  # começo previsível para o README
        self.janela.abrir_atividade(atividade, semente=semente, **opcoes)
        self.atividade = self.janela.atividades[atividade]
        self.nome = atividade
        self._processar()

    def _processar(self) -> None:
        for _ in range(3):
            self.app.processEvents()

    # --- ações ------------------------------------------------------------------------

    def _ids(self) -> tuple[dict, dict]:
        estado = self.atividade.estado()
        return (
            {i["id"]: i for i in estado.get("itens", [])},
            {a["id"]: a for a in estado.get("alvos", [])},
        )

    def _exigir_atividade(self) -> None:
        if self.atividade.momento != "atividade":
            raise Erro(
                f"a atividade esta no momento '{self.atividade.momento}'",
                "use {\"acao\": \"proximo\"} para comecar ou seguir",
            )

    def executar(self, pedido: dict) -> dict:
        acao = pedido.get("acao")
        if acao not in ACOES:
            raise Erro(f"acao desconhecida: {acao}", f"acoes: {', '.join(ACOES)}")
        b = self.atividade.barramento
        b.usar("agente")
        antes = self.atividade.ultimo_anuncio
        if acao == "apontar":
            b.apontar.emit(float(pedido["x"]), float(pedido["y"]))
        elif acao == "pegar":
            self._exigir_atividade()
            itens, _ = self._ids()
            id_ = pedido.get("id")
            if id_ not in itens:
                raise Erro(f"item inexistente: {id_}", f"ids disponiveis: {', '.join(itens)}")
            b.apontar.emit(*self.atividade.area.centro(id_))
            b.pegar.emit()
        elif acao == "soltar":
            self._exigir_atividade()
            _, alvos = self._ids()
            alvo = pedido.get("alvo")
            if alvo not in alvos:
                raise Erro(f"alvo inexistente: {alvo}", f"alvos disponiveis: {', '.join(alvos)}")
            b.apontar.emit(*self.atividade.area.centro(alvo))
            b.soltar.emit()
        elif acao == "escolher":
            self._exigir_atividade()
            b.escolher.emit(str(pedido.get("id")))
        elif acao == "pausar":
            self.atividade.pausar()
        elif acao == "continuar":
            self.atividade.continuar()
        elif acao == "proximo":
            if self.atividade.momento == "apresentacao":
                self.atividade.comecar()
            elif self.atividade.oferece_desafio:
                self.atividade.responder_desafio(bool(pedido.get("sim", False)))
            else:
                self.atividade.proximo()
        elif acao == "captura":
            arquivo = pedido.get("arquivo", "captura.png")
            self._processar()
            self.janela.grab().save(arquivo)
        self._processar()
        anuncio = self.atividade.ultimo_anuncio
        return {
            "ok": True,
            "anuncio": anuncio if anuncio != antes else "",
            "estado": self.atividade.estado(),
        }


def _escrever(dados: dict) -> None:
    sys.stdout.write(json.dumps(dados, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def executar(atividade: str, perfis: list[str], entrada=None, palavra: str | None = None) -> int:
    os.environ["ATLAS_SEM_ANIMACAO"] = "1"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # acentos iguais no Windows e no Linux
    try:
        agente = Agente(atividade, perfis, palavra=palavra)
    except Erro as erro:
        _escrever({"ok": False, "erro": erro.erro, "dica": erro.dica})
        return 1
    except StopIteration:
        _escrever({"ok": False, "erro": f"palavra inexistente: {palavra}",
                   "dica": "palavras: bola, casa, pato, gato, sapo, vaca, macaco, sapato, "
                           "boneca, janela, tomate, braco, prato, passaro, livro"})
        return 1
    _escrever({"pronto": True, "atividade": agente.nome, "acoes": ACOES})
    for linha in entrada or sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            pedido = json.loads(linha)
            if not isinstance(pedido, dict):
                raise Erro("pedido precisa ser um objeto JSON", '{"acao": "estado"}')
            if pedido.get("acao") == "sair":
                _escrever({"ok": True, "anuncio": "Ate logo."})
                break
            _escrever(agente.executar(pedido))
        except json.JSONDecodeError as erro:
            exemplo = '{"acao": "estado"}'
            _escrever({"ok": False, "erro": f"JSON invalido: {erro.msg}", "dica": exemplo})
        except Erro as erro:
            _escrever({"ok": False, "erro": erro.erro, "dica": erro.dica})
        except (KeyError, TypeError, ValueError) as erro:
            _escrever({"ok": False, "erro": f"pedido incompleto: {erro}", "dica": "veja o README"})
    agente.janela.close()
    return 0
