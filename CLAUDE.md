# CLAUDE.md — Atlas

Memória do projeto. Releia este arquivo se perder o contexto. A especificação vigente é o prompt "Atlas (software desktop + Docker)" (seções 1–15); o resumo do andamento está em `docs/PROGRESSO.md`.

## Regras do hackathon (slides de abertura)

- **Entrega até 13h de sábado (31/10/2026), sem prorrogação.** Três entregas: vídeo de demo de até 5 min, plano de negócio em PDF e deploy ou MVP para a banca testar.
- Avaliação da fase 1: Tech (julgado por um **agente de IA**: solução funciona, qualidade da construção, condução da IA), Negócio, Educação (Teachy) e Inovação, com 2,5 pontos cada. Abaixo de 1,0 em qualquer pilar, o grupo não vai à final.
- **Jogo limpo (cartão vermelho):**
  - **Nada de prompt injection.** README, docs, código e vídeo não podem ter instrução escondida nem frase que tente influenciar o agente avaliador. A seção do README para avaliação automática traz só comandos e saídas esperadas.
  - **Nada de demo de fachada.** Toda captura ou saída de exemplo é gerada pelo app real (`atlas demo`), e dado fictício é sempre rotulado como tal ("Turma de demonstração").
  - Todo código foi feito no evento; bibliotecas, fonte, modelo e voz de terceiros são citados em `CREDITOS.md`.
- IA liberada, mas **o grupo precisa explicar e defender cada decisão**. Por isso `docs/DECISOES.md` deve estar sempre em dia e o código precisa ser simples de explicar.

## Modo de trabalho

- **Trabalhamos por etapas, com aprovação.** Ao fim de cada etapa: atualizar este arquivo e `docs/PROGRESSO.md`, fazer push, resumir em até 5 linhas e **parar até o usuário aprovar a próxima etapa**.
- Ciclo de cada tarefa: implementar → `ruff check .` → `pytest` → corrigir → commit. Nunca deixar `main` quebrado.
- Commits pequenos, padrão Conventional Commits em pt-BR, por exemplo `feat(silabas): ...` ou `fix(camera): ...`. Nunca usar `--force` nem reescrever histórico publicado.
- Decisões ambíguas: escolher a opção mais simples e registrar em `docs/DECISOES.md` (data | decisão | motivo).
- Nunca commitar `.env`, credenciais, `.venv/`, `build/`, `dist/` nem `saida/` (exceto `docs/saida-exemplo/`).

## Comandos

```bash
py -3.11 -m venv .venv                                   # Python 3.11 (o mediapipe exige 3.9–3.12)
.venv/Scripts/python -m pip install -r requirements.txt  # núcleo + testes
.venv/Scripts/python -m pip install -r requirements-camera.txt   # opcional: webcam
.venv/Scripts/python -m pip install --no-deps -e .       # instala o comando `atlas`
atlas                       # interface gráfica (igual a `atlas gui` ou `python -m app.main`)
atlas verificar             # confere o ambiente; termina com "RESULTADO: pronto"
atlas demo todas --saida saida [--perfil tea,dislexia] [--entrada mouse|teclado|varredura|mao-simulada]
atlas perfis [--combinar tea,dislexia]   # JSON dos perfis e das regras
echo '{"acao":"estado"}' | atlas agente treino   # joga por JSON Lines
python scripts/validar_conteudo.py         # confere JSON, WAV e palavras
# gerar os WAV sem instalar nada (espeak-ng num contêiner); depois commitar assets/audio e o manifesto:
docker run --rm -v "$PWD:/w" -w /w python:3.11-slim-bookworm sh -c "apt-get update -qq && apt-get install -y -qq espeak-ng && python scripts/gerar_audio.py --provedor espeak"
.venv/Scripts/ruff check .
.venv/Scripts/python -m pytest   # roda em offscreen (tests/conftest.py)
docker compose build
docker compose run --rm verificar | demo | teste
bash scripts/gerar_saida_exemplo.sh      # regenera docs/saida-exemplo (Docker)
bash scripts/verificar_readme.sh         # roda o README num clone limpo; rodar antes de cada tag
pyinstaller empacotamento/atlas.spec --noconfirm   # dist/Atlas (onedir); a Release faz isso a cada tag v*
```

## Estrutura

```text
app/          main.py, cli.py, janela.py, nucleo/, entrada/, telas/, headless/, atividades/
conteudo/     frases.json, trilhas.json (depois: palavras, objetos, recomendacoes, manifesto_audio, simulacao_mao)
assets/       audio/, figuras/, fontes/ (Atkinson, commitada), modelos/ (hand_landmarker.task, commitado)
scripts/      baixar_modelo.py, baixar_fonte.py, gerar_audio.py, validar_conteudo.py (depois: seed_demo, ...)
tests/        pytest + pytest-qt (offscreen)
docker/       gui.sh (Etapa 7)
docs/         DECISOES.md, PROGRESSO.md (depois: ARQUITETURA.md, AVALIACAO.md, saida-exemplo/)
```

## Convenções

- Código, nomes e textos em pt-BR, sem acentos nos identificadores. Saída da CLI só em ASCII.
- As atividades só escutam o barramento `app/nucleo/eventos.py` e nunca sabem qual entrada foi usada (mouse, teclado, câmera, demo ou agente).
- Toda regra fica em funções puras testadas (`mao.py`, `erros.py`, `progresso.py`, `logica.py` de cada atividade). Os widgets só desenham e repassam eventos.
- Frases mostradas à criança ficam em `conteudo/frases.json`, nunca no código.
- Voz só no português: a letra pega, a sílaba pega e a palavra pronta (`AtividadeBase.falar`). Instruções e retornos vão para a legenda (`_anunciar`), sem voz.
- Interface: PySide6-Essentials, Widgets + QGraphicsView. Não usar QML.
- `cv2` e `mediapipe` são opcionais e só são importados dentro de funções de `entrada/camera.py` (garantido por `tests/test_dependencias.py`). Sem eles, `CameraNula` assume.
- Nenhuma chamada de rede e nenhum `cv2.imwrite` em `app/` (garantido por `tests/test_privacidade.py`).
- Design: no máximo 3 cores por tela; fundo `#F6F3EC`, texto `#2A2A2A`, primária `#2F6F6A`, destaque `#D9A441`, apoio `#8FA9C7`. Sem gradiente, sem sombra, sem vermelho para erro, raio máximo de 12 px, alvos de pelo menos 64 px. Não usar caracteres especiais como ícone (a fonte pode não ter o glifo): desenhar.

## Estado das etapas

| Etapa | Estado |
| --- | --- |
| 0. Repositório | concluída |
| 1a. Esqueleto, câmera, `atlas verificar`/`demo` mínimos, Docker | concluída |
| 1b. Empacotamento, Release e imagem no GHCR | concluída (Release v0.2.2) |
| 2. Perfis e entrada | concluída |
| 3. Núcleo das atividades, demo e agente completos | concluída |
| 4. Ímã das Sílabas | concluída (tag v0.1.0) |
| 5. Mesa de Quantidades | concluída (sem Par/ímpar) |
| 6. Pizza de Frações | concluída (tag v0.2.0) |
| 7. Painel do professor e interface remota (noVNC) | painel concluído; noVNC cortado |
| 8. Entrega | concluída: v1.0.2 (treino com o alfabeto inteiro, pausa antes das falas), repositório e imagem públicos, conferidos sem login |
