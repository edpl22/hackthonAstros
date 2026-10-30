"""Protocolo do agente (JSON Lines): a IA joga a atividade só com stdin e stdout."""

import json

import pytest

from app.headless import agente


@pytest.fixture(autouse=True)
def sem_animacao(monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")


def _conversar(capsys, pedidos, atividade="treino", perfis=()):
    linhas = [p if isinstance(p, str) else json.dumps(p) for p in pedidos]
    codigo = agente.executar(atividade, list(perfis), entrada=linhas)
    respostas = [json.loads(linha) for linha in capsys.readouterr().out.splitlines()]
    return codigo, respostas


def test_primeira_linha_anuncia_as_acoes(capsys):
    codigo, respostas = _conversar(capsys, [{"acao": "sair"}])
    assert codigo == 0
    assert respostas[0] == {"pronto": True, "atividade": "treino", "acoes": agente.ACOES}
    assert respostas[-1]["ok"] is True


def test_completa_o_treino_pelo_agente(capsys):
    pedidos = [{"acao": "proximo"}]  # Começar
    for i, letra in enumerate("abcd"):
        pedidos += [{"acao": "pegar", "id": f"peca-{letra}-{i}"},
                    {"acao": "soltar", "alvo": f"caixa-{i + 1}"}]
    pedidos += [{"acao": "estado"}, {"acao": "sair"}]
    _, respostas = _conversar(capsys, pedidos)
    assert all(r["ok"] for r in respostas[1:])
    assert respostas[3]["anuncio"] == "Letra A colocada na caixa da letra A."
    final = respostas[-2]["estado"]
    assert final["concluida"] and final["momento"] == "fim"
    assert final["oferece_desafio"] is True  # 4 acertos de primeira
    assert final["modo_entrada"] == "agente"


def test_erro_proposital_recebe_pista(capsys):
    pedidos = [
        {"acao": "proximo"},
        {"acao": "pegar", "id": "peca-b-1"},
        {"acao": "soltar", "alvo": "caixa-1"},
    ]
    _, respostas = _conversar(capsys, pedidos)
    resposta = respostas[-1]
    assert resposta["anuncio"].startswith("A letra B voltou para o lugar. Vamos tentar de novo.")
    assert resposta["estado"]["pista_nivel"] == 1


def test_estado_tem_ids_estaveis(capsys):
    _, respostas = _conversar(capsys, [{"acao": "estado"}], perfis=["tea"])
    estado = respostas[1]["estado"]
    assert [i["id"] for i in estado["itens"]] == ["peca-a-0", "peca-b-1", "peca-c-2"]
    assert [a["id"] for a in estado["alvos"]] == ["caixa-1", "caixa-2", "caixa-3"]
    assert estado["momento"] == "apresentacao"


@pytest.mark.parametrize(
    ("pedido", "trecho_erro", "trecho_dica"),
    [
        ({"acao": "voar"}, "acao desconhecida", "estado"),
        ({"acao": "pegar", "id": "peca-x"}, "item inexistente: peca-x", "peca-a-0"),
        ({"acao": "soltar", "alvo": "caixa-9"}, "alvo inexistente: caixa-9", "caixa-1"),
        ({"acao": "apontar"}, "pedido incompleto", "README"),
        ("isto nao e json", "JSON invalido", "estado"),
        ("[1, 2]", "objeto JSON", "estado"),
    ],
)
def test_erros_explicam_o_que_fazer(capsys, pedido, trecho_erro, trecho_dica):
    _, respostas = _conversar(capsys, [{"acao": "proximo"}, pedido])
    erro = respostas[-1]
    assert erro["ok"] is False
    assert trecho_erro in erro["erro"] and trecho_dica in erro["dica"]


def test_pegar_antes_de_comecar_explica(capsys):
    _, respostas = _conversar(capsys, [{"acao": "pegar", "id": "peca-a-0"}])
    assert "proximo" in respostas[-1]["dica"]


def test_pausa_pelo_agente(capsys):
    pedidos = [{"acao": "proximo"}, {"acao": "pausar"},
               {"acao": "pegar", "id": "peca-a-0"}, {"acao": "continuar"}]
    _, respostas = _conversar(capsys, pedidos)
    assert respostas[2]["estado"]["pausada"] is True
    assert respostas[3]["estado"]["itens"][0]["disponivel"]  # nada mudou na pausa
    assert respostas[4]["estado"]["pausada"] is False


def test_captura(capsys, tmp_path):
    arquivo = tmp_path / "passo.png"
    _, respostas = _conversar(capsys, [{"acao": "captura", "arquivo": str(arquivo)}])
    assert respostas[-1]["ok"] and arquivo.stat().st_size > 1000


def test_atividade_inexistente(capsys):
    codigo, respostas = _conversar(capsys, [], atividade="xadrez")
    assert codigo == 1
    assert respostas[0]["ok"] is False and "treino" in respostas[0]["dica"]
