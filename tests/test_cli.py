import json

import pytest

from app import cli


@pytest.fixture(autouse=True)
def dados_temporarios(tmp_path, monkeypatch):
    monkeypatch.setenv("ATLAS_DADOS", str(tmp_path / "dados"))


def test_verificar_pronto(capsys):
    assert cli.main(["verificar"]) == 0
    saida = capsys.readouterr().out
    assert saida.strip().endswith("RESULTADO: pronto")
    assert "FALHA" not in saida
    assert saida.isascii()


def test_verificar_falha_sem_banco(capsys, monkeypatch, tmp_path):
    arquivo = tmp_path / "nao-e-pasta"
    arquivo.write_text("x")
    monkeypatch.setenv("ATLAS_DADOS", str(arquivo))
    assert cli.main(["verificar"]) == 1
    assert "RESULTADO: com falhas" in capsys.readouterr().out


def test_perfis_lista_todos_e_as_regras(capsys):
    assert cli.main(["perfis"]) == 0
    dados = json.loads(capsys.readouterr().out)
    assert len(dados["perfis"]) == 8
    assert "velocidade" in dados["regras"]["menor vence"]


def test_perfis_combinar(capsys):
    assert cli.main(["perfis", "--combinar", "tea,dislexia"]) == 0
    dados = json.loads(capsys.readouterr().out)
    assert dados["combinacao"] == ["tea", "dislexia"]
    assert dados["resultado"]["velocidade"] == 0
    assert dados["resultado"]["escala"] == 1.2


def test_perfil_desconhecido_e_erro_claro(capsys):
    with pytest.raises(SystemExit):
        cli.main(["perfis", "--combinar", "tea,xyz"])
    assert "perfil desconhecido: xyz" in capsys.readouterr().err


def _ler_eventos(pasta):
    linhas = (pasta / "eventos.jsonl").read_text("utf-8").splitlines()
    return [json.loads(linha) for linha in linhas]


def test_demo_gera_evidencias(tmp_path):
    saida = tmp_path / "saida"
    assert cli.main(["demo", "todas", "--saida", str(saida), "--tamanho", "1024x700"]) == 0

    capturas = sorted(p.name for p in saida.glob("captura-*.png"))
    assert capturas[0] == "captura-01-inicio.png"
    assert len(capturas) == 13
    relatorio = (saida / "relatorio.md").read_text(encoding="utf-8")
    for captura in capturas:
        assert captura in relatorio
    # O erro proposital aparece no relatório com o tipo de erro e as duas pistas.
    assert "letra_trocada" in relatorio
    assert "1 - repetir a instrucao" in relatorio and "2 - realcar" in relatorio
    eventos = _ler_eventos(saida)
    assert eventos[-1] == {"n": len(eventos), "roteiro": "treino", "evento": "estado_final",
                           "concluida": True}
    tentativas = json.loads((saida / "tentativas.json").read_text("utf-8"))
    assert [t["correta"] for t in tentativas] == [False, False, True, True, True, True]
    assert tentativas[0]["tipo_erro"] == "letra_trocada" and tentativas[1]["pistas"] == 2
    audio = (saida / "audio.log").read_text("utf-8").splitlines()
    assert audio and all(linha.startswith("toca ") for linha in audio)


@pytest.mark.parametrize("entrada", ["teclado", "varredura", "mao-simulada"])
def test_demo_treino_com_cada_entrada(tmp_path, entrada):
    saida = tmp_path / entrada
    assert cli.main(["demo", "treino", "--entrada", entrada, "--saida", str(saida)]) == 0
    eventos = _ler_eventos(saida)
    assert eventos[-1]["concluida"] is True
    assert any("voltou" in e.get("anuncio", "") for e in eventos)


def test_demo_com_perfil(tmp_path):
    saida = tmp_path / "tea"
    assert cli.main(["demo", "treino", "--perfil", "tea", "--saida", str(saida)]) == 0
    assert "perfil: tea" in (saida / "relatorio.md").read_text("utf-8")


def test_demo_roteiro_invalido():
    with pytest.raises(SystemExit):
        cli.main(["demo", "nao-existe"])
