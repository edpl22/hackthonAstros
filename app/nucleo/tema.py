"""Paleta, fonte e folha de estilo. Na Etapa 2 passa a aplicar também o perfil do aluno."""

from dataclasses import dataclass

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from app.nucleo import caminhos


@dataclass(frozen=True)
class Paleta:
    fundo: str
    texto: str
    primaria: str
    destaque: str
    apoio: str
    superficie: str  # fundo dos botões e alvos


PALETA_PADRAO = Paleta(
    fundo="#F6F3EC",
    texto="#2A2A2A",
    primaria="#2F6F6A",
    destaque="#D9A441",
    apoio="#8FA9C7",
    superficie="#FFFFFF",
)

PALETA_ALTO_CONTRASTE = Paleta(
    fundo="#FFFFFF",
    texto="#000000",
    primaria="#00524C",
    destaque="#D9A441",
    apoio="#000000",
    superficie="#FFFFFF",
)

# Pares texto/fundo usados nas telas; o teste de contraste confere todos.
PARES_DE_TEXTO = (
    ("texto", "fundo"),
    ("texto", "superficie"),
    ("primaria", "fundo"),
    ("primaria", "superficie"),
    ("texto", "destaque"),
)

CORPO_PX = 24
INSTRUCAO_PX = 32
TITULO_PX = 56
FONTE_RESERVA = "sans-serif"


def _luminancia(cor: str) -> float:
    canais = [int(cor[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lineares = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
    r, g, b = lineares
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(cor_a: str, cor_b: str) -> float:
    """Razão de contraste WCAG 2.x entre duas cores `#RRGGBB`."""
    clara, escura = sorted((_luminancia(cor_a), _luminancia(cor_b)), reverse=True)
    return (clara + 0.05) / (escura + 0.05)


def carregar_fonte() -> str:
    """Registra a Atkinson Hyperlegible e devolve o nome da família (ou a reserva do sistema)."""
    familia = None
    for nome in ("AtkinsonHyperlegible-Regular.ttf", "AtkinsonHyperlegible-Bold.ttf"):
        arquivo = caminhos.asset("fontes", nome)
        if not arquivo.exists():
            continue
        ident = QFontDatabase.addApplicationFont(str(arquivo))
        familias = QFontDatabase.applicationFontFamilies(ident) if ident >= 0 else []
        familia = familia or (familias[0] if familias else None)
    return familia or FONTE_RESERVA


def folha_estilo(p: Paleta, familia: str, escala: float = 1.0) -> str:
    def px(valor: float) -> int:
        return round(valor * escala)

    return f"""
    QWidget {{
        background: {p.fundo};
        color: {p.texto};
        font-family: "{familia}";
        font-size: {px(CORPO_PX)}px;
    }}
    QLabel#titulo {{
        color: {p.primaria};
        font-size: {px(TITULO_PX)}px;
        font-weight: bold;
    }}
    QLabel#instrucao {{
        font-size: {px(INSTRUCAO_PX)}px;
    }}
    QPushButton {{
        background: {p.superficie};
        color: {p.texto};
        border: 2px solid {p.apoio};
        border-radius: 12px;
        padding: {px(14)}px {px(30)}px;
        min-height: {px(64)}px;
        min-width: {px(64)}px;
    }}
    QPushButton:hover {{
        border: 2px solid {p.primaria};
    }}
    QPushButton:focus {{
        border: 4px solid {p.primaria};
        padding: {px(12)}px {px(28)}px;
    }}
    QPushButton:pressed {{
        background: {p.destaque};
    }}
    QPushButton#grande {{
        font-size: {px(INSTRUCAO_PX)}px;
        font-weight: bold;
        min-width: {px(280)}px;
        min-height: {px(160)}px;
    }}
    """


def aplicar(app: QApplication, paleta: Paleta = PALETA_PADRAO, escala: float = 1.0) -> str:
    familia = carregar_fonte()
    app.setFont(QFont(familia, round(CORPO_PX * escala)))
    app.setStyleSheet(folha_estilo(paleta, familia, escala))
    return familia
