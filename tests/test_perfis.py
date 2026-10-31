from dataclasses import fields

import pytest

from app.nucleo import perfis
from app.nucleo.perfis import PERFIS, Perfil, combinar


def test_oito_perfis_prontos():
    assert list(PERFIS) == [
        "padrao", "tea", "tdah", "dislexia", "baixa_visao", "daltonismo", "motor", "cegueira",
    ]


def test_valores_da_especificacao():
    assert (PERFIS["padrao"].velocidade, PERFIS["padrao"].max_itens) == (0.5, 4)
    assert PERFIS["tea"].velocidade == 0 and PERFIS["tea"].max_itens == 3
    assert PERFIS["tea"].miniatura_camera is False and PERFIS["tea"].aviso_troca_atividade
    assert PERFIS["tdah"].um_passo_por_vez and PERFIS["tdah"].rodada_itens == 5
    assert PERFIS["dislexia"].espacamento_letras == 0.12 and PERFIS["dislexia"].escala == 1.2
    assert PERFIS["baixa_visao"].escala == 1.75 and PERFIS["baixa_visao"].contorno_px == 5
    assert PERFIS["daltonismo"].paleta_segura
    motor = PERFIS["motor"]
    assert (motor.modo_entrada_preferido, motor.tolerancia_alvo_px, motor.tempo_permanencia_ms) == (
        "permanencia", 60, 1200,
    )
    assert PERFIS["cegueira"].modo_entrada_preferido == "teclado"


def test_lista_vazia_e_padrao():
    assert combinar([]) == Perfil()


def test_um_perfil_sozinho_nao_muda():
    for nome, perfil in PERFIS.items():
        assert combinar([nome]) == perfil


def test_tea_com_dislexia():
    p = combinar(["tea", "dislexia"])
    assert p.velocidade == 0  # menor vence
    assert p.max_itens == 3  # menor vence
    assert p.escala == 1.2  # maior vence
    assert p.silabas_alternadas  # True vence
    assert p.miniatura_camera is False  # False vence
    assert p.espacamento_letras == 0.12


def test_entrada_mais_acessivel_vence():
    assert combinar(["motor"]).modo_entrada_preferido == "permanencia"
    assert combinar(["motor", "cegueira"]).modo_entrada_preferido == "teclado"


def test_combinacao_e_comutativa():
    assert combinar(["baixa_visao", "tdah", "motor"]) == combinar(["motor", "tdah", "baixa_visao"])


def test_combinar_todos_mantem_escala_no_limite():
    p = combinar(list(PERFIS))
    assert 1.0 <= p.escala <= 2.0
    assert p.max_itens == 3 and p.rodada_itens == 5


def test_todo_campo_tem_regra():
    com_regra = set(perfis.MENOR_VENCE) | set(perfis.MAIOR_VENCE) | set(perfis.FALSO_VENCE)
    com_regra |= set(perfis.REGRAS["True vence"]) | {"modo_entrada_preferido"}
    assert {f.name for f in fields(Perfil)} == com_regra


def test_ler_lista():
    assert perfis.ler_lista(" tea, dislexia ") == ["tea", "dislexia"]
    assert perfis.ler_lista("") == []
    with pytest.raises(ValueError, match="desconhecido"):
        perfis.ler_lista("tea,xyz")
