"""Lógica pura da camada de entrada: alvos, foco, gesto do ponteiro e permanência."""

import pytest

from app.entrada.alvos import Area, CicloFoco, distancia_ate, mais_proximo
from app.entrada.mao import DetectorPermanencia, RastreadorMao, mapear_area_ativa, razao_pinca
from app.entrada.mao_simulada import pontos_sinteticos, quadros
from app.entrada.ponteiro import GestoPonteiro

# --- alvos -----------------------------------------------------------------

A = Area("a", 0, 0, 100, 100)
B = Area("b", 300, 0, 100, 100)


def test_distancia_dentro_e_fora():
    assert distancia_ate(A, 50, 50) == 0
    assert distancia_ate(A, 130, 50) == 30
    assert distancia_ate(A, 103, 104) == pytest.approx(5)


def test_mais_proximo_respeita_tolerancia():
    assert mais_proximo([A, B], 50, 50, 0) == "a"
    assert mais_proximo([A, B], 120, 50, 24) == "a"  # área expandida pela tolerância
    assert mais_proximo([A, B], 150, 50, 24) is None
    assert mais_proximo([A, B], 150, 50, 60) == "a"  # perfil motor: tolerância maior
    assert mais_proximo([A, B], 280, 50, 24) == "b"


def test_ciclo_foco():
    foco = CicloFoco()
    assert foco.avancar() is None
    foco.definir(["a", "b", "c"])
    assert [foco.avancar(), foco.avancar(), foco.avancar(), foco.avancar()] == ["a", "b", "c", "a"]
    assert foco.voltar() == "c"
    foco.definir(["c", "d"])  # mantém o foco no mesmo id
    assert foco.atual == "c"
    foco.definir(["x"])
    assert foco.atual is None
    assert CicloFoco().voltar() is None


def test_ciclo_foco_voltar_sem_foco_vai_para_o_ultimo():
    foco = CicloFoco()
    foco.definir(["a", "b"])
    assert foco.voltar() == "b"


# --- gesto do ponteiro -----------------------------------------------------


class Mao:
    segurando = False


def _gesto():
    estado = Mao()
    return estado, GestoPonteiro(lambda: estado.segurando)


def test_arrastar_e_soltar():
    estado, gesto = _gesto()
    assert gesto.pressionar(10, 10) == [("apontar", 10, 10), ("pegar",)]
    estado.segurando = True
    assert gesto.mover(200, 10) == [("apontar", 200, 10)]
    assert gesto.liberar(200, 10) == [("apontar", 200, 10), ("soltar",)]


def test_clique_clique():
    estado, gesto = _gesto()
    gesto.pressionar(10, 10)
    estado.segurando = True
    assert gesto.liberar(12, 11) == []  # clique curto: a peça continua na mão
    assert gesto.mover(100, 100) == [("apontar", 100, 100)]  # a peça segue o mouse
    assert gesto.pressionar(200, 200) == [("apontar", 200, 200), ("soltar",)]


def test_mover_sem_botao_e_sem_peca_nao_emite():
    _, gesto = _gesto()
    assert gesto.mover(5, 5) == []


# --- permanência -----------------------------------------------------------


def test_permanencia_dispara_depois_do_tempo():
    d = DetectorPermanencia(tolerancia_px=60, tempo_ms=1200)
    assert d.atualizar(100, 100, 0.0, True) is False
    assert d.atualizar(110, 105, 0.6, True) is False
    assert d.progresso == pytest.approx(0.5)
    assert d.atualizar(120, 100, 1.2, True) is True
    assert d.atualizar(120, 100, 2.0, True) is False  # não repete sem sair e voltar


def test_permanencia_recomeca_ao_sair_da_tolerancia():
    d = DetectorPermanencia(tolerancia_px=24, tempo_ms=800)
    d.atualizar(100, 100, 0.0, True)
    d.atualizar(200, 100, 0.5, True)  # saiu: nova âncora
    assert d.atualizar(200, 100, 1.0, True) is False
    assert d.atualizar(200, 100, 1.3, True) is True


def test_permanencia_so_sobre_alvo():
    d = DetectorPermanencia(tolerancia_px=24, tempo_ms=100)
    for t in range(10):
        assert d.atualizar(0, 0, t, False) is False
    assert d.progresso == 0


def test_permanencia_rearma_depois_de_sair_do_alvo():
    d = DetectorPermanencia(tolerancia_px=24, tempo_ms=100)
    d.atualizar(0, 0, 0.0, True)
    assert d.atualizar(0, 0, 0.2, True) is True
    d.atualizar(0, 0, 0.3, False)
    d.atualizar(0, 0, 0.4, True)
    assert d.atualizar(0, 0, 0.6, True) is True


# --- mão simulada ----------------------------------------------------------


def test_pontos_sinteticos_abrem_e_fecham_a_pinca():
    assert razao_pinca(pontos_sinteticos(0.5, 0.5, False)) > 0.40
    assert razao_pinca(pontos_sinteticos(0.5, 0.5, True)) < 0.25


def test_pontos_sinteticos_desfazem_a_area_ativa():
    pontos = pontos_sinteticos(0.2, 0.7, False)
    assert mapear_area_ativa(*pontos[8][:2]) == pytest.approx((0.2, 0.7))


def test_quadros_levam_o_cursor_ate_o_alvo():
    passos = [{"ir_para": "x", "ms": 500}, {"esperar": 500}, {"pinca": True, "ms": 200}]
    lista = list(quadros(passos, lambda _id: (0.8, 0.3)))
    assert len(lista) == 15 + 15 + 6
    tempos = [t for t, _ in lista]
    assert tempos == sorted(tempos)
    rastreador = RastreadorMao()
    for t, pontos in lista:
        estado = rastreador.atualizar(pontos, True, t)
    assert (estado.x, estado.y) == pytest.approx((0.8, 0.3), abs=0.02)
    assert estado.pinca_fechada
