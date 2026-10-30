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
| 2026-10-30 | Dockerfile em dois estágios: `base` (verificar, demo, teste, agente) e `gui` (acrescenta Xvfb, x11vnc, noVNC e libs xcb) | Os pacotes do modo gui somavam ~350 MB; a imagem base ficou com 1,2 GB de conteúdo (`du -sxh /`), abaixo da meta de 1,5 GB |
| 2026-10-30 | Contêiner roda como root | Evita problemas de permissão nos volumes montados (`./saida`) |
| 2026-10-30 | Nova atividade "Treino de arrastar" (peças A–D nas caixas A–D) | Valida a camada de entrada com uma atividade real antes das três do MVP, ensina a criança a pegar e soltar, e vira a base da cena do Ímã das Sílabas |
| 2026-10-30 | Perfil ganhou campos extras: `aviso_troca_atividade`, `contorno_px`, `silabas_alternadas`, `resposta_por_escolha`, `varredura_disponivel`, `descrever_foco`, `miniatura_camera` | A tabela de perfis cita esses comportamentos; cada um vira um campo que combina pela mesma regra |
| 2026-10-30 | Na combinação, `som_celebracao` e `miniatura_camera`: False vence; entrada: teclado > permanência > ponteiro | Desligar estímulo é o mais acessível; teclado atende cegueira, que é a necessidade mais restritiva |
| 2026-10-30 | A mão simulada gera os 21 pontos a partir de passos ("ir até a peça B", "fechar a pinça"), em vez de guardar pontos crus no JSON | O roteiro funciona em qualquer tamanho e perfil; os pontos ainda passam pelo `mao.py` real (filtro, área ativa, pinça) |
| 2026-10-30 | Cena das atividades com tamanho lógico fixo 1280 x 720, escalada para caber na janela | Coordenadas iguais no demo, no agente e na tela; o mouse é convertido com `mapToScene` |
| 2026-10-30 | Modos sem tela usam `ATLAS_SEM_ANIMACAO=1` | Capturas e testes determinísticos; na interface, as animações seguem com até 250 ms (0 com "reduzir movimento") |
| 2026-10-30 | Varredura liga por opção da atividade (`varredura=True`), não sozinha no perfil motor | O perfil motor já usa permanência; ligar a varredura será uma opção na área do adulto |
| 2026-10-30 | Esc só emite `pausar` (e anuncia) por enquanto; a tela de Pausa entra com a `AtividadeBase` na Etapa 3 | Mantém a etapa no escopo combinado |
| 2026-10-30 | Formulário da área do adulto dentro de uma área com rolagem | Em 1280 x 720 o formulário não cabia e os itens se sobrepunham (visto na captura) |
| 2026-10-30 | Toda captura de `docs/saida-exemplo/` sai do `atlas demo` rodando o app real | Regra de jogo limpo: demo de fachada desclassifica |
