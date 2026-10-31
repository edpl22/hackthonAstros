"""Serviço de áudio: toca o WAV da letra, da sílaba ou da palavra pelo manifesto.

O PySide6-Essentials não traz o QtMultimedia, então o WAV é tocado pelo próprio sistema:
`winsound` no Windows, `afplay` no macOS e `paplay`/`aplay` no Linux. Sem dispositivo de
áudio (Docker, testes), `ATLAS_AUDIO=nulo` só registra no log o que tocaria.
Só o português tem voz; instruções e retornos ficam na legenda da atividade.
"""

import array
import io
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import wave
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.nucleo import caminhos
from app.nucleo.conteudo import carregar

PAUSA_INICIAL_MS = 150  # fone Bluetooth e HDMI "acordam" no começo do som e engolem a 1ª sílaba


def _wav_com_volume(caminhos_wav, volume: float) -> bytes:
    """Junta os WAV (PCM 16 bits, mesmo formato), põe uma pausa curta no início e multiplica as
    amostras pelo volume."""
    if isinstance(caminhos_wav, Path):
        caminhos_wav = [caminhos_wav]
    quadros = b""
    parametros = None
    for caminho in caminhos_wav:
        with wave.open(str(caminho), "rb") as entrada:
            parametros = parametros or entrada.getparams()
            quadros += entrada.readframes(entrada.getnframes())
    n_silencio = parametros.framerate * PAUSA_INICIAL_MS // 1000
    quadros = b"\x00" * (n_silencio * parametros.sampwidth * parametros.nchannels) + quadros
    amostras = array.array("h", quadros)
    if sys.byteorder == "big":
        amostras.byteswap()
    if volume < 0.999:
        amostras = array.array("h", (int(a * volume) for a in amostras))
    if sys.byteorder == "big":
        amostras.byteswap()
    saida = io.BytesIO()
    with wave.open(saida, "wb") as destino:
        destino.setparams(parametros)
        destino.writeframes(amostras.tobytes())
    return saida.getvalue()


class _TocadorSistema:
    """Toca em fila, numa thread: uma fala não corta a anterior (a sílaba e depois "Terminou!").
    Se a criança age rápido, as falas antigas que ainda não começaram são descartadas."""

    MAX_ESPERANDO = 1

    def __init__(self):
        self._cache: dict[tuple, bytes] = {}
        self._fila: queue.Queue = queue.Queue()
        threading.Thread(target=self._trabalhar, daemon=True).start()

    def tocar(self, caminhos_wav: list[Path], volume: float) -> None:
        chave = (tuple(str(c) for c in caminhos_wav), round(volume, 2))
        if chave not in self._cache:
            self._cache[chave] = _wav_com_volume(caminhos_wav, volume)
        while self._fila.qsize() >= self.MAX_ESPERANDO:
            try:
                self._fila.get_nowait()
            except queue.Empty:
                break
        self._fila.put((chave, self._cache[chave]))

    def _trabalhar(self) -> None:
        while True:
            chave, dados = self._fila.get()
            try:
                self._tocar_agora(chave, dados)
            except Exception:  # noqa: BLE001 - sem som não pode derrubar a atividade
                pass

    @staticmethod
    def _tocar_agora(chave, dados: bytes) -> None:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(dados, winsound.SND_MEMORY | winsound.SND_NODEFAULT)
            return
        # macOS e Linux tocam de um arquivo: o WAV juntado vai para a pasta temporária.
        arquivo = Path(tempfile.gettempdir()) / f"atlas-{abs(hash(chave))}.wav"
        if not arquivo.exists():
            arquivo.write_bytes(dados)
        if sys.platform == "darwin":
            subprocess.run(["afplay", str(arquivo)], check=False)
        elif shutil.which("paplay"):
            subprocess.run(["paplay", str(arquivo)], check=False)
        elif shutil.which("aplay"):
            subprocess.run(["aplay", "-q", str(arquivo)], check=False)

    def parar(self) -> None:
        while not self._fila.empty():
            try:
                self._fila.get_nowait()
            except queue.Empty:
                break
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(None, 0)


class ServicoAudio(QObject):
    legenda = Signal(str)  # toda frase falada também vira legenda na tela

    def __init__(self, backend: str | None = None, volume: float = 1.0, parent=None):
        super().__init__(parent)
        self.backend = backend or os.environ.get("ATLAS_AUDIO", "sistema")
        self.volume = volume
        self.silenciado = False
        self.log: list[str] = []
        self._tocador = _TocadorSistema() if self.backend != "nulo" else None
        try:
            self.manifesto: dict[str, str] = carregar("manifesto_audio.json")["frases"]
        except FileNotFoundError:
            self.manifesto = {}

    def arquivo_de(self, texto: str) -> str | None:
        return self.manifesto.get(texto)

    def falar(self, texto: str) -> None:
        if not texto:
            return
        self.legenda.emit(texto)
        if self.silenciado:
            self.log.append(f"silenciado: {texto}")
            return
        arquivo = self.arquivo_de(texto)
        if arquivo is None:
            self.log.append(f"legenda (sem wav): {texto}")
            return
        self.log.append(f"toca {arquivo}")
        if self._tocador is not None and self.volume > 0:
            self._tocador.tocar([caminhos.asset("audio", arquivo)], self.volume)

    def silenciar(self, silenciado: bool) -> None:
        """Pausa silencia tudo na hora."""
        self.silenciado = silenciado
        if silenciado and self._tocador is not None:
            self._tocador.parar()

    def definir_volume(self, volume: float) -> None:
        self.volume = min(1.0, max(0.0, volume))
