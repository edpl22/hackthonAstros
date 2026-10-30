"""Download simples para os scripts de preparo. O app em si nunca acessa a rede."""

import shutil
import tempfile
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def baixar(url: str, destino: Path, tamanho_minimo: int = 1) -> None:
    """Baixa `url` para `destino`, gravando primeiro num arquivo temporário."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as resposta, tempfile.NamedTemporaryFile(
        delete=False, dir=destino.parent, suffix=".parcial"
    ) as tmp:
        shutil.copyfileobj(resposta, tmp)
        caminho_tmp = Path(tmp.name)
    if caminho_tmp.stat().st_size < tamanho_minimo:
        caminho_tmp.unlink()
        raise RuntimeError(f"Download incompleto: {url}")
    caminho_tmp.replace(destino)
    print(f"ok  {destino.relative_to(RAIZ)}  ({destino.stat().st_size:,} bytes)")
