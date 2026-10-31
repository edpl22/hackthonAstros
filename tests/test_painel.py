from app.nucleo import painel, turma_demo
from app.nucleo.registro import Registro


def _t(item, correta, tipo=None, modelo=False, habilidade="h", aluno="Ana"):
    return {"aluno": aluno, "habilidade": habilidade, "item": item, "correta": correta,
            "tipo_erro": tipo, "precisou_modelo": modelo}


def test_agrupa_tentativas_seguidas_no_mesmo_item():
    itens = painel.agrupar_itens([_t("a", False, "x"), _t("a", True), _t("a", True), _t("b", True)])
    assert [len(i) for i in itens] == [2, 1, 1]  # "a" repetido depois de acertar é outro item


def test_domina_com_80_por_cento_na_primeira():
    lista = [_t(f"i{n}", n < 8) for n in range(10)]
    assert painel.situacao(lista).estado == painel.DOMINA


def test_precisa_apoio_abaixo_de_50():
    lista = [_t(f"i{n}", n < 4, None if n < 4 else "somou_denominadores") for n in range(10)]
    s = painel.situacao(lista)
    assert s.estado == painel.PRECISA_APOIO and s.tipo_erro == "somou_denominadores"
    assert (s.vezes, s.tentativas) == (6, 10)


def test_precisa_apoio_com_dois_modelos():
    lista = [_t(f"i{n}", True) for n in range(8)] + [
        _t("m1", False, "x", modelo=True), _t("m2", False, "x", modelo=True),
    ]
    assert painel.situacao(lista).estado == painel.PRECISA_APOIO


def test_em_progresso_no_meio():
    lista = [_t(f"i{n}", n < 6) for n in range(10)]
    assert painel.situacao(lista).estado == painel.EM_PROGRESSO


def test_so_os_ultimos_10_itens_contam():
    antigos = [_t(f"v{n}", False, "x") for n in range(10)]
    recentes = [_t(f"i{n}", True) for n in range(10)]
    assert painel.situacao(antigos + recentes).estado == painel.DOMINA


def test_turma_demo_tem_os_tres_estados_e_recomendacoes():
    registro = Registro(":memory:")
    turma_demo.criar(registro)
    assert len(registro.listar_alunos()) == 6
    assert registro.ler_config("nome_turma", "") == "Turma de demonstração"
    alunos, habilidades, celulas = painel.grade(registro.listar_tentativas())
    assert alunos == ["Ana", "Beto", "Caio", "Duda", "Edu", "Fê"]
    estados = {s.estado for s in celulas.values()}
    assert estados == {painel.DOMINA, painel.EM_PROGRESSO, painel.PRECISA_APOIO}
    frases = painel.recomendacoes(celulas)
    assert any(f.startswith("Somar frações") and "Ana somou os denominadores" in f for f in frases)
    assert len(habilidades) == 4


def test_turma_demo_e_sempre_igual():
    a, b = Registro(":memory:"), Registro(":memory:")
    turma_demo.criar(a)
    turma_demo.criar(b)
    assert a.listar_tentativas() == b.listar_tentativas()


def test_tela_do_painel(qtbot, monkeypatch):
    from app.entrada.camera import CameraNula
    from app.janela import JanelaPrincipal
    from app.nucleo.audio import ServicoAudio

    janela = JanelaPrincipal(CameraNula, Registro(":memory:"), ServicoAudio(backend="nulo"))
    qtbot.addWidget(janela)
    from PySide6.QtWidgets import QLabel, QWidget

    janela.abrir_painel()
    textos = [w.text() for w in janela.painel.conteudo.findChildren(QLabel)]
    assert any("Ainda não há tentativas" in x for x in textos)
    janela.adulto.carregar_turma_demo()
    janela.abrir_painel()
    assert janela.painel.titulo.text() == "Painel do professor: Turma de demonstração"
    nomes = [w.accessibleName() for w in janela.painel.conteudo.findChildren(QWidget)]
    esperado = "Ana, somar frações de mesmo denominador: Precisa de apoio"
    assert any(n.startswith(esperado) for n in nomes)
    janela.adulto.carregar_turma_demo()  # não duplica
    assert len(janela.registro.listar_alunos()) == 6
