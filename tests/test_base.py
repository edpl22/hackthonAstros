"""AtividadeBase: 3 momentos, Agora/Depois, pistas, nível, Pausa, áudio e registro.

Usa o treino como atividade concreta e joga pelo barramento (o mesmo caminho do agente).
"""

import pytest
from PySide6.QtCore import Qt

from app.atividades.base import APRESENTACAO, ATIVIDADE, FIM, Contexto
from app.atividades.treino import logica
from app.atividades.treino.tela import TelaTreino
from app.entrada import camera as camera_mod
from app.entrada.camera import Camera, CameraNula
from app.nucleo.audio import ServicoAudio
from app.nucleo.conteudo import texto
from app.nucleo.perfis import PERFIS, combinar
from app.nucleo.registro import Registro
from app.nucleo.sessao import Sessao


@pytest.fixture
def tela(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    sessao = Sessao()
    contexto = Contexto(Registro(":memory:"), ServicoAudio(backend="nulo"), sessao, CameraNula)
    t = TelaTreino(contexto)
    qtbot.addWidget(t)
    t.resize(1280, 720)
    t.show()
    return t


def _abrir(tela, perfis=(), semente=2):
    tela.ctx.sessao.definir(None, list(perfis))
    tela.iniciar(tela.ctx.sessao.perfil, semente=semente)
    tela.comecar()


def _jogar(tela, peca, caixa):
    b = tela.barramento
    b.apontar.emit(*tela.cena.centro(peca))
    b.pegar.emit()
    b.apontar.emit(*tela.cena.centro(caixa))
    b.soltar.emit()


def _acertar_todas(tela):
    for i, letra in enumerate(tela.rodada.letras):
        if letra not in tela.rodada.colocadas:
            _jogar(tela, logica.id_peca(letra, i), logica.id_caixa(i))


def _errar_a(tela):
    """Peça B na caixa A."""
    _jogar(tela, logica.id_peca(tela.rodada.letras[1], 1), logica.id_caixa(0))


# --- roteiro em 3 momentos -------------------------------------------------------


def test_tres_momentos_e_faixa_agora_depois(tela):
    # TEA: 3 peças, então a rodada termina sem os 4 acertos que oferecem o desafio.
    tela.ctx.sessao.definir(None, ["tea"])
    tela.iniciar(PERFIS["tea"], semente=2)
    assert tela.momento == APRESENTACAO
    assert tela.faixa.texto_agora.text() == "Explicação"
    assert tela.faixa.texto_depois.text() == "Atividade"
    assert tela.instrucao.text() == texto("treino.apresentacao")
    assert tela.ctx.audio.log == []  # nenhum som antes de uma ação da criança

    tela.comecar()
    assert tela.momento == ATIVIDADE
    assert (tela.faixa.texto_agora.text(), tela.faixa.texto_depois.text()) == ("Atividade", "Fim")

    _acertar_todas(tela)
    assert tela.momento == FIM and tela.estado()["concluida"]
    assert tela.faixa.texto_depois.text() == "Nova rodada"
    assert tela.botao_proximo.isVisible()

    tela.proximo()
    assert tela.momento == ATIVIDADE and not tela.rodada.colocadas


def test_botoes_da_atividade_tem_nome_acessivel(tela):
    _abrir(tela)
    for botao in (tela.botao_voltar, tela.botao_pausa, tela.botao_comecar,
                  tela.botao_proximo, tela.botao_sim, tela.botao_nao):
        assert botao.accessibleName()


# --- pistas graduais --------------------------------------------------------------


def test_tres_pistas_ate_o_modelo(tela):
    _abrir(tela)
    _errar_a(tela)
    assert tela.estado()["pista_nivel"] == 1
    assert tela.ultimo_anuncio.endswith(tela.instrucao_atual())  # 1ª: repete a instrução

    _errar_a(tela)
    assert tela.estado()["pista_nivel"] == 2
    realcados = {i["id"] for i in tela.estado()["itens"] if i["realcado"]}
    assert realcados == {logica.id_peca("A", 0)}  # 2ª: realça a peça certa
    assert tela.cena.caixas["caixa-1"].realcado

    _errar_a(tela)
    assert "A" in tela.rodada.colocadas  # 3ª: o modelo coloca a peça A
    assert tela.cena.pecas[logica.id_peca("A", 0)].encaixada
    tentativas = tela.ctx.registro.listar_tentativas()
    assert [t["pistas"] for t in tentativas] == [1, 2, 3]
    assert tentativas[-1]["precisou_modelo"] is True
    assert {t["tipo_erro"] for t in tentativas} == {"letra_trocada"}


def test_erro_e_neutro(tela):
    _abrir(tela)
    _errar_a(tela)
    assert "Vamos tentar de novo" in tela.ultimo_anuncio
    assert all("errad" not in linha.lower() for linha in tela.ctx.audio.log)


# --- nível ------------------------------------------------------------------------


def test_quatro_acertos_oferecem_desafio_e_nivel_2_usa_minusculas(tela):
    _abrir(tela)
    _acertar_todas(tela)
    assert tela.oferece_desafio and tela.botao_sim.isVisible()
    assert not tela.botao_proximo.isVisible()
    tela.proximo()  # sem responder, não avança
    assert tela.momento == FIM

    tela.responder_desafio(True)
    assert tela.nivel.nivel == 2 and tela.momento == ATIVIDADE
    minusculas = [letra.lower() for letra in tela.rodada.letras]  # o desafio já é o bloco seguinte
    assert [p.rotulo for p in tela.cena.pecas.values()] == minusculas
    _acertar_todas(tela)  # minúscula na caixa da maiúscula
    assert tela.momento == FIM


def test_recusar_o_desafio_mantem_o_nivel(tela):
    _abrir(tela)
    _acertar_todas(tela)
    tela.responder_desafio(False)
    assert tela.nivel.nivel == 1 and tela.momento == ATIVIDADE


def test_dois_modelos_seguidos_voltam_um_nivel(tela):
    _abrir(tela)
    tela.nivel.nivel = 2
    tela.proximo  # noqa: B018 - só para deixar claro que a rodada atual segue
    for item in range(2):
        for _ in range(3):
            letras = tela.rodada.letras
            outra = (item + 1) % len(letras)
            _jogar(tela, logica.id_peca(letras[outra], outra), logica.id_caixa(item))
    _acertar_todas(tela)
    assert tela.nivel.nivel == 1
    assert tela.ultimo_anuncio == texto("base.nivel_voltou")


def test_nivel_travado_nao_oferece_desafio(tela):
    _abrir(tela)
    tela.nivel.travado = True
    _acertar_todas(tela)
    assert not tela.oferece_desafio and tela.botao_proximo.isVisible()


# --- pausa -------------------------------------------------------------------------


def test_pausa_congela_cobre_e_silencia(tela, qtbot):
    _abrir(tela)
    qtbot.mouseClick(tela.botao_pausa, Qt.LeftButton)
    assert tela.pausada and tela.camada_pausa.isVisible()
    assert tela.ctx.audio.silenciado
    _jogar(tela, logica.id_peca("A", 0), logica.id_caixa(0))
    assert not tela.rodada.colocadas  # nada acontece durante a pausa

    qtbot.keyClick(tela.camada_pausa, Qt.Key_Escape)  # Esc também continua
    assert not tela.pausada and not tela.camada_pausa.isVisible()
    assert not tela.ctx.audio.silenciado
    _jogar(tela, logica.id_peca("A", 0), logica.id_caixa(0))
    assert "A" in tela.rodada.colocadas


def test_esc_pausa(tela, qtbot):
    _abrir(tela)
    qtbot.keyClick(tela, Qt.Key_Escape)
    assert tela.pausada


# --- áudio e perfis -------------------------------------------------------------------


def test_voz_so_diz_as_letras_pegas(tela):
    _abrir(tela, ["dislexia", "cegueira"])  # nenhum perfil lê instrução ou retorno em voz
    assert tela.ctx.audio.log == []
    _acertar_todas(tela)
    letras = tela.rodada.letras
    assert tela.ctx.audio.log == [f"toca {tela.ctx.audio.arquivo_de(letra)}" for letra in letras]
    assert all(tela.ctx.audio.arquivo_de(letra) for letra in letras)


def test_tea_com_aviso_de_troca(tela):
    _abrir(tela, ["tea"])
    _acertar_todas(tela)
    assert texto("base.aviso_troca") in tela.texto_fim_detalhe.text()


# --- registro ------------------------------------------------------------------------


def test_cada_resposta_vira_tentativa(tela):
    _abrir(tela, ["tea", "motor"])
    _errar_a(tela)
    _acertar_todas(tela)
    tentativas = tela.ctx.registro.listar_tentativas()
    assert len(tentativas) == 1 + len(tela.rodada.letras)
    primeira = tentativas[0]
    assert primeira["aluno"] == "visitante"
    assert primeira["atividade"] == "treino"
    assert primeira["habilidade"] == texto("treino.habilidade")
    assert (primeira["item"], primeira["resposta"], primeira["correta"]) == ("A", "B", False)
    assert primeira["perfis"] == ["tea", "motor"]
    assert primeira["tempo_ms"] >= 0
    assert all(t["correta"] for t in tentativas[1:])


def test_estado_completo(tela):
    _abrir(tela, ["motor"])
    estado = tela.estado()
    for chave in ("tela", "momento", "nivel", "instrucao", "itens", "alvos", "pista_nivel",
                  "pausada", "oferece_desafio", "concluida", "anuncio", "modo_entrada"):
        assert chave in estado
    assert estado["tela"] == "treino" and estado["momento"] == ATIVIDADE
    assert len(estado["itens"]) == combinar(["motor"]).max_itens


# --- botão de câmera -------------------------------------------------------------------


def test_atividade_comeca_com_a_camera_ligada_e_o_botao_desliga(tela, qtbot):
    _abrir(tela)
    assert tela.camera_ligada and tela.botao_camera.isChecked()
    assert tela.botao_camera.accessibleName() == texto("base.camera_desligar")
    qtbot.mouseClick(tela.botao_camera, Qt.LeftButton)
    assert not tela.camera_ligada
    assert tela.botao_camera.accessibleName() == texto("base.camera_ligar")
    assert tela.indicador.accessibleName() == "Câmera desligada"
    _acertar_todas(tela)  # mouse e teclado continuam funcionando
    assert tela.momento == FIM
    qtbot.mouseClick(tela.botao_camera, Qt.LeftButton)
    assert tela.camera_ligada


def test_reabrir_a_atividade_religa_a_camera(tela):
    _abrir(tela)
    tela.botao_camera.setChecked(False)
    _abrir(tela)
    assert tela.camera_ligada and tela.botao_camera.isChecked()


class _CameraLenta(Camera):
    """Thread que demora a terminar, como a câmera real enquanto o MediaPipe carrega."""

    def run(self):
        self.msleep(300)
        self.estado.emit("desligada")

    def parar(self):
        self.requestInterruption()  # não espera: a thread segue rodando


def test_desligar_camera_que_ainda_carrega_nao_derruba_nem_mexe_no_indicador(qtbot, monkeypatch):
    monkeypatch.setenv("ATLAS_SEM_ANIMACAO", "1")
    contexto = Contexto(
        Registro(":memory:"), ServicoAudio(backend="nulo"), Sessao(), _CameraLenta
    )
    tela = TelaTreino(contexto)
    qtbot.addWidget(tela)
    _abrir(tela)
    camera = tela.camera
    tela.botao_camera.setChecked(False)  # desliga com a thread rodando
    assert camera in camera_mod._encerrando
    tela.indicador.mostrar("ligada")  # se o sinal antigo chegasse, voltaria para "desligada"
    qtbot.waitUntil(lambda: camera not in camera_mod._encerrando, timeout=3000)
    assert tela.indicador.rotulo.text() == texto("teste_camera.camera_ligada")


def test_indicador_avisa_quando_nao_ha_camera(tela):
    _abrir(tela)  # CameraNula: sem opencv/mediapipe ou sem webcam
    assert tela.indicador.rotulo.text() == texto("teste_camera.camera_indisponivel")
