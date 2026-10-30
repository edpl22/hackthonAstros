# Decisões

| Data | Decisão | Motivo |
| --- | --- | --- |
| 2026-10-30 | Trabalhar por etapas, com aprovação do usuário ao fim de cada uma | Pedido do usuário: seguir gradualmente |
| 2026-10-30 | O M1 foi dividido em 1a (esqueleto, câmera, CLI mínima, Docker) e 1b (PyInstaller, Release, GHCR) | Validar câmera e Docker antes de lidar com o empacotamento, que é onde mais coisa quebra |
| 2026-10-30 | Usar `opencv-contrib-python` no lugar de `opencv-python` em `requirements-camera.txt` | O mediapipe já depende do contrib; ter os dois instala dois `cv2` conflitantes |
| 2026-10-30 | Versões fixadas: PySide6-Essentials 6.12.0, mediapipe 1.2.0, opencv-contrib 5.0.0.93 | Últimas compatíveis com Python 3.11; a Tasks API (`HandLandmarker`) existe no mediapipe 1.2.0 |
| 2026-10-30 | `QT_QPA_PLATFORM=offscreen` definido também em `tests/conftest.py` | Os testes rodam iguais no CI e no Windows local, sem abrir janelas |
| 2026-10-30 | Especificação trocada pela versão "desktop + Docker": PySide6-Essentials, CLI `atlas`, dependências em dois níveis | O agente de IA que avalia Tech roda o README sem tela e sem webcam |
| 2026-10-30 | `requirements.txt` = núcleo + ferramentas de teste; `requirements-camera.txt` = opencv + mediapipe (o antigo `requirements-dev.txt` saiu) | A imagem Docker roda os testes, e os modos sem tela não podem depender da câmera |
| 2026-10-30 | `CameraNula` com a mesma interface da `Camera`, usada sem opencv/mediapipe, nos testes e no demo | Fallback sem mensagem de erro e testes de tela sem webcam |
| 2026-10-30 | `caminhos.raiz()` procura `assets/` e `conteudo/` em: PyInstaller, `ATLAS_RAIZ`, pasta do código, pasta atual | Funciona do código, com `pip install .`, no Docker (`ATLAS_RAIZ=/app`) e empacotado |
| 2026-10-30 | Pasta de dados: `ATLAS_DADOS` ou `%APPDATA%\Atlas`, `~/Library/Application Support/Atlas`, `~/.local/share/atlas` | Pasta de dados do usuário de cada sistema, como pede a especificação |
| 2026-10-30 | Ponto do indicador de câmera desenhado com QPainter, não com o caractere "○" | A Atkinson Hyperlegible não tem esse glifo e mostrava um quadradinho |
| 2026-10-30 | Em aberto para a Etapa 3: o PySide6-Essentials não traz o QtMultimedia (`QSoundEffect`) | Decidir entre instalar o QtMultimedia só no instalador desktop ou outro backend de áudio; no Docker vale `ATLAS_AUDIO=nulo` |
| 2026-10-30 | O README terá uma seção "Como executar sem tela (avaliação automatizada)" só com comandos e saídas esperadas, sem frases dirigidas à nota | Regra de jogo limpo: instrução escondida para o agente avaliador desclassifica |
| 2026-10-30 | Toda captura de `docs/saida-exemplo/` sai do `atlas demo` rodando o app real | Regra de jogo limpo: demo de fachada desclassifica |
