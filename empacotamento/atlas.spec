# PyInstaller, modo onedir (onefile descompactaria o mediapipe a cada abertura).
# Gerar:  pyinstaller empacotamento/atlas.spec --noconfirm   (na raiz do repositório)
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

RAIZ = Path(SPECPATH).parent  # noqa: F821 - SPECPATH vem do PyInstaller

datas = [(str(RAIZ / "assets"), "assets"), (str(RAIZ / "conteudo"), "conteudo")]
binaries = []
hiddenimports = []
for pacote in ("mediapipe",):
    d, b, h = collect_all(pacote)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(  # noqa: F821
    [str(RAIZ / "empacotamento" / "atlas_launcher.py")],
    pathex=[str(RAIZ)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + ["app.cli", "app.main"],
    excludes=["tkinter", "pytest", "ruff", "IPython"],
    noarchive=False,
)
pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Atlas",
    console=False,  # sem janela de console para a criança
    upx=False,
)
coleta = COLLECT(exe, a.binaries, a.datas, name="Atlas", upx=False)  # noqa: F821

if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        coleta,
        name="Atlas.app",
        bundle_identifier="br.hackathon.atlas",
        info_plist={
            "CFBundleName": "Atlas",
            "CFBundleDisplayName": "Atlas",
            "NSHighResolutionCapable": True,
            "NSCameraUsageDescription": (
                "O Atlas usa a câmera só para ver a mão da criança. "
                "Nenhuma imagem é salva ou enviada."
            ),
            "NSMicrophoneUsageDescription": "O Atlas não grava áudio.",
        },
    )
