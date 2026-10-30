"""Baixa o modelo MediaPipe Hand Landmarker (Apache 2.0) para assets/modelos/."""

from _download import RAIZ, baixar

URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)


def main() -> None:
    baixar(URL, RAIZ / "assets" / "modelos" / "hand_landmarker.task", tamanho_minimo=1_000_000)


if __name__ == "__main__":
    main()
