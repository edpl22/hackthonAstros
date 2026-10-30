# Atlas sem tela: `atlas verificar`, `atlas demo` e os testes rodam aqui sem webcam e sem áudio.
FROM python:3.11-slim-bookworm

# Bibliotecas do Qt (offscreen e xcb para o modo gui), fontes e ferramentas do modo gui (noVNC).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libegl1 libgl1 libxkbcommon0 libdbus-1-3 libfontconfig1 libglib2.0-0 fonts-dejavu-core \
        xvfb x11vnc novnc websockify tini \
        libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
        libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências primeiro, para o cache do Docker não refazer o pip a cada mudança no código.
COPY requirements.txt requirements-camera.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && (pip install --no-cache-dir -r requirements-camera.txt \
        || echo "AVISO: opencv/mediapipe sem wheel para esta arquitetura; camera desativada")

COPY . .
RUN pip install --no-cache-dir --no-deps .

ENV QT_QPA_PLATFORM=offscreen \
    ATLAS_AUDIO=nulo \
    ATLAS_DADOS=/dados \
    ATLAS_RAIZ=/app \
    PYTHONUNBUFFERED=1

RUN mkdir -p /saida /dados

ENTRYPOINT ["tini", "--", "atlas"]
CMD ["verificar"]
