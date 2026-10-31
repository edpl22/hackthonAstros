import random

import pytest

from app.atividades.silabas import logica
from app.atividades.silabas.logica import Bolha


def test_quinze_palavras_por_nivel():
    assert [p.id for p in logica.palavras_do_nivel(1)] == [
        "bola", "casa", "pato", "gato", "sapo", "vaca",
    ]
    assert [p.id for p in logica.palavras_do_nivel(2)] == [
        "macaco", "sapato", "boneca", "janela", "tomate",
    ]
    assert [p.id for p in logica.palavras_do_nivel(3)] == ["braco", "prato", "passaro", "livro"]
    assert len(logica.palavras_do_nivel(4)) == 15


def test_bo_de_bola_e_aberto():
    bola = logica.palavra("bola")
    assert bola.fala_silabas[0] == "bó"
    assert bola.silabas == ("BO", "LA") and bola.tonica == 0


@pytest.mark.parametrize(
    ("silaba", "par"),
    [("BO", "PO"), ("PRA", "BRA"), ("VRO", "FRO"), ("TO", "DO"), ("CA", "GA"), ("LI", None)],
)
def test_trocar_par(silaba, par):
    assert logica.trocar_par(silaba) == par


def test_slug_sem_acento():
    assert logica.slug("PÁS") == "pas" and logica.slug("ÇO") == "co"


def test_nivel_1_distratoras_de_outras_palavras():
    rodada = logica.nova_rodada(1, 4, semente=1, id_palavra="bola")
    distratoras = [b.silaba for b in rodada.bolhas if b.posicao is None]
    assert len(rodada.bolhas) == 4 and len(distratoras) == 2
    outras = {s for p in logica.carregar_palavras() if p.id != "bola" for s in p.silabas}
    assert set(distratoras) <= outras
    assert not set(distratoras) & {"BO", "LA"}


def test_nivel_3_distratora_e_par_surdo_sonoro():
    rodada = logica.nova_rodada(3, 3, semente=2, id_palavra="prato")
    distratoras = [b.silaba for b in rodada.bolhas if b.posicao is None]
    assert distratoras[0] in {"BRA", "DO"}


def test_max_itens_do_perfil():
    assert len(logica.nova_rodada(1, 3, 1, "bola").bolhas) == 3  # TEA
    assert len(logica.nova_rodada(2, 3, 1, "macaco").bolhas) == 3  # sem distratora
    assert len(logica.nova_rodada(1, 4, 1, "bola").bolhas) == 4


def test_nivel_4_so_as_silabas_da_palavra():
    rodada = logica.nova_rodada(4, 4, 1, "janela")
    assert sorted(b.silaba for b in rodada.bolhas) == ["JA", "LA", "NE"]
    assert rodada.tonica and rodada.proxima_posicao() == 1
    certa = next(b for b in rodada.bolhas if b.silaba == "NE")
    errada = next(b for b in rodada.bolhas if b.silaba == "JA")
    assert logica.conferir_tonica(rodada, certa) is None
    assert logica.conferir_tonica(rodada, errada) == "tonica_errada"


@pytest.mark.parametrize("semente", range(15))
def test_bolhas_nunca_comecam_na_ordem_da_palavra(semente):
    rodada = logica.nova_rodada(1, 2, semente, "bola")
    assert [b.posicao for b in rodada.bolhas] == [1, 0]


def test_ids_estaveis_e_unicos():
    rodada = logica.nova_rodada(1, 4, 5, "bola")
    ids = [b.id for b in rodada.bolhas]
    assert len(set(ids)) == 4
    assert any(i.startswith("bolha-bo-") for i in ids)
    assert logica.nova_rodada(1, 4, 5, "bola").bolhas == rodada.bolhas  # mesma semente


def test_rodada_progride_pelas_caixas():
    rodada = logica.nova_rodada(1, 2, 1, "bola")
    assert rodada.proxima_posicao() == 0
    rodada.colocadas[0] = "BO"
    assert rodada.proxima_posicao() == 1 and not rodada.concluida
    rodada.colocadas[1] = "LA"
    assert rodada.concluida and rodada.proxima_posicao() is None
    assert rodada.bolha_da_posicao(0).silaba == "BO"


def test_conferir_classifica_os_erros():
    rodada = logica.nova_rodada(1, 2, 1, "bola")
    assert logica.conferir(rodada, 0, "BO") is None
    assert logica.conferir(rodada, 0, "LA") == "ordem_trocada"
    assert logica.conferir(rodada, 0, "PO") == "par_surdo_sonoro"
    assert logica.conferir(rodada, 1, "SA") == "silaba_de_outra_palavra"


def test_minusculas_no_nivel_3():
    assert logica.rotulo("PRA", 3) == "pra"
    assert logica.rotulo("BO", 1) == "BO" and logica.rotulo("BO", 4) == "BO"


def test_palavra_aleatoria_evita_a_anterior():
    for semente in range(20):
        assert logica.nova_rodada(1, 4, semente, anterior="bola").palavra.id != "bola"


def test_distratoras_sem_repeticao():
    alvo = logica.palavra("sapato")
    lista = logica.distratoras(alvo, 5, 3, random.Random(0))
    assert len(lista) == len(set(lista)) == 5


def test_bolha_e_imutavel():
    with pytest.raises(AttributeError):
        Bolha("x", "BO", 0).silaba = "PO"
