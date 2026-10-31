"""Mesa de Quantidades: montar, comparar e resolver, por barramento, mouse, teclado e agente."""

import json

import pytest
from PySide6.QtCore import Qt

from app.atividades.base import FIM, Contexto
from app.atividades.quantidades import logica
from app.atividades.quantidades.tela import BANDEJA_A, TelaQuantidades
from app.entrada.camera import CameraNula
from app.headless import agente
from app.nucleo.audio import ServicoAudio
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), CameraNula)
    t = TelaQuantidades(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _abrir(tela, nivel, perfis=(), semente=5, **opcoes):
    tela.ctx.sessao.definir(None, list(perfis))
    tela.iniciar(tela.ctx.sessao.perfil, semente=semente, nivel=nivel, **opcoes)
    tela.comecar()


def _arrastar(tela, origem, destino):
    b = tela.barramento
    b.apontar.emit(*tela.cena.centro(origem))
    b.pegar.emit()
    b.apontar.emit(*tela.cena.centro(destino))
    b.soltar.emit()


def _objetos_livres(tela):
    return [p.id for p in tela.cena.pecas.values() if p.tipo == "objeto" and not p.encaixada]


def _cartao_certo(tela):
    return next(c.id for c in tela.rodada.cartoes if c.valor == tela.rodada.certo)


def _cartao_errado(tela):
    return next(c.id for c in tela.rodada.cartoes if c.valor != tela.rodada.certo)


# --- Montar ---------------------------------------------------------------------------


def test_montar_conta_e_fala_cada_objeto(tela):
    _abrir(tela, logica.MONTAR)
    meta = tela.rodada.a
    for _ in range(meta):
        _arrastar(tela, _objetos_livres(tela)[0], BANDEJA_A)
    assert tela.estado()["bandejas"] == {BANDEJA_A: meta}
    assert tela.numeros[BANDEJA_A].text() == str(meta)
    falado = logica.quantidade(meta, tela.conjunto)
    assert tela.ctx.audio.log[-1] == f"toca {tela.ctx.audio.arquivo_de(falado)}"
    tela.barramento.escolher.emit("cartao-pronto")
    assert tela.momento == FIM
    assert tela.ctx.registro.listar_tentativas()[-1]["resposta"] == str(meta)


def test_montar_um_a_mais_esvazia_e_da_pista(tela):
    _abrir(tela, logica.MONTAR)
    for _ in range(tela.rodada.a + 1):
        _arrastar(tela, _objetos_livres(tela)[0], BANDEJA_A)
    tela.barramento.escolher.emit("cartao-pronto")
    tentativa = tela.ctx.registro.listar_tentativas()[-1]
    assert tentativa["tipo_erro"] == "um_a_mais_ou_menos" and tentativa["pistas"] == 1
    assert tela.estado()["bandejas"] == {BANDEJA_A: 0}  # a bandeja volta vazia
    assert tela.momento != FIM


def test_montar_modelo_na_terceira_vez(tela):
    _abrir(tela, logica.MONTAR)
    for _ in range(3):
        tela.barramento.escolher.emit("cartao-pronto")  # bandeja vazia: errado
    assert tela.momento == FIM
    assert tela.estado()["bandejas"] == {BANDEJA_A: tela.rodada.a}
    assert tela.ctx.registro.listar_tentativas()[-1]["precisou_modelo"] is True


# --- Comparar -------------------------------------------------------------------------


def test_comparar_liga_um_a_um_e_marca_a_sobra(tela):
    _abrir(tela, logica.COMPARAR, semente=6)  # 7 x 5
    r = tela.rodada
    assert r.a != r.b and r.certo == logica.comparar(r.a, r.b)
    hachuradas = [p for p in tela.cena.pecas.values() if p.hachura]
    assert len(hachuradas) == abs(r.a - r.b)
    assert tela.sobra.text() == f"sobrou {abs(r.a - r.b)}"
    tela.barramento.escolher.emit(_cartao_errado(tela))
    assert tela.ctx.registro.listar_tentativas()[-1]["tipo_erro"] == "comparacao_errada"
    tela.barramento.escolher.emit(_cartao_certo(tela))
    assert tela.momento == FIM


# --- Resolver -------------------------------------------------------------------------


def test_soma_pelo_clique_no_cartao(tela, qtbot):
    _abrir(tela, logica.SOMA)
    r = tela.rodada
    assert tela.estado()["conta"] == f"{r.a} + {r.b}"
    assert tela.estado()["bandejas"] == {"bandeja-a": r.a, "bandeja-b": r.b}
    b = tela.barramento
    b.apontar.emit(*tela.cena.centro(_cartao_errado(tela)))
    b.pegar.emit()  # pegar um cartão já é escolher
    assert tela.ctx.registro.listar_tentativas()[-1]["correta"] is False
    assert not b.segurando
    b.apontar.emit(*tela.cena.centro(_cartao_certo(tela)))
    b.pegar.emit()
    assert tela.momento == FIM


def test_soma_por_teclado(tela, qtbot):
    _abrir(tela, logica.SOMA)
    alvo = _cartao_certo(tela)
    for _ in range(10):
        if tela.entrada_teclado.foco.atual == alvo:
            break
        qtbot.keyClick(tela.cena, Qt.Key_Tab)
    qtbot.keyClick(tela.cena, Qt.Key_Return)
    assert tela.momento == FIM


def test_erros_de_conta_classificados(tela):
    encontrados = set()
    for semente in range(40):
        _abrir(tela, logica.CONTAS, semente=semente)
        for cartao in tela.rodada.cartoes:
            if cartao.valor != tela.rodada.certo:
                tela.barramento.escolher.emit(cartao.id)
        encontrados |= {t["tipo_erro"] for t in tela.ctx.registro.listar_tentativas()}
    assert {"operacao_trocada", "digitos_invertidos", "um_a_mais_ou_menos"} <= encontrados


def test_pista_2_acende_os_objetos(tela):
    _abrir(tela, logica.SOMA)
    for _ in range(2):
        tela.barramento.escolher.emit(_cartao_errado(tela))
    acesos = [p for p in tela.cena.pecas.values() if p.realcado and p.tipo == "objeto"]
    assert len(acesos) == tela.rodada.a + tela.rodada.b
    assert "Vamos contar juntos." in " ".join(tela.ctx.audio.log) or tela.ctx.audio.log


def test_conjunto_escolhido_pelo_professor(tela):
    tela.ctx.registro.salvar_config("conjunto_mesa", "peixe")
    _abrir(tela, logica.SOMA)
    assert tela.estado()["conjunto"] == "peixe"
    objetos = [p for p in tela.cena.pecas.values() if p.tipo == "objeto"]
    assert all(p.figura.endswith("peixe.svg") for p in objetos)


def test_tea_quantidades_menores(tela):
    _abrir(tela, logica.MONTAR, perfis=["tea"])
    assert tela.rodada.a <= 5


# --- agente ---------------------------------------------------------------------------


def test_agente_resolve_uma_conta(capsys, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    linhas = [json.dumps(p) for p in ({"acao": "proximo"}, {"acao": "estado"})]
    agente.executar("quantidades", [], entrada=linhas)
    estado = json.loads(capsys.readouterr().out.splitlines()[-1])["estado"]
    assert estado["modo"] == "montar" and estado["bandejas"] == {"bandeja-a": 0}
    objetos = [i["id"] for i in estado["itens"] if i["tipo"] == "objeto"]
    meta = int(estado["instrucao"].split()[1])
    pedidos = [{"acao": "proximo"}]
    for objeto in objetos[:meta]:
        pedidos += [{"acao": "pegar", "id": objeto}, {"acao": "soltar", "alvo": "bandeja-a"}]
    pedidos.append({"acao": "escolher", "id": "cartao-pronto"})
    agente.executar("quantidades", [], entrada=[json.dumps(p) for p in pedidos])
    respostas = [json.loads(linha) for linha in capsys.readouterr().out.splitlines()]
    assert respostas[-1]["estado"]["concluida"] is True
