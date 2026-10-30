"""opencv e mediapipe são opcionais: só `entrada/camera.py` os importa, e só dentro de funções."""

import re
from pathlib import Path

RAIZ_APP = Path(__file__).resolve().parent.parent / "app"
IMPORT_CAMERA = re.compile(r"^(\s*)(import|from)\s+(cv2|mediapipe)\b", re.MULTILINE)


def test_cv2_e_mediapipe_so_dentro_de_camera_py_e_preguicosos():
    for arquivo in sorted(RAIZ_APP.rglob("*.py")):
        for recuo, *_ in IMPORT_CAMERA.findall(arquivo.read_text(encoding="utf-8")):
            nome = arquivo.relative_to(RAIZ_APP).as_posix()
            assert nome == "entrada/camera.py", f"{nome} importa a câmera"
            assert recuo, f"{nome} importa a câmera no topo do módulo"
