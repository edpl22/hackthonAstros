"""Treino de arrastar sobre a AtividadeBase.

Nível 1: peças em letra bastão (A) para a caixa da mesma letra.
Nível 2: peças em minúscula (a) para a caixa da maiúscula (A).
"""

from app.atividades.base import AtividadeBase
from app.atividades.treino import logica
from app.nucleo import anuncio, erros
from app.nucleo.conteudo import texto
from app.telas.cena_itens import ALTURA, LARGURA, CenaItens

LADO_PECA = 140
Y_PECAS, Y_CAIXAS = 0.28, 0.70  # centro das filas, em fração da altura da cena


class TelaTreino(AtividadeBase):
    id_atividade = "treino"
    nivel_maximo = 2

    def iniciar(self, *args, **kwargs) -> None:
        self._rodadas = 0  # cada abertura começa no A; cada nova rodada avança no alfabeto
        super().iniciar(*args, **kwargs)

    def preparar_rodada(self, semente: int | None) -> None:
        semente_rodada = None if semente is None else semente + self._rodadas
        self.rodada = logica.nova_rodada(self.perfil.max_itens, semente_rodada, self._rodadas)
        self._rodadas += 1

    def criar_area(self) -> CenaItens:
        cena = CenaItens(self.barramento, self.perfil)
        letras = self.rodada.letras
        n = len(letras)
        # Escala do perfil, limitada para tudo caber na cena (largura e altura).
        lado = min(LADO_PECA * self.perfil.escala, (LARGURA - 80) / n - 40, ALTURA * 0.34)
        passo = LARGURA / n
        minuscula = self.nivel.nivel >= 2
        for i, letra in enumerate(letras):
            coluna = self.rodada.ordem_pecas[i]
            rotulo = letra.lower() if minuscula else letra
            cena.adicionar_peca(
                logica.id_peca(letra, i), rotulo, passo * (coluna + 0.5), ALTURA * Y_PECAS, lado
            )
            cena.adicionar_caixa(
                logica.id_caixa(i), letra, passo * (i + 0.5), ALTURA * Y_CAIXAS, lado + 24
            )
        cena.pegou.connect(self._ao_pegar)
        cena.soltou.connect(self._ao_soltar)
        cena.nada_para_pegar.connect(lambda: self._anunciar(anuncio.frase("nada_para_pegar")))
        return cena

    @property
    def cena(self) -> CenaItens:
        return self.area

    def instrucao_atual(self) -> str:
        letra = self.rodada.proxima_letra()
        if letra is None:
            return texto("treino.terminou")
        return texto("treino.instrucao").format(letra=letra)

    def item_atual(self) -> str | None:
        return self.rodada.proxima_letra()

    # --- jogadas --------------------------------------------------------------------

    def _letra(self, peca_id: str) -> str:
        return self.cena.pecas[peca_id].rotulo

    def _indice(self, letra: str) -> int:
        return self.rodada.letras.index(letra.upper())

    def _ao_pegar(self, peca_id: str) -> None:
        self._anunciar(anuncio.frase("pegou", item=self._letra(peca_id)), falar=False)

    def _ao_soltar(self, peca_id: str, caixa_id) -> None:
        letra = self._letra(peca_id)
        if caixa_id is None:  # caiu fora: não é resposta, só volta
            self.cena.devolver(peca_id)
            self._anunciar(anuncio.frase("soltou_fora", item=letra))
            return
        letra_caixa = self.cena.caixas[caixa_id].rotulo
        tipo_erro = erros.classificar_treino(letra, letra_caixa)
        if tipo_erro is None:
            self.cena.encaixar(peca_id, caixa_id)
            self.rodada.colocadas.add(letra_caixa)
            frase = anuncio.frase("encaixou", item=letra, alvo=letra_caixa)
        else:
            self.cena.devolver(peca_id)  # erro neutro: a peça volta, nada vermelho
            frase = anuncio.frase("voltou", item=letra)
        self.cena.realcar([])
        self.registrar_resposta(letra_caixa, letra, tipo_erro is None, tipo_erro, frase)
        self._depois_da_jogada()

    def _depois_da_jogada(self) -> None:
        self.atualizar_instrucao()
        if self.rodada.concluida:
            self.concluir()

    # --- pistas ------------------------------------------------------------------------

    def realcar(self, item: str) -> None:
        i = self._indice(item)
        self.cena.realcar([logica.id_peca(self.rodada.letras[i], i), logica.id_caixa(i)])

    def mostrar_modelo(self, item: str) -> None:
        i = self._indice(item)
        self.cena.encaixar(logica.id_peca(self.rodada.letras[i], i), logica.id_caixa(i))
        self.rodada.colocadas.add(self.rodada.letras[i])

    def estado_area(self) -> dict:
        return self.cena.estado()
