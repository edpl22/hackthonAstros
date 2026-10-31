"""Mesa de Quantidades sobre a AtividadeBase.

Nível 1 (Montar): objetos no cesto, uma bandeja e o cartão "Pronto"; o número da bandeja
muda e aparece na legenda a cada objeto ("três maçãs").
Nível 2 (Comparar): as bandejas vêm cheias, os objetos são ligados um a um por linhas e a
sobra fica com hachura, contorno grosso e o texto "sobrou".
Níveis 3 e 4 (Resolver): as bandejas mostram a conta; a criança escolhe entre 3 cartões.
Pista 2: os objetos acendem um a um.
"""

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QFont, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsSimpleTextItem

from app.atividades.base import AtividadeBase
from app.atividades.quantidades import logica
from app.nucleo.conteudo import texto
from app.nucleo.tema import paleta_atual
from app.telas.cena_itens import LARGURA, CenaItens

BANDEJA_A, BANDEJA_B = "bandeja-a", "bandeja-b"
LADO_BANDEJA = 280
Y_BANDEJAS = 250
Y_CARTOES = 490
PASSO_PISTA_MS = 400
CONJUNTO_PADRAO = "maca"


def _frase(chave: str, **dados) -> str:
    return texto(f"quantidades.{chave}").format(**dados)


class TelaQuantidades(AtividadeBase):
    id_atividade = "quantidades"
    nivel_maximo = logica.NIVEL_MAXIMO

    def __init__(self, contexto, parent=None):
        self.rodada: logica.Rodada | None = None
        self._rodadas = 0
        self._timer_pista = None
        super().__init__(contexto, parent)

    # --- rodada ----------------------------------------------------------------------

    @property
    def conjunto(self) -> logica.Conjunto:
        padrao = self.ctx.registro.ler_config("conjunto_mesa", CONJUNTO_PADRAO)
        return logica.conjunto(self.opcoes.get("conjunto", padrao))

    def iniciar(self, *args, **kwargs) -> None:
        self._rodadas = 0  # a mesma semente dá as mesmas rodadas a cada abertura
        super().iniciar(*args, **kwargs)

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
        caixa = item.boundingRect()
        item.setPos(x - caixa.width() / 2, y - caixa.height() / 2)
        cena.scene().addItem(item)
        return item

    def _numero(self, bandeja: str, valor: int) -> None:
        item = self.numeros[bandeja]
        item.setText(str(valor))
        x = self.cena.caixas[bandeja].x()
        item.setPos(x - item.boundingRect().width() / 2, 22)

    def _bandeja(self, cena, id_bandeja: str, x: float, capacidade: int) -> None:
        caixa = cena.adicionar_caixa(
            id_bandeja, texto(f"quantidades.{id_bandeja}"), x, Y_BANDEJAS, LADO_BANDEJA,
            mostrar_rotulo=False,
        )
        caixa.capacidade = capacidade
        self.numeros[id_bandeja] = self._texto(cena, "0", x, 60, 64)

    def _objeto(self, cena, indice: int, x: float, y: float, lado: float):
        peca = cena.adicionar_peca(
            f"objeto-{self.conjunto.id}-{indice}", self.conjunto.singular, x, y, lado, tipo="objeto"
        )
        peca.figura = self.conjunto.figura
        return peca

    def _encher(self, cena, id_bandeja: str, quantidade: int, primeiro: int) -> list:
        caixa = cena.caixas[id_bandeja]
        pecas = []
        for k in range(quantidade):
            vaga = caixa.posicao_vaga(k)
            peca = self._objeto(cena, primeiro + k, vaga.x(), vaga.y(), 56)
            cena.encaixar(peca.id, id_bandeja)
            pecas.append(peca)
        self._numero(id_bandeja, quantidade)
        return pecas

    def criar_area(self) -> CenaItens:
        cena = CenaItens(self.barramento, self.perfil)
        self.area = cena
        self.numeros = {}
        self.sobra = None
        r = self.rodada
        if r.montar:
            self._bandeja(cena, BANDEJA_A, LARGURA / 2, capacidade=12)
            n = r.a + 2  # dois a mais que a meta no cesto
            passo = (LARGURA - 120) / n
            for i in range(n):
                self._objeto(cena, i, 60 + passo * (i + 0.5), Y_CARTOES - 10, min(64, passo - 16))
            self._cartoes(cena, [(LARGURA - 140, Y_BANDEJAS)])
        else:
            self._bandeja(cena, BANDEJA_A, 380, capacidade=12)
            self._bandeja(cena, BANDEJA_B, 900, capacidade=12)
            esquerda = self._encher(cena, BANDEJA_A, r.a, 0)
            direita = self._encher(cena, BANDEJA_B, r.b, r.a)
            if r.nivel == logica.COMPARAR:
                self._ligar(cena, esquerda, direita)
            else:
                self._texto(cena, logica.sinal(r.operacao), LARGURA / 2, Y_BANDEJAS, 96)
                if r.operacao == "-":  # subtração: a bandeja da direita é o que sai
                    y = Y_BANDEJAS + LADO_BANDEJA / 2 + 22
                    self._texto(cena, texto("quantidades.tirar"), 900, y, 28)
            n = len(r.cartoes)
            posicoes = [(LARGURA / 2 + (i - (n - 1) / 2) * 200, Y_CARTOES) for i in range(n)]
            self._cartoes(cena, posicoes)
        cena.pegou.connect(self._ao_pegar)
        cena.soltou.connect(self._ao_soltar)
        cena.escolheu.connect(self._ao_escolher)
        return cena

    def _cartoes(self, cena, posicoes) -> None:
        for cartao, (x, y) in zip(self.rodada.cartoes, posicoes, strict=True):
            cena.adicionar_peca(cartao.id, cartao.rotulo, x, y, 130, tipo="cartao")

    def _ligar(self, cena, esquerda, direita) -> None:
        """Comparar: liga um a um; a sobra ganha hachura, contorno grosso e o texto "sobrou"."""
        caneta = QPen(QColor(paleta_atual().primaria), 3)
        for a, b in zip(esquerda, direita, strict=False):
            linha = QGraphicsLineItem(a.x(), a.y(), b.x(), b.y())
            linha.setPen(caneta)
            linha.setZValue(2)
            cena.scene().addItem(linha)
        maior, menor = (esquerda, direita) if len(esquerda) > len(direita) else (direita, esquerda)
        for peca in maior[len(menor):]:
            peca.hachura = True
            peca.update()
        if len(maior) != len(menor):
            x = cena.caixas[BANDEJA_A if maior is esquerda else BANDEJA_B].x()
            self.sobra = self._texto(
                cena, f"{texto('quantidades.sobrou')} {len(maior) - len(menor)}",
                x, Y_BANDEJAS + LADO_BANDEJA / 2 + 22, 28,
            )

    # --- textos -------------------------------------------------------------------------

    def instrucao_atual(self) -> str:
        r = self.rodada
        if r.concluida:
            return texto("quantidades.terminou")
        if r.montar:
            nome = self.conjunto.singular if r.a == 1 else self.conjunto.plural
            return _frase("instrucao_montar", n=r.a, objetos=nome)
        if r.nivel == logica.COMPARAR:
            return texto("quantidades.instrucao_comparar")
        return _frase("instrucao_conta", a=r.a, sinal=logica.sinal(r.operacao), b=r.b)

    def item_atual(self) -> str | None:
        r = self.rodada
        if r.montar:
            return f"montar-{r.a}"
        if r.nivel == logica.COMPARAR:
            return f"comparar-{r.a}x{r.b}"
        return f"conta-{r.a}{r.operacao}{r.b}"

    def habilidade(self) -> str:
        nomes = {logica.MONTAR: "montar", logica.COMPARAR: "comparar"}
        chave = nomes.get(self.rodada.nivel, "contas")
        return texto(f"quantidades.habilidade_{chave}")

    # --- jogadas -----------------------------------------------------------------------

    def _contados(self) -> int:
        return len(self.cena.caixas[BANDEJA_A].ocupantes)

    def _ao_pegar(self, peca_id: str) -> None:
        peca = self.cena.pecas[peca_id]
        if peca.tipo == "cartao":  # cartão: pegar já é escolher (mão, mouse e teclado)
            self.cena.devolver(peca_id)
            self.barramento.soltar.emit()
            self._ao_escolher(peca_id)
            return
        self._anunciar(_frase("pegou", quantidade=logica.quantidade(1, self.conjunto)))

    def _ao_soltar(self, peca_id: str, caixa_id) -> None:
        peca = self.cena.pecas[peca_id]
        if peca.tipo == "cartao" or caixa_id is None or not self.rodada.montar:
            self.cena.devolver(peca_id)
            return
        self.cena.encaixar(peca_id, caixa_id)
        contados = self._contados()
        self._numero(BANDEJA_A, contados)
        self._anunciar(logica.quantidade(contados, self.conjunto))  # "três maçãs", na legenda

    def _ao_escolher(self, peca_id: str) -> None:
        r = self.rodada
        if r.concluida or peca_id not in self.cena.pecas:
            return
        cartao = next(c for c in r.cartoes if c.id == peca_id)
        tempo_ms = int((self.relogio() - self._inicio_item) * 1000)
        contados = self._contados()
        tipo_erro = logica.conferir(r, cartao.valor, tempo_ms, contados)
        if r.montar:
            resposta = str(contados)
            na_bandeja = logica.quantidade(contados, self.conjunto)
            if tipo_erro is None:
                frase = _frase("certo_montar", quantidade=na_bandeja)
            else:
                frase = _frase("errado_montar", quantidade=na_bandeja)
                self.cena.esvaziar(BANDEJA_A)
                self._numero(BANDEJA_A, 0)
        else:
            resposta = cartao.valor
            if tipo_erro is None:
                frase = _frase("certo", resposta=cartao.rotulo)
            else:
                frase = _frase("errado", resposta=cartao.rotulo.capitalize())
        if tipo_erro is None:
            r.concluida = True
            self.cena.realcar([peca_id])
        self.registrar_resposta(self.item_atual(), resposta, tipo_erro is None, tipo_erro, frase)
        self.atualizar_instrucao()
        if r.concluida and self.momento == "atividade":
            self.concluir()

    # --- pistas -------------------------------------------------------------------------

    def realcar(self, item: str) -> None:
        """Pista 2: os objetos acendem um a um."""
        objetos = [
            p.id for p in self.cena.pecas.values()
            if p.tipo == "objeto" and (p.encaixada or self.rodada.montar)
        ]
        if self._timer_pista is not None:
            self._timer_pista.stop()
        if self.perfil.reduzir_movimento or _sem_animacao():
            self.cena.realcar(objetos)
            return
        acesos = []

        def acender():
            if len(acesos) == len(objetos):
                self._timer_pista.stop()
                return
            acesos.append(objetos[len(acesos)])
            self.cena.realcar(acesos)

        self._timer_pista = QTimer(self)
        self._timer_pista.setInterval(PASSO_PISTA_MS)
        self._timer_pista.timeout.connect(acender)
        self._timer_pista.start()

    def mostrar_modelo(self, item: str) -> None:
        r = self.rodada
        if r.montar:
            self.cena.esvaziar(BANDEJA_A)
            livres = [p for p in self.cena.pecas.values() if p.tipo == "objeto"]
            for peca in livres[: r.a]:
                self.cena.encaixar(peca.id, BANDEJA_A)
            self._numero(BANDEJA_A, r.a)
            certo = "cartao-pronto"
        else:
            certo = next(c.id for c in r.cartoes if c.valor == r.certo)
        r.concluida = True
        self.cena.realcar([certo])

    def estado_area(self) -> dict:
        r = self.rodada
        dados = {
            "modo": {1: "montar", 2: "comparar"}.get(r.nivel, "resolver"),
            "conjunto": self.conjunto.id,
            "bandejas": {b: len(c.ocupantes) for b, c in self.cena.caixas.items()},
            **self.cena.estado(),
        }
        if r.operacao:
            dados["conta"] = f"{r.a} {logica.sinal(r.operacao)} {r.b}"
        return dados


def _sem_animacao() -> bool:
    import os

    return os.environ.get("ATLAS_SEM_ANIMACAO") == "1"
