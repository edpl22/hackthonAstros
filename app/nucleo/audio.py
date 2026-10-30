"""Serviço de áudio: toca o WAV de cada frase pelo manifesto e sempre mostra a legenda.

O PySide6-Essentials não traz o QtMultimedia, então o WAV é tocado pelo próprio sistema:
`winsound` no Windows, `afplay` no macOS e `paplay`/`aplay` no Linux. Sem dispositivo de
áudio (Docker, testes), `ATLAS_AUDIO=nulo` só registra no log o que tocaria.
Regra pedagógica: nenhum som de "errado"; quem chama decide quando falar (após uma ação).
"""

import array
import io
import os
import re
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


def dividir_em_frases(texto: str) -> list[str]:
    return [f for f in re.split(r"(?<=[.!?])\s+", texto.strip()) if f]


def _wav_com_volume(caminhos_wav, volume: float) -> bytes:
    """Junta os WAV (PCM 16 bits, mesmo formato) e multiplica as amostras pelo volume."""
    if isinstance(caminhos_wav, Path):
        caminhos_wav = [caminhos_wav]
    quadros = b""
    parametros = None
    for caminho in caminhos_wav:
        with wave.open(str(caminho), "rb") as entrada:
            parametros = parametros or entrada.getparams()
            quadros += entrada.readframes(entrada.getnframes())
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
    def __init__(self):
        self._cache: dict[tuple[str, float], bytes] = {}

    def tocar(self, caminhos_wav: list[Path], volume: float) -> None:
        chave = (tuple(str(c) for c in caminhos_wav), round(volume, 2))
        if chave not in self._cache:
            self._cache[chave] = _wav_com_volume(caminhos_wav, volume)
        dados = self._cache[chave]
        if sys.platform == "win32":

            def tocar_windows():
                import winsound

                winsound.PlaySound(dados, winsound.SND_MEMORY | winsound.SND_NODEFAULT)

            threading.Thread(target=tocar_windows, daemon=True).start()
            return
        # macOS e Linux tocam de um arquivo: o WAV juntado vai para a pasta temporária.
        arquivo = Path(tempfile.gettempdir()) / f"atlas-{abs(hash(chave))}.wav"
        if not arquivo.exists():
            arquivo.write_bytes(dados)
        if sys.platform == "darwin":
            subprocess.Popen(["afplay", str(arquivo)])
        elif shutil.which("paplay"):
            subprocess.Popen(["paplay", str(arquivo)])
        elif shutil.which("aplay"):
            subprocess.Popen(["aplay", "-q", str(arquivo)])

    def parar(self) -> None:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(None, winsound.SND_PURGE)


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

    def arquivos_de(self, texto: str) -> list[str] | None:
        """WAVs que, em sequência, falam o texto. Frases compostas ("A letra B voltou...
        Pegue a letra A...") são montadas com os maiores trechos que existem no manifesto."""
        if texto in self.manifesto:
            return [self.manifesto[texto]]
        frases = dividir_em_frases(texto)
        arquivos, i = [], 0
        while i < len(frases):
            for j in range(len(frases), i, -1):
                trecho = " ".join(frases[i:j])
                if trecho in self.manifesto:
                    arquivos.append(self.manifesto[trecho])
                    i = j
                    break
            else:
                return None
        return arquivos

    def falar(self, texto: str) -> None:
        if not texto:
            return
        self.legenda.emit(texto)
        if self.silenciado:
            self.log.append(f"silenciado: {texto}")
            return
        arquivos = self.arquivos_de(texto)
        if arquivos is None:
            self.log.append(f"legenda (sem wav): {texto}")
            return
        self.log.append("toca " + " + ".join(arquivos))
        if self._tocador is not None and self.volume > 0:
            self._tocador.tocar([caminhos.asset("audio", a) for a in arquivos], self.volume)

    def silenciar(self, silenciado: bool) -> None:
        """Pausa silencia tudo na hora."""
        self.silenciado = silenciado
        if silenciado and self._tocador is not None:
            self._tocador.parar()

    def definir_volume(self, volume: float) -> None:
        self.volume = min(1.0, max(0.0, volume))
