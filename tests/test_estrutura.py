import importlib

import pytest

PACOTES = [
    "app",
    "app.nucleo",
    "app.entrada",
    "app.telas",
    "app.atividades",
    "app.atividades.silabas",
    "app.atividades.quantidades",
    "app.atividades.pizza",
    "app.headless",
]


@pytest.mark.parametrize("nome", PACOTES)
def test_pacote_importa(nome):
    importlib.import_module(nome)
