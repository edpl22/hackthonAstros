import math

import pytest

from app.entrada import mao


def _mao(polegar=(0.50, 0.50), indicador=(0.60, 0.50)):
    """21 pontos com palma de 0,2 (punho 0,5/0,8 até base do médio 0,5/0,6), proporção 1."""
    pontos = [(0.5, 0.5, 0.0)] * 21
    pontos[mao.PUNHO] = (0.5, 0.8, 0.0)
    pontos[mao.BASE_MEDIO] = (0.5, 0.6, 0.0)
    pontos[mao.POLEGAR] = (*polegar, 0.0)
    pontos[mao.INDICADOR] = (*indicador, 0.0)
    return pontos


# --- filtro One Euro -------------------------------------------------------


def test_um_euro_primeiro_valor_passa_direto():
    assert mao.FiltroUmEuro().filtrar(0.3, 0.0) == 0.3


def test_um_euro_suaviza_tremor():
    filtro = mao.FiltroUmEuro()
    saidas = [filtro.filtrar(0.5 + (0.01 if i % 2 else -0.01), i / 30) for i in range(60)]
    variacao = max(saidas[30:]) - min(saidas[30:])
    assert variacao < 0.02 * 0.5  # tremor de 0,02 cai para menos da metade


def test_um_euro_converge_para_valor_parado():
    filtro = mao.FiltroUmEuro()
    filtro.filtrar(0.0, 0.0)
    saida = 0.0
    for i in range(1, 120):
        saida = filtro.filtrar(1.0, i / 30)
    assert saida == pytest.approx(1.0, abs=1e-3)


def test_um_euro_beta_maior_segue_movimento_rapido_mais_de_perto():
    lento, rapido = mao.FiltroUmEuro(beta=0.0), mao.FiltroUmEuro(beta=5.0)
    for filtro in (lento, rapido):
        filtro.filtrar(0.0, 0.0)
    assert rapido.filtrar(1.0, 1 / 30) > lento.filtrar(1.0, 1 / 30)


def test_um_euro_ignora_tempo_que_nao_avanca():
    filtro = mao.FiltroUmEuro()
    filtro.filtrar(0.2, 1.0)
    assert filtro.filtrar(0.9, 1.0) == 0.9  # recomeça em vez de dividir por zero


def test_um_euro_reiniciar():
    filtro = mao.FiltroUmEuro()
    filtro.filtrar(0.0, 0.0)
    filtro.reiniciar()
    assert filtro.filtrar(0.7, 0.1) == 0.7


# --- área ativa ------------------------------------------------------------


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [((0.1, 0.1), (0.0, 0.0)), ((0.5, 0.5), (0.5, 0.5)), ((0.9, 0.9), (1.0, 1.0))],
)
def test_area_ativa_mapeia_80_por_cento_central(entrada, esperado):
    assert mao.mapear_area_ativa(*entrada) == pytest.approx(esperado)


def test_area_ativa_trava_nas_bordas():
    assert mao.mapear_area_ativa(0.0, 1.0) == (0.0, 1.0)


# --- pinça -----------------------------------------------------------------


def test_razao_pinca_normaliza_pelo_tamanho_da_palma():
    assert mao.razao_pinca(_mao(indicador=(0.60, 0.50)), proporcao=1.0) == pytest.approx(0.5)


def test_razao_pinca_igual_com_mao_perto_ou_longe():
    perto = _mao()
    longe = [(0.5 + (x - 0.5) / 2, 0.5 + (y - 0.5) / 2, z) for x, y, z in perto]
    assert mao.razao_pinca(perto) == pytest.approx(mao.razao_pinca(longe))


def test_razao_pinca_palma_degenerada():
    pontos = [(0.5, 0.5, 0.0)] * 21
    assert mao.razao_pinca(pontos) == math.inf


def test_pinca_histerese():
    pinca = mao.DetectorPinca()
    assert pinca.atualizar(0.30) is False  # entre os limites, continua aberta
    assert pinca.atualizar(0.24) is True  # fecha abaixo de 0,25
    assert pinca.atualizar(0.35) is True  # entre os limites, continua fechada
    assert pinca.atualizar(0.40) is True  # exatamente 0,40 ainda não abre
    assert pinca.atualizar(0.41) is False  # abre acima de 0,40


def test_pinca_limites_invalidos():
    with pytest.raises(ValueError):
        mao.DetectorPinca(fecha=0.5, abre=0.4)


# --- rastreador ------------------------------------------------------------


def test_rastreador_sem_mao():
    estado = mao.RastreadorMao().atualizar(None, False, 0.0)
    assert estado == mao.EstadoMao(presente=False)


def test_rastreador_posicao_e_pinca():
    rastreador = mao.RastreadorMao()
    estado = rastreador.atualizar(_mao(polegar=(0.5, 0.5), indicador=(0.51, 0.5)), True, 0.0)
    assert estado.presente
    assert (estado.x, estado.y) == pytest.approx(mao.mapear_area_ativa(0.51, 0.5))
    assert estado.pinca_fechada


def test_rastreador_reinicia_pinca_quando_a_mao_some():
    rastreador = mao.RastreadorMao()
    rastreador.atualizar(_mao(indicador=(0.51, 0.5)), True, 0.0)
    rastreador.atualizar(None, False, 0.1)
    assert rastreador.pinca.fechada is False
