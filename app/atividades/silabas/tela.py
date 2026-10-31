"""Ímã das Sílabas sobre a AtividadeBase.

Níveis 1 a 3: figura da palavra no alto, uma caixa por sílaba e bolhas com as sílabas certas
mais distratoras. Pegar a bolha toca a sílaba; soltar na caixa certa encaixa; errar devolve a
bolha e dá uma pista. Com a palavra pronta, toca a palavra inteira.
Nível 4: "Qual bolha é a mais forte?" — escolher a sílaba tônica.
"""

from PySide6.QtCore import QRectF

from app.atividades.base import AtividadeBase
from app.atividades.silabas import logica
from app.nucleo.conteudo import texto
from app.telas.cena_itens import ALTURA, LARGURA, CenaItens

LADO_BOLHA = 120
LADO_FIGURA = 190
Y_FIGURA, Y_CAIXAS, Y_BOLHAS = 0.17, 0.50, 0.81  # fração da altura da cena
Y_BOLHAS_TONICA = 0.66


def _frase(chave: str, **dados) -> str:
    return texto(f"silabas.{chave}").format(**dados)


def _ordinal(posicao: int) -> str:
    return texto("silabas.ordinais").split(",")[posicao]


class TelaSilabas(AtividadeBase):
    id_atividade = "silabas"
    nivel_maximo = logica.NIVEL_MAXIMO

    def __init__(self, contexto, parent=None):
        self.rodada: logica.Rodada | None = None
        self._rodadas = 0
        super().__init__(contexto, parent)

    # --- rodada e cena ---------------------------------------------------------------

    def iniciar(self, *args, **kwargs) -> None:
        self._rodadas = 0  # a mesma semente dá as mesmas rodadas a cada abertura
        super().iniciar(*args, **kwargs)

    def preparar_rodada(self, semente: int | None) -> None:
        anterior = self.rodada.palavra.id if self.rodada else None
        semente_rodada = None if semente is None else semente + self._rodadas
        self._rodadas += 1
        self.rodada = logica.nova_rodada(
            self.nivel.nivel,
            self.perfil.max_itens,
            semente_rodada,
            id_palavra=self.opcoes.pop("palavra", None),  # só a primeira rodada
            anterior=anterior,
        )

    @property
    def cena(self) -> CenaItens:
        return self.area

    def _rotulo(self, bolha: logica.Bolha) -> str:
        return logica.rotulo(bolha.silaba, self.rodada.nivel)

    def criar_area(self) -> CenaItens:
        cena = CenaItens(self.barramento, self.perfil)
        rodada = self.rodada
        escala = self.perfil.escala
        lado_figura = min(LADO_FIGURA * escala, ALTURA * 0.32)
        cena.adicionar_figura(rodada.palavra.figura, LARGURA / 2, ALTURA * Y_FIGURA, lado_figura)
        n_bolhas = len(rodada.bolhas)
        limite_altura = ALTURA * (0.21 if escala < 1.3 else 0.26)  # baixa visão: bolhas maiores
        lado = min(LADO_BOLHA * escala, (LARGURA - 80) / n_bolhas - 30, limite_altura)
        y_bolhas = ALTURA * (Y_BOLHAS_TONICA if rodada.tonica else Y_BOLHAS)
        passo = LARGURA / n_bolhas
        for i, bolha in enumerate(rodada.bolhas):
            alternada = (
                self.perfil.silabas_alternadas
                and bolha.posicao is not None
                and bolha.posicao % 2 == 1
            )
            cena.adicionar_peca(
                bolha.id, self._rotulo(bolha), passo * (i + 0.5), y_bolhas, lado,
                tipo="bolha", forma="redondo", alternada=alternada,
            )
        if not rodada.tonica:
            n = len(rodada.palavra.silabas)
            lado_caixa = lado + 24
            largura_total = n * lado_caixa + (n - 1) * 24
            x0 = (LARGURA - largura_total) / 2 + lado_caixa / 2
            for pos in range(n):
                cena.adicionar_caixa(
                    logica.id_caixa(pos), _frase("caixa", ordinal=_ordinal(pos)),
                    x0 + pos * (lado_caixa + 24), ALTURA * Y_CAIXAS, lado_caixa,
                    mostrar_rotulo=False,
                )
            regiao = QRectF(40, ALTURA * (Y_BOLHAS - 0.11), LARGURA - 80, ALTURA * 0.22)
            cena.flutuar(self.perfil.velocidade, regiao)
        cena.pegou.connect(self._ao_pegar)
        cena.soltou.connect(self._ao_soltar)
        cena.escolheu.connect(self._ao_escolher)
        cena.nada_para_pegar.connect(lambda: self._anunciar(_frase("nada_para_pegar"), False))
        return cena

    def parar(self) -> None:
        if self.area is not None:
            self.cena.parar_flutuar()
        super().parar()

    # --- textos ------------------------------------------------------------------------

    def texto_apresentacao(self) -> str:
        chave = "apresentacao_tonica" if self.rodada.tonica else "apresentacao"
        return texto(f"silabas.{chave}")

    def figura_apresentacao(self) -> str | None:
        return self.rodada.palavra.figura

    def instrucao_atual(self) -> str:
        rodada = self.rodada
        if rodada.concluida:
            return texto("silabas.terminou")
        if rodada.tonica:
            return _frase("instrucao_tonica", palavra=rodada.palavra.texto)
        pos = rodada.proxima_posicao()
        bolha = rodada.bolha_da_posicao(pos)
        return _frase("instrucao", silaba=self._rotulo(bolha), ordinal=_ordinal(pos))

    def item_atual(self) -> str | None:
        pos = self.rodada.proxima_posicao()
        if pos is None:
            return None
        return self._item(pos)

    def _item(self, pos: int) -> str:
        sufixo = "tonica" if self.rodada.tonica else str(pos + 1)
        return f"{self.rodada.palavra.id}-{sufixo}"

    def habilidade(self) -> str:
        chave = "habilidade_tonica" if self.rodada.tonica else "habilidade"
        return texto(f"silabas.{chave}")

    # --- jogadas -------------------------------------------------------------------------

    def _bolha(self, id_bolha: str) -> logica.Bolha:
        return next(b for b in self.rodada.bolhas if b.id == id_bolha)

    def _ao_pegar(self, id_bolha: str) -> None:
        bolha = self._bolha(id_bolha)
        self.falar(logica.fala_da_bolha(self.rodada, bolha))  # ao pegar, toca a sílaba
        if self.rodada.tonica:
            self.cena.devolver(id_bolha)
            self.barramento.soltar.emit()  # no nível 4 pegar já é escolher
            self._ao_escolher(id_bolha)
            return
        self._anunciar(_frase("pegou", silaba=self._rotulo(bolha)))

    def _ao_soltar(self, id_bolha: str, caixa_id) -> None:
        if self.rodada.tonica:
            self.cena.devolver(id_bolha)
            return
        bolha = self._bolha(id_bolha)
        rotulo = self._rotulo(bolha)
        if caixa_id is None:  # caiu fora: não é resposta, só volta
            self.cena.devolver(id_bolha)
            self._anunciar(_frase("soltou_fora", silaba=rotulo))
            return
        pos = int(caixa_id.split("-")[1]) - 1
        tipo_erro = logica.conferir(self.rodada, pos, bolha.silaba)
        if tipo_erro is None:
            self.cena.encaixar(id_bolha, caixa_id)
            self.rodada.colocadas[pos] = bolha.silaba
            frase = _frase("encaixou", silaba=rotulo, ordinal=_ordinal(pos))
        else:
            self.cena.devolver(id_bolha)  # erro neutro: a bolha volta, nada vermelho
            frase = _frase("voltou", silaba=rotulo)
        self.cena.realcar([])
        self.registrar_resposta(self._item(pos), bolha.silaba, tipo_erro is None, tipo_erro, frase)
        self._depois_da_jogada()

    def _ao_escolher(self, id_bolha: str) -> None:
        if not self.rodada.tonica or self.rodada.concluida:
            return
        bolha = self._bolha(id_bolha)
        tipo_erro = logica.conferir_tonica(self.rodada, bolha)
        palavra = self.rodada.palavra.texto
        if tipo_erro is None:
            self.rodada.tonica_escolhida = True
            self.cena.realcar([id_bolha])
            frase = _frase("tonica_certa", silaba=bolha.silaba, palavra=palavra)
        else:
            frase = _frase("tonica_errada", silaba=bolha.silaba)
        self.registrar_resposta(self._item(0), bolha.silaba, tipo_erro is None, tipo_erro, frase)
        self._depois_da_jogada()

    def _depois_da_jogada(self) -> None:
        self.atualizar_instrucao()
        if self.rodada.concluida and self.momento == "atividade":
            if not self.rodada.tonica:
                # Palavra pronta: realça as sílabas e toca a palavra inteira.
                self.cena.realcar(self.cena.caixas.keys())
                self.falar(self.rodada.palavra.fala_palavra)
            self.cena.parar_flutuar()
            self.concluir()

    # --- pistas --------------------------------------------------------------------------

    def _posicao_do_item(self, item: str) -> int:
        sufixo = item.rsplit("-", 1)[1]
        return self.rodada.palavra.tonica if sufixo == "tonica" else int(sufixo) - 1

    def realcar(self, item: str) -> None:
        pos = self._posicao_do_item(item)
        bolha = self.rodada.bolha_da_posicao(pos)
        ids = [bolha.id] if self.rodada.tonica else [bolha.id, logica.id_caixa(pos)]
        self.cena.realcar(ids)

    def mostrar_modelo(self, item: str) -> None:
        pos = self._posicao_do_item(item)
        bolha = self.rodada.bolha_da_posicao(pos)
        if self.rodada.tonica:
            self.rodada.tonica_escolhida = True
            self.cena.realcar([bolha.id])
        else:
            self.cena.encaixar(bolha.id, logica.id_caixa(pos))
            self.rodada.colocadas[pos] = bolha.silaba

    def estado_area(self) -> dict:
        return {
            "palavra": self.rodada.palavra.texto,
            "figura": self.rodada.palavra.figura,
            **self.cena.estado(),
        }
