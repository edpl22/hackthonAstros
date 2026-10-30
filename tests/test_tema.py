import pytest

from app.nucleo import tema


def test_contraste_extremos():
    assert tema.contraste("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert tema.contraste("#777777", "#777777") == pytest.approx(1.0)


@pytest.mark.parametrize("paleta", [tema.PALETA_PADRAO, tema.PALETA_ALTO_CONTRASTE])
@pytest.mark.parametrize(("papel_texto", "papel_fundo"), tema.PARES_DE_TEXTO)
def test_pares_de_texto_passam_wcag_aa(paleta, papel_texto, papel_fundo):
    frente, fundo = getattr(paleta, papel_texto), getattr(paleta, papel_fundo)
    assert tema.contraste(frente, fundo) >= 4.5, f"{papel_texto} {frente} sobre {fundo}"


def test_folha_estilo_sem_efeitos_proibidos():
    qss = tema.folha_estilo(tema.PALETA_PADRAO, "Atkinson Hyperlegible").lower()
    for proibido in ("gradient", "shadow", "red", "#ff0000"):
        assert proibido not in qss
