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


def test_demo_gera_evidencias(tmp_path):
    saida = tmp_path / "saida"
    assert cli.main(["demo", "todas", "--saida", str(saida), "--tamanho", "1024x700"]) == 0

    capturas = sorted(p.name for p in saida.glob("captura-*.png"))
    assert capturas[0] == "captura-01-inicio.png"
    assert len(capturas) >= 3
    relatorio = (saida / "relatorio.md").read_text(encoding="utf-8")
    for captura in capturas:
        assert captura in relatorio
    linhas = (saida / "eventos.jsonl").read_text("utf-8").splitlines()
    eventos = [json.loads(linha) for linha in linhas]
    assert len(eventos) == len(capturas)
    assert json.loads((saida / "tentativas.json").read_text("utf-8")) == []
    assert (saida / "audio.log").exists()


def test_demo_roteiro_invalido():
    with pytest.raises(SystemExit):
        cli.main(["demo", "nao-existe"])
