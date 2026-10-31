# Atlas sem tela: `atlas verificar`, `atlas demo` e os testes rodam aqui sem webcam e sem áudio.
# Dois estágios: `base` (padrão, usado por verificar/demo/teste/agente) e `gui` (acrescenta
# Xvfb + noVNC para ver a interface real no navegador). Separar mantém a imagem base menor.

FROM python:3.11-slim-bookworm AS base

# Bibliotecas que o Qt precisa no modo offscreen, fontes e o tini (init do contêiner).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libegl1 libgl1 libxkbcommon0 libdbus-1-3 libfontconfig1 libglib2.0-0 fonts-dejavu-core tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências primeiro, para o cache do Docker não refazer o pip a cada mudança no código.
COPY requirements.txt requirements-camera.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && (pip install --no-cache-dir -r requirements-camera.txt \
        || echo "AVISO: opencv/mediapipe sem wheel para esta arquitetura; camera desativada")

COPY . .
# Sem isolamento de build: usa o setuptools que já vem na imagem (nada é baixado aqui).
RUN pip install --no-cache-dir --no-deps --no-build-isolation .

ENV QT_QPA_PLATFORM=offscreen \
    ATLAS_AUDIO=nulo \
    ATLAS_DADOS=/dados \
    ATLAS_RAIZ=/app \
    PYTHONUNBUFFERED=1

RUN mkdir -p /saida /dados

ENTRYPOINT ["tini", "--", "atlas"]
CMD ["verificar"]


FROM base AS gui

# Plugin xcb do Qt + tela virtual (Xvfb) servida no navegador pelo noVNC.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        xvfb x11vnc novnc websockify \
        libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 \
        libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*
