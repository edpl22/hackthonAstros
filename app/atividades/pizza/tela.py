"""Pizza de Frações sobre a AtividadeBase.

Nível 1: uma pizza cortada em d fatias; tocar numa fatia escolhe ou devolve; a fração aparece
embaixo, grande; "Pronto" confere. Níveis 2 e 3: duas pizzas com o mesmo corte e 3 cartões.
Fatia escolhida: hachura diagonal + contorno grosso (não só cor). Opção: barra de chocolate.
Pista 2: as pizzas aparecem sobrepostas, com "as fatias continuam do mesmo tamanho".
"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsSimpleTextItem

from app.atividades.base import AtividadeBase
from app.atividades.pizza import logica
from app.nucleo.conteudo import texto
from app.nucleo.tema import paleta_atual
from app.telas.cena_itens import LARGURA, CenaItens, Peca

Y_CARTOES = 490


def _frase(chave: str, **dados) -> str:
    return texto(f"pizza.{chave}").format(**dados)


class Fatia(Peca):
    """Uma fatia de pizza (setor) ou um pedaço da barra de chocolate.

    A posição do item é o centro da fatia (para o mouse, o teclado e a mão acharem);
    o desenho é feito em relação ao centro da pizza.
    """

    def configurar(self, centro: QPointF, raio: float, indice: int, corte: int, forma: str):
        self.centro, self.raio, self.indice, self.corte, self.forma_fatia = (
            centro, raio, indice, corte, forma,
        )
        self.escolhida = False
        if forma == "barra":
            largura = 2 * raio / corte
            meio = QPointF(centro.x() - raio + largura * (indice + 0.5), centro.y())
            self.lado = min(largura * 0.9, raio * 0.7)
        else:
            angulo = math.radians(90 - (indice + 0.5) * 360 / corte)
            meio = centro + QPointF(math.cos(angulo), -math.sin(angulo)) * raio * 0.6
            corda = 2 * raio * 0.6 * math.sin(math.pi / corte)
            self.lado = min(raio * 0.7, corda * 0.9)
        self.setPos(meio)
        self.origem = meio

    def _caminho(self) -> QPainterPath:
        c = self.centro - self.pos()
        r = self.raio
        caminho = QPainterPath()
        if self.forma_fatia == "barra":
            largura = 2 * r / self.corte
            caminho.addRect(QRectF(c.x() - r + largura * self.indice, c.y() - r * 0.45,
                                   largura, r * 0.9))
        else:
            caminho.moveTo(c)
            inicio = 90 - self.indice * 360 / self.corte
            caminho.arcTo(QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r), inicio, -360 / self.corte)
            caminho.closeSubpath()
        return caminho

    def boundingRect(self) -> QRectF:
        c = self.centro - self.pos()
        m = self.raio + 16
        return QRectF(c.x() - m, c.y() - m, 2 * m, 2 * m)

    def shape(self) -> QPainterPath:
        return self._caminho()

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        caminho = self._caminho()
        pintor.setPen(QPen(QColor(p.texto), self.contorno + (4 if self.escolhida else 0)))
        pintor.setBrush(QBrush(QColor(p.destaque)))
        pintor.drawPath(caminho)
        if self.escolhida:  # hachura diagonal: a escolha não depende só da cor
            pintor.setBrush(QBrush(QColor(p.texto), Qt.BDiagPattern))
            pintor.drawPath(caminho)
        if self.realcado or self.focado:
            pintor.setPen(QPen(QColor(p.primaria), 6 if self.realcado else 4))
            pintor.setBrush(Qt.NoBrush)
            pintor.drawPath(caminho)


class TelaPizza(AtividadeBase):
    id_atividade = "pizza"
    nivel_maximo = logica.NIVEL_MAXIMO

    def __init__(self, contexto, parent=None):
        self.rodada: logica.Rodada | None = None
        self._rodadas = 0
        super().__init__(contexto, parent)

    def iniciar(self, *args, **kwargs) -> None:
        self._rodadas = 0  # a mesma semente dá as mesmas rodadas a cada abertura
        super().iniciar(*args, **kwargs)

    @property
    def forma(self) -> str:
        return self.opcoes.get("forma", self.ctx.registro.ler_config("forma_pizza", "pizza"))

    def preparar_rodada(self, semente: int | None) -> None:
        semente_rodada = None if semente is None else semente + self._rodadas
        self._rodadas += 1
        self.rodada = logica.nova_rodada(self.nivel.nivel, semente_rodada, self.perfil.max_itens)

    @property
    def cena(self) -> CenaItens:
        return self.area

    # --- cena ----------------------------------------------------------------------------

    def _texto(self, cena, conteudo: str, x: float, y: float, tamanho: int):
        item = QGraphicsSimpleTextItem(conteudo)
        fonte = QFont(self.font())
        fonte.setPixelSize(tamanho)
        fonte.setBold(True)
        item.setFont(fonte)
        item.setBrush(QColor(paleta_atual().texto))
        self._centralizar(item, x, y)
        item.setZValue(20)
        cena.scene().addItem(item)
        return item

    @staticmethod
    def _centralizar(item, x: float, y: float) -> None:
        caixa = item.boundingRect()
        item.setPos(x - caixa.width() / 2, y - caixa.height() / 2)

    def _pizza(self, cena, nome: str, centro: QPointF, raio: float, escolhidas: int) -> list:
        fatias = []
        for i in range(self.rodada.corte):
            fatia = Fatia(f"fatia-{nome}-{i}", "", "fatia", 10, self.perfil.contorno_px)
            fatia.configurar(centro, raio, i, self.rodada.corte, self.forma)
            fatia.escolhida = i < escolhidas
            fatia.encaixada = not self.rodada.montar  # nas somas as fatias não se mexem
            cena.scene().addItem(fatia)
            cena.pecas[fatia.id] = fatia
            fatias.append(fatia)
        return fatias

    def criar_area(self) -> CenaItens:
        cena = CenaItens(self.barramento, self.perfil)
        self.area = cena
        self.dica = None
        r = self.rodada
        if r.montar:
            self.fatias = {"a": self._pizza(cena, "a", QPointF(520, 230), 175, 0)}
            self.fracao = self._texto(cena, f"0/{r.corte}", 520, 470, 72)
            cartoes = [(1000, 230)]
        else:
            (n1, d), (n2, _) = r.parcelas
            self.fatias = {
                "a": self._pizza(cena, "a", QPointF(330, 215), 140, n1),
                "b": self._pizza(cena, "b", QPointF(830, 215), 140, n2),
            }
            self._texto(cena, "+", 580, 215, 96)
            self._texto(cena, f"{n1}/{d}", 330, 395, 48)
            self._texto(cena, f"{n2}/{d}", 830, 395, 48)
            self.fracao = self._texto(cena, "= ?", 1110, 215, 72)
            n = len(r.cartoes)
            cartoes = [(LARGURA / 2 + (i - (n - 1) / 2) * 200, Y_CARTOES) for i in range(n)]
        for cartao, (x, y) in zip(r.cartoes, cartoes, strict=True):
            cena.adicionar_peca(cartao.id, cartao.rotulo, x, y, 130, tipo="cartao")
        cena.pegou.connect(self._ao_pegar)
        cena.escolheu.connect(self._ao_escolher)
        return cena

    # --- textos ---------------------------------------------------------------------------

    def instrucao_atual(self) -> str:
        r = self.rodada
        if r.concluida:
            return texto("pizza.terminou")
        if r.montar:
            fatias = "fatia" if r.certo[0] == 1 else "fatias"
            return _frase("instrucao_montar", n=r.certo[0], fatias=fatias, corte=r.corte)
        (n1, d), (n2, _) = r.parcelas
        return _frase("instrucao_somar", a=f"{n1}/{d}", b=f"{n2}/{d}")

    def item_atual(self) -> str | None:
        r = self.rodada
        if r.montar:
            return f"montar-{logica.texto(r.certo)}"
        return f"soma-{logica.texto(r.parcelas[0])}+{logica.texto(r.parcelas[1])}"

    def habilidade(self) -> str:
        chave = "habilidade_montar" if self.rodada.montar else "habilidade_somar"
        return texto(f"pizza.{chave}")

    # --- jogadas ---------------------------------------------------------------------------

    def _escolhidas(self) -> int:
        return sum(f.escolhida for f in self.fatias["a"])

    def _ao_pegar(self, peca_id: str) -> None:
        peca = self.cena.pecas[peca_id]
        self.cena.devolver(peca_id)
        self.barramento.soltar.emit()  # tocar já decide: escolher fatia ou cartão
        if peca.tipo == "fatia":
            peca.escolhida = not peca.escolhida
            peca.update()
            self.fracao.setText(f"{self._escolhidas()}/{self.rodada.corte}")
            self._centralizar(self.fracao, 520, 470)
            self._anunciar(_frase("fracao", fracao=self.fracao.text()))
        else:
            self._ao_escolher(peca_id)

    def _ao_escolher(self, peca_id: str) -> None:
        r = self.rodada
        if r.concluida or not peca_id.startswith("cartao-"):
            if peca_id.startswith("fatia-") and r.montar:
                self._ao_pegar(peca_id)
            return
        cartao = next(c for c in r.cartoes if c.id == peca_id)
        if r.montar:
            escolhidas = self._escolhidas()
            tipo_erro = logica.conferir_montar(r, escolhidas)
            resposta = f"{escolhidas}/{r.corte}"
        else:
            tipo_erro = logica.conferir_soma(r, cartao.valor)
            resposta = cartao.rotulo
        if tipo_erro is None:
            r.concluida = True
            self.cena.realcar([peca_id])
            final = logica.misto(r.certo)
            igual = f" = {final}" if final != logica.texto(r.certo) else ""
            frase = _frase("certo", resposta=f"{logica.texto(r.certo)}{igual}")
            if not r.montar:
                self.fracao.setText(f"= {logica.texto(r.certo)}")
        else:
            frase = _frase("errado", resposta=resposta)
        self.registrar_resposta(self.item_atual(), resposta, tipo_erro is None, tipo_erro, frase)
        self.atualizar_instrucao()
        if r.concluida and self.momento == "atividade":
            self.concluir()

    # --- pistas -----------------------------------------------------------------------------

    def realcar(self, item: str) -> None:
        """Pista 2: as pizzas sobrepostas mostram que o tamanho da fatia não muda."""
        if self.rodada.montar:
            alvo = self.fatias["a"][: self.rodada.certo[0]]
            self.cena.realcar([f.id for f in alvo])
            return
        for fatia in self.fatias["b"]:
            fatia.setOpacity(0.55)  # transparência que ensina: a fatia de B cobre a de A
            fatia.centro = self.fatias["a"][0].centro
            fatia.configurar(fatia.centro, fatia.raio, fatia.indice, fatia.corte, fatia.forma_fatia)
            fatia.escolhida = fatia.indice < self.rodada.parcelas[1][0]
            fatia.update()
        self.dica = self._texto(self.cena, texto("pizza.pista_tamanho"), 580, 40, 30)

    def mostrar_modelo(self, item: str) -> None:
        r = self.rodada
        if r.montar:
            for i, fatia in enumerate(self.fatias["a"]):
                fatia.escolhida = i < r.certo[0]
                fatia.update()
            self.fracao.setText(logica.texto(r.certo))
            certo = "cartao-pronto"
        else:
            certo = next(c.id for c in r.cartoes if c.valor == r.certo)
        r.concluida = True
        self.cena.realcar([certo])

    def estado_area(self) -> dict:
        r = self.rodada
        dados = {
            "modo": {1: "montar", 2: "somar"}.get(r.nivel, "desafio"),
            "forma": self.forma,
            "corte": r.corte,
            "fatias_escolhidas": self._escolhidas() if r.montar else None,
            "parcelas": [logica.texto(f) for f in r.parcelas],
            **self.cena.estado(),
        }
        return dados
