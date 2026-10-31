"""Jogo Dourado sobre a AtividadeBase.

O número aparece no alto. Embaixo fica o quadro valor de lugar (uma coluna por ordem: milhar,
centena, dezena, unidade) e, sob cada coluna, a pilha das peças daquela ordem: cubo, placa,
barra e cubinho. A criança leva as peças para as colunas e toca em "Pronto".
Peça na coluna de outra ordem volta para a pilha com a explicação. Ao errar o "Pronto", só as
colunas erradas voltam para as pilhas.
"""

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsSimpleTextItem

from app.atividades.base import AtividadeBase
from app.atividades.dourado import logica
from app.nucleo import erros
from app.nucleo.conteudo import texto
from app.nucleo.tema import paleta_atual
from app.telas.cena_itens import CenaItens, Peca

LADO_COLUNA = 230
LADO_PECA = 56
Y_NUMERO = 40
Y_COLUNAS = 215
Y_ROTULOS = Y_COLUNAS + LADO_COLUNA / 2 + 22
Y_PILHAS = 480
X_PRONTO = 1170


def _frase(chave: str, **dados) -> str:
    return texto(f"dourado.{chave}").format(**dados)


def _nome(ordem: str, n: int) -> str:
    """"1 centena", "3 centenas" (o plural de milhar é milhares)."""
    singular, plural = texto(f"dourado.ordens.{ordem}").split(",")
    return f"{n} {singular if n == 1 else plural}"


def id_coluna(ordem: str) -> str:
    return f"coluna-{ordem}"


class PecaDourada(Peca):
    """Cubo (milhar), placa (centena), barra (dezena) ou cubinho (unidade), desenhados."""

    def configurar(self, ordem: str) -> "PecaDourada":
        self.ordem = ordem
        return self

    def paint(self, pintor, _opcao, _widget=None) -> None:
        p = paleta_atual()
        q = self._quadro()
        t = self.lado
        pintor.setPen(QPen(QColor(p.texto), 2 + (3 if self.segurada else 0)))
        pintor.setBrush(QBrush(QColor(p.destaque)))
        if self.ordem == "unidade":
            pintor.drawRect(QRectF(-t * 0.16, -t * 0.16, t * 0.32, t * 0.32))
        elif self.ordem == "dezena":
            barra = QRectF(q.left(), -t * 0.09, t, t * 0.18)
            pintor.drawRect(barra)
            pintor.setPen(QPen(QColor(p.texto), 1))
            for k in range(1, 10):
                x = barra.left() + barra.width() * k / 10
                pintor.drawLine(QPointF(x, barra.top()), QPointF(x, barra.bottom()))
        elif self.ordem == "centena":
            pintor.drawRect(q)
            pintor.setPen(QPen(QColor(p.texto), 1))
            for k in range(1, 10):
                d = t * k / 10
                pintor.drawLine(QPointF(q.left() + d, q.top()), QPointF(q.left() + d, q.bottom()))
                pintor.drawLine(QPointF(q.left(), q.top() + d), QPointF(q.right(), q.top() + d))
        else:  # milhar: cubo com frente, topo e lateral
            f = t * 0.22
            frente = QRectF(q.left(), q.top() + f, t - f, t - f)
            topo = QPolygonF([
                frente.topLeft(), frente.topLeft() + QPointF(f, -f),
                frente.topRight() + QPointF(f, -f), frente.topRight(),
            ])
            lado = QPolygonF([
                frente.topRight(), frente.topRight() + QPointF(f, -f),
                frente.bottomRight() + QPointF(f, -f), frente.bottomRight(),
            ])
            for face in (topo, lado):
                pintor.drawPolygon(face)
            pintor.drawRect(frente)
            pintor.setPen(QPen(QColor(p.texto), 1))
            for k in range(1, 4):  # algumas linhas para lembrar os 10 x 10 x 10
                d = frente.width() * k / 4
                pintor.drawLine(QPointF(frente.left() + d, frente.top()),
                                QPointF(frente.left() + d, frente.bottom()))
                pintor.drawLine(QPointF(frente.left(), frente.top() + d),
                                QPointF(frente.right(), frente.top() + d))
        self._desenhar_foco(pintor)


class TelaDourado(AtividadeBase):
    id_atividade = "dourado"
    nivel_maximo = logica.NIVEL_MAXIMO

    def __init__(self, contexto, parent=None):
        self.rodada: logica.Rodada | None = None
        self._rodadas = 0
        super().__init__(contexto, parent)

    def iniciar(self, *args, **kwargs) -> None:
        self._rodadas = 0  # a mesma semente dá as mesmas rodadas a cada abertura
        super().iniciar(*args, **kwargs)

    def preparar_rodada(self, semente: int | None) -> None:
        anterior = self.rodada.numero if self.rodada else None
        semente_rodada = None if semente is None else semente + self._rodadas
        self._rodadas += 1
        self.rodada = logica.nova_rodada(self.nivel.nivel, semente_rodada, anterior)

    @property
    def cena(self) -> CenaItens:
        return self.area

    # --- cena ---------------------------------------------------------------------------

    def _texto(self, cena, conteudo: str, x: float, y: float, tamanho: int):
        item = QGraphicsSimpleTextItem(conteudo)
        fonte = QFont(self.font())
        fonte.setPixelSize(tamanho)
        fonte.setBold(True)
        item.setFont(fonte)
        item.setBrush(QColor(paleta_atual().texto))
        caixa = item.boundingRect()
        item.setPos(x - caixa.width() / 2, y - caixa.height() / 2)
        cena.scene().addItem(item)
        return item

    def _x_coluna(self, i: int) -> float:
        n = len(self.rodada.ordens)
        largura = X_PRONTO - 110
        return 30 + largura * (i + 0.5) / n

    def criar_area(self) -> CenaItens:
        cena = CenaItens(self.barramento, self.perfil)
        self.area = cena
        r = self.rodada
        self._texto(cena, logica.texto_numero(r.numero), X_PRONTO / 2, Y_NUMERO, 64)
        self.pilhas: dict[str, list[str]] = {}
        for i, ordem in enumerate(r.ordens):
            x = self._x_coluna(i)
            coluna = cena.adicionar_caixa(
                id_coluna(ordem), ordem, x, Y_COLUNAS, LADO_COLUNA, mostrar_rotulo=False
            )
            coluna.capacidade = logica.PECAS_POR_PILHA
            self._texto(cena, texto(f"dourado.ordens.{ordem}").split(",")[0].capitalize(),
                        x, Y_ROTULOS, 26)
            self.pilhas[ordem] = []
            for k in range(logica.PECAS_POR_PILHA):
                peca = PecaDourada(f"{ordem}-{k}", ordem, "dourado", LADO_PECA,
                                   self.perfil.contorno_px).configurar(ordem)
                peca.setPos(x, Y_PILHAS)
                peca.origem = QPointF(x, Y_PILHAS)
                peca.setZValue(5)
                cena.scene().addItem(peca)
                cena.pecas[peca.id] = peca
                self.pilhas[ordem].append(peca.id)
        cena.adicionar_peca("cartao-pronto", texto("dourado.pronto"), X_PRONTO, Y_COLUNAS, 130,
                            tipo="cartao")
        self._arrumar_pilhas()
        cena.pegou.connect(self._ao_pegar)
        cena.soltou.connect(self._ao_soltar)
        cena.escolheu.connect(self._ao_escolher)
        return cena

    def _arrumar_pilhas(self) -> None:
        """Só a peça de cima de cada pilha pode ser pega (o teclado não passa pelas 9)."""
        for ordem, ids in self.pilhas.items():
            na_coluna = set(self.cena.caixas[id_coluna(ordem)].ocupantes)
            livres = [i for i in ids if i not in na_coluna]
            for altura, id_peca in enumerate(livres):
                peca = self.cena.pecas[id_peca]
                peca.encaixada = altura != len(livres) - 1  # embaixo de outras: presa
                destino = peca.origem + QPointF(altura * 2, -altura * 2)
                peca.setPos(destino)
                peca.setZValue(5 + altura * 0.01)
            for id_peca in na_coluna:
                self.cena.pecas[id_peca].encaixada = True

    def _contar(self) -> None:
        r = self.rodada
        for ordem in logica.ORDENS:
            coluna = self.cena.caixas.get(id_coluna(ordem))
            r.na_mesa[ordem] = len(coluna.ocupantes) if coluna else 0

    # --- textos -------------------------------------------------------------------------

    def instrucao_atual(self) -> str:
        if self.rodada.concluida:
            return texto("dourado.terminou")
        return _frase("instrucao", numero=logica.texto_numero(self.rodada.numero))

    def item_atual(self) -> str | None:
        return str(self.rodada.numero)

    # --- jogadas ------------------------------------------------------------------------

    def _ao_pegar(self, id_peca: str) -> None:
        peca = self.cena.pecas[id_peca]
        if peca.tipo == "cartao":  # cartão: pegar já é escolher (mão, mouse e teclado)
            self.cena.devolver(id_peca)
            self.barramento.soltar.emit()
            self._ao_escolher(id_peca)
            return
        self._anunciar(_frase("pegou", peca=texto(f"dourado.pecas.{peca.ordem}")))

    def _ao_soltar(self, id_peca: str, id_alvo) -> None:
        peca = self.cena.pecas[id_peca]
        if peca.tipo == "cartao" or id_alvo is None:
            self._arrumar_pilhas()
            return
        ordem_coluna = self.cena.caixas[id_alvo].rotulo
        if ordem_coluna != peca.ordem:  # peça de outra ordem: volta, com a explicação
            self._arrumar_pilhas()
            self._anunciar(_frase(
                "coluna_errada", peca=texto(f"dourado.pecas.{peca.ordem}").capitalize(),
                ordem=texto(f"dourado.ordens.{peca.ordem}").split(",")[0].capitalize(),
            ))
            return
        self.cena.encaixar(id_peca, id_alvo)
        self._arrumar_pilhas()
        self._contar()
        self._anunciar(_nome(peca.ordem, self.rodada.na_mesa[peca.ordem]))

    def _ao_escolher(self, id_peca: str) -> None:
        r = self.rodada
        if id_peca != "cartao-pronto" or r.concluida:
            return
        self._contar()
        certo = logica.algarismos(r.numero)
        tipo_erro = erros.classificar_dourado(dict(r.na_mesa), certo)
        resposta = logica.texto_numero(r.total)
        if tipo_erro is None:
            r.concluida = True
            self.cena.realcar(["cartao-pronto"])
            frase = _frase("certo", numero=logica.texto_numero(r.numero))
        else:
            erradas = logica.ordens_erradas(r)
            for ordem in erradas:  # só as colunas erradas voltam para as pilhas
                if id_coluna(ordem) in self.cena.caixas:
                    self.cena.esvaziar(id_coluna(ordem))
            self._arrumar_pilhas()
            self._contar()
            nomes = ", ".join(texto(f"dourado.ordens.{o}").split(",")[1] for o in erradas)
            frase = _frase("errado", total=resposta, ordens=nomes)
        self.registrar_resposta(self.item_atual(), resposta, tipo_erro is None, tipo_erro, frase)
        self.atualizar_instrucao()
        if r.concluida and self.momento == "atividade":
            self.concluir()

    # --- pistas -------------------------------------------------------------------------

    def realcar(self, item: str) -> None:
        """Pista 2: acende a pilha e a coluna de cada ordem que ainda não está certa."""
        ids = []
        for ordem in logica.ordens_erradas(self.rodada):
            if ordem in self.pilhas:
                topo = [i for i in self.pilhas[ordem] if not self.cena.pecas[i].encaixada]
                ids += topo + [id_coluna(ordem)]
        self.cena.realcar(ids)

    def mostrar_modelo(self, item: str) -> None:
        r = self.rodada
        certo = logica.algarismos(r.numero)
        for ordem in r.ordens:
            self.cena.esvaziar(id_coluna(ordem))
        for ordem in r.ordens:
            for id_peca in self.pilhas[ordem][: certo[ordem]]:
                self.cena.encaixar(id_peca, id_coluna(ordem))
        self._arrumar_pilhas()
        self._contar()
        r.concluida = True
        self.cena.realcar(["cartao-pronto"])

    def estado_area(self) -> dict:
        r = self.rodada
        return {
            "numero": r.numero,
            "na_mesa": {o: r.na_mesa[o] for o in r.ordens},
            **self.cena.estado(),
        }
