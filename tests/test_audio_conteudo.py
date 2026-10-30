import importlib.util
import wave
from pathlib import Path

from app.nucleo import audio, caminhos
from app.nucleo.audio import ServicoAudio
from app.nucleo.conteudo import texto

RAIZ = Path(__file__).resolve().parent.parent


def _script(nome):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "scripts" / f"{nome}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_conteudo_valido():
    assert _script("validar_conteudo").validar() == []


def test_todo_texto_coletado_tem_audio():
    gerar = _script("gerar_audio")
    servico = ServicoAudio(backend="nulo")
    faltando = [t for t in gerar.coletar_textos() if servico.arquivo_de(t) is None]
    assert faltando == []


def test_backend_nulo_registra_o_que_tocaria(qtbot):
    servico = ServicoAudio(backend="nulo")
    legendas = []
    servico.legenda.connect(legendas.append)
    frase = texto("base.terminou")
    servico.falar(frase)
    servico.falar("Frase que não tem áudio.")
    assert servico.log[0].startswith("toca ") and servico.log[0].endswith(".wav")
    assert servico.log[1] == "legenda (sem wav): Frase que não tem áudio."
    assert legendas == [frase, "Frase que não tem áudio."]  # a legenda aparece sempre


def test_pausa_silencia(qtbot):
    servico = ServicoAudio(backend="nulo")
    servico.silenciar(True)
    servico.falar(texto("base.terminou"))
    assert servico.log == [f"silenciado: {texto('base.terminou')}"]


def test_volume_multiplica_as_amostras():
    arquivo = next(caminhos.asset("audio").glob("*.wav"))
    original = audio._wav_com_volume(arquivo, 1.0)
    metade = audio._wav_com_volume(arquivo, 0.5)
    import array
    import io

    def pico(dados):
        with wave.open(io.BytesIO(dados), "rb") as w:
            return max(abs(a) for a in array.array("h", w.readframes(w.getnframes())))

    assert abs(pico(metade) - pico(original) // 2) <= 1


def test_volume_limitado():
    servico = ServicoAudio(backend="nulo")
    servico.definir_volume(3)
    assert servico.volume == 1.0
    servico.definir_volume(-1)
    assert servico.volume == 0.0


def test_frase_composta_junta_os_trechos_que_tem_audio():
    servico = ServicoAudio(backend="nulo")
    voltou = texto("anuncio.voltou").format(item="B")
    instrucao = texto("treino.instrucao").format(letra="A")
    arquivos = servico.arquivos_de(f"{voltou} {instrucao}")
    assert arquivos == [servico.arquivo_de(voltou), servico.arquivo_de(instrucao)]
    assert servico.arquivos_de(f"{voltou} Frase nova sem audio.") is None


def test_juntar_wavs_soma_as_duracoes():
    arquivos = sorted(caminhos.asset("audio").glob("*.wav"))[:2]
    juntos = audio._wav_com_volume(arquivos, 1.0)
    import io

    def quadros(dados_ou_caminho):
        eh_bytes = isinstance(dados_ou_caminho, bytes)
        alvo = io.BytesIO(dados_ou_caminho) if eh_bytes else str(dados_ou_caminho)
        with wave.open(alvo, "rb") as w:
            return w.getnframes()

    assert quadros(juntos) == quadros(arquivos[0]) + quadros(arquivos[1])
