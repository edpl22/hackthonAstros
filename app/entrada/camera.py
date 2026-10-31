"""Câmera numa QThread: OpenCV captura, MediaPipe acha a mão, sinais levam os pontos.

OpenCV e MediaPipe só são importados dentro de `run()`, para o app abrir rápido.
Nenhum quadro é salvo: cada imagem vive só dentro do laço.
"""

import importlib.util
import sys
import time
import warnings

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QImage

from app.nucleo import caminhos

LARGURA, ALTURA = 640, 480
LARGURA_REDUZIDA, ALTURA_REDUZIDA = 480, 360
FPS_MINIMO = 15
MINIATURA = (160, 120)
TEMPO_MAX_ABRIR_S = 3.0
INTERVALO_FPS_S = 0.5


class Camera(QThread):
    # lista de 21 (x, y, z) normalizados (já espelhados) e se há mão no quadro
    pontos = Signal(object, bool)
    fps = Signal(float)
    # "ligando", "ligada", "indisponivel" ou "desligada"
    estado = Signal(str)
    miniatura = Signal(QImage)

    def __init__(self, indice: int = 0, mostrar_miniatura: bool = False, parent=None):
        super().__init__(parent)
        self.indice = indice
        self.mostrar_miniatura = mostrar_miniatura

    def parar(self) -> None:
        self.requestInterruption()
        self.wait(2000)

    def _abrir_captura(self, cv2):
        if sys.platform == "win32":
            captura = cv2.VideoCapture(self.indice, cv2.CAP_DSHOW)
        else:
            captura = cv2.VideoCapture(self.indice)
        captura.set(cv2.CAP_PROP_FRAME_WIDTH, LARGURA)
        captura.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTURA)
        captura.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # só o quadro mais recente
        return captura

    def _criar_detector(self):
        import mediapipe as mp
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python.vision import (
            HandLandmarker,
            HandLandmarkerOptions,
            RunningMode,
        )

        # Lido como bytes: o caminho do modelo pode ter acentos, que o MediaPipe não aceita.
        modelo = caminhos.asset("modelos", "hand_landmarker.task").read_bytes()
        opcoes = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_buffer=modelo),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
        )
        return mp, HandLandmarker.create_from_options(opcoes)

    def run(self) -> None:
        self.estado.emit("ligando")
        try:
            import cv2

            mp, detector = self._criar_detector()
        except Exception:
            self.estado.emit("indisponivel")
            return

        captura = None
        final = "desligada"
        try:
            captura = self._abrir_captura(cv2)
            if not self._laco(cv2, mp, detector, captura):
                final = "indisponivel"
        except Exception:  # webcam arrancada ou erro do MediaPipe: o app segue sem câmera
            final = "indisponivel"
        finally:
            if captura is not None:
                captura.release()
            detector.close()
            self.estado.emit(final)

    def _laco(self, cv2, mp, detector, captura) -> bool:
        """Lê quadros até pedirem para parar (devolve True) ou a câmera sumir (False)."""
        inicio = time.monotonic()
        ligada = False
        ultimo_quadro = inicio
        ultimo_ts_ms = -1
        quadros, marca_fps = 0, time.monotonic()
        medias: list[float] = []
        reduzida = False

        while not self.isInterruptionRequested():
            ok, quadro = captura.read() if captura.isOpened() else (False, None)
            agora = time.monotonic()
            if not ok:
                # Sem quadro por 3 s, ao abrir ou no meio do uso (webcam desconectada).
                if agora - ultimo_quadro > TEMPO_MAX_ABRIR_S:
                    return False
                self.msleep(30)
                continue
            ultimo_quadro = agora
            if not ligada:
                ligada = True
                self.estado.emit("ligada")

            quadro = cv2.flip(quadro, 1)  # espelho: a mão direita aparece à direita
            rgb = cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)

            # O MediaPipe exige timestamps em ms sempre crescentes.
            ts_ms = max(int((agora - inicio) * 1000), ultimo_ts_ms + 1)
            ultimo_ts_ms = ts_ms
            resultado = detector.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ts_ms
            )
            if resultado.hand_landmarks:
                lista = [(p.x, p.y, p.z) for p in resultado.hand_landmarks[0]]
                self.pontos.emit(lista, True)
            else:
                self.pontos.emit([], False)

            if self.mostrar_miniatura:
                pequena = cv2.resize(rgb, MINIATURA)
                altura, largura = pequena.shape[:2]
                imagem = QImage(pequena.data, largura, altura, 3 * largura, QImage.Format_RGB888)
                self.miniatura.emit(imagem.copy())

            quadros += 1
            if agora - marca_fps >= INTERVALO_FPS_S:
                fps = quadros / (agora - marca_fps)
                self.fps.emit(fps)
                quadros, marca_fps = 0, agora
                medias.append(fps)
                # Máquina lenta: média abaixo de 15 fps nos últimos 2 s -> 480 x 360, uma vez.
                if not reduzida and len(medias) >= 4 and sum(medias[-4:]) / 4 < FPS_MINIMO:
                    captura.set(cv2.CAP_PROP_FRAME_WIDTH, LARGURA_REDUZIDA)
                    captura.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTURA_REDUZIDA)
                    reduzida = True
        return True


class CameraNula(QObject):
    """Mesma interface da `Camera`, sem câmera: usada sem opencv/mediapipe, nos testes e no demo."""

    pontos = Signal(object, bool)
    fps = Signal(float)
    estado = Signal(str)
    miniatura = Signal(QImage)

    def __init__(self, mostrar_miniatura: bool = False, parent=None):
        super().__init__(parent)
        self.mostrar_miniatura = mostrar_miniatura

    def start(self) -> None:
        self.estado.emit("indisponivel")

    def parar(self) -> None:
        self.estado.emit("desligada")


# Câmeras que ainda estão terminando. Guardar a referência evita destruir a QThread rodando,
# o que derruba o app (ex.: desligar enquanto o MediaPipe ainda carrega).
_encerrando: set = set()


def encerrar(camera) -> None:
    """Para a câmera sem travar a tela nem derrubar o app. Os sinais são desligados antes,
    para que um estado ou ponto atrasado não chegue a uma tela que já ligou outra câmera."""
    with warnings.catch_warnings():  # o PySide avisa quando o sinal não tinha conexão
        warnings.simplefilter("ignore", RuntimeWarning)
        for sinal in (camera.pontos, camera.fps, camera.estado, camera.miniatura):
            try:
                sinal.disconnect()
            except (RuntimeError, TypeError):
                pass
    camera.parar()
    if isinstance(camera, QThread) and camera.isRunning():
        _encerrando.add(camera)
        camera.finished.connect(lambda: _encerrando.discard(camera))
        camera.finished.connect(camera.deleteLater)
    else:
        camera.deleteLater()


def esperar_encerramento(ms: int = 5000) -> None:
    """Ao fechar o app: dá tempo para as câmeras que ainda estão terminando."""
    for camera in list(_encerrando):
        camera.wait(ms)


def pacotes_disponiveis() -> bool:
    """Confere se opencv e mediapipe estão instalados, sem importá-los."""
    return all(importlib.util.find_spec(nome) is not None for nome in ("cv2", "mediapipe"))


def testar_detector() -> None:
    """Carrega OpenCV, MediaPipe e o modelo da mão sem abrir a webcam (`verificar --completo`).
    Levanta a exceção original se algo faltar."""
    import cv2  # noqa: F401 - só confere que carrega

    _mp, detector = Camera()._criar_detector()
    detector.close()


def fabrica_padrao():
    return Camera if pacotes_disponiveis() else CameraNula
