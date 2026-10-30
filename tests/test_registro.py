import pytest

from app.nucleo.registro import AVATARES, Registro
from app.nucleo.sessao import Sessao


@pytest.fixture
def registro():
    r = Registro(":memory:")
    yield r
    r.fechar()


def test_seis_avatares_com_figura():
    from app.nucleo import caminhos

    assert len(AVATARES) == 6
    for avatar in AVATARES:
        assert caminhos.asset("figuras", "avatares", f"{avatar}.svg").exists()


def test_salvar_listar_editar_apagar(registro):
    ana = registro.salvar_aluno("  Ana   B ", "gato", ["tea", "dislexia"])
    assert ana.apelido == "Ana B"
    registro.salvar_aluno("Beto", "sapo", [])
    assert [a.apelido for a in registro.listar_alunos()] == ["Ana B", "Beto"]

    registro.salvar_aluno("Ana", "peixe", ["motor"], id=ana.id)
    editada = registro.listar_alunos()[0]
    assert (editada.apelido, editada.avatar, editada.perfis) == ("Ana", "peixe", ["motor"])

    registro.apagar_aluno(ana.id)
    assert [a.apelido for a in registro.listar_alunos()] == ["Beto"]


@pytest.mark.parametrize(
    ("apelido", "avatar", "perfis", "mensagem"),
    [
        ("", "gato", [], "vazio"),
        ("x" * 21, "gato", [], "20"),
        ("Ana", "dragao", [], "avatar"),
        ("Ana", "gato", ["nao_existe"], "perfil"),
    ],
)
def test_validacao(registro, apelido, avatar, perfis, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        registro.salvar_aluno(apelido, avatar, perfis)


def test_apelido_repetido(registro):
    registro.salvar_aluno("Ana", "gato", [])
    with pytest.raises(ValueError, match="já existe"):
        registro.salvar_aluno("Ana", "sapo", [])


def test_tabela_nao_tem_nome_completo_nem_foto(registro):
    colunas = {linha[1] for linha in registro.conexao.execute("PRAGMA table_info(alunos)")}
    assert colunas == {"id", "apelido", "avatar", "perfis"}


def test_sessao_combina_perfis_do_aluno(registro, qtbot):
    aluno = registro.salvar_aluno("Ana", "gato", ["tea", "baixa_visao"])
    sessao = Sessao()
    with qtbot.waitSignal(sessao.mudou):
        sessao.definir(aluno)
    assert sessao.perfil.max_itens == 3 and sessao.perfil.escala == 1.75
    sessao.definir(None, ["dislexia"])
    assert sessao.perfil.espacamento_letras == 0.12
    sessao.definir(None)
    assert sessao.perfis == []


def _tentativa(**mudancas):
    from app.nucleo.registro import Tentativa

    dados = dict(
        aluno="Ana", atividade="treino", habilidade="reconhecer letras", item="A",
        resposta="B", correta=False, tipo_erro="letra_trocada", pistas=1,
        precisou_modelo=False, tempo_ms=2300, modo_entrada="mouse", perfis=["tea"],
    )
    dados.update(mudancas)
    return Tentativa(**dados)


def test_tentativas_tem_os_campos_da_especificacao(registro):
    colunas = {linha[1] for linha in registro.conexao.execute("PRAGMA table_info(tentativas)")}
    assert colunas == {
        "id", "aluno", "atividade", "habilidade", "item", "resposta", "correta", "tipo_erro",
        "pistas", "precisou_modelo", "tempo_ms", "modo_entrada", "perfis", "ts",
    }


def test_salvar_e_listar_tentativas(registro):
    registro.salvar_tentativa(_tentativa())
    registro.salvar_tentativa(_tentativa(aluno="Beto", correta=True, tipo_erro=None))
    todas = registro.listar_tentativas()
    assert len(todas) == 2
    assert todas[0]["correta"] is False and todas[0]["perfis"] == ["tea"]
    assert todas[0]["ts"]  # preenchido na hora
    assert [t["aluno"] for t in registro.listar_tentativas("Beto")] == ["Beto"]


def test_exportar_e_apagar_tudo(registro, tmp_path):
    registro.salvar_aluno("Ana", "gato", ["tea"])
    registro.salvar_tentativa(_tentativa())
    registro.salvar_config("volume", "0.5")
    arquivo = registro.exportar_json(tmp_path / "atlas.json")
    import json

    dados = json.loads(arquivo.read_text("utf-8"))
    assert dados["alunos"][0]["apelido"] == "Ana"
    assert dados["tentativas"][0]["tipo_erro"] == "letra_trocada"

    registro.apagar_tudo()
    assert registro.listar_alunos() == [] and registro.listar_tentativas() == []
    assert registro.ler_config("volume", "1.0") == "1.0"


def test_config(registro):
    assert registro.ler_config("volume", "0.8") == "0.8"
    registro.salvar_config("volume", "0.3")
    registro.salvar_config("volume", "0.4")
    assert registro.ler_config("volume", "0.8") == "0.4"
