# Progresso

## Etapa 0 — Repositório
- [x] Acesso ao `edpl22/hackthonAstros` conferido (privado, permissão de escrita)
- [x] Estrutura de pastas, `.gitignore`, `pyproject.toml`, `requirements*.txt`, `CLAUDE.md`, `DECISOES.md`, `PROGRESSO.md`, `README.md` (rascunho), `LICENSE`, `CREDITOS.md`
- [x] `ci.yml`: ubuntu, Python 3.11, libs do Qt, offscreen, `ruff check` e `pytest`
- [x] **Aceite:** CI verde no repositório privado

## Etapa 1a — Esqueleto, câmera, CLI mínima e Docker
- [x] Janela principal, tema, fonte e navegação Início → Matérias → Trilhas
- [x] Atividade "Teste da mão" com o cursor da mão, o estado da pinça e o indicador "Câmera ligada"
- [x] `mao.py` puro: One Euro, área ativa, pinça com histerese (permanência fica para a Etapa 2)
- [x] `baixar_modelo.py` e `baixar_fonte.py` executados; modelo e fonte commitados
- [x] `atlas verificar` completo e `atlas demo` mínimo (4 capturas da navegação + `relatorio.md`)
- [x] `Dockerfile`, `docker-compose.yml`, `.dockerignore`; job `docker` no CI
- [ ] `docker compose run --rm verificar` e `demo` funcionando numa build limpa
- [ ] **Aceite:** o usuário testa a câmera com `python -m app.main`

## Etapa 1b — Empacotamento, Release e GHCR
- [ ] `empacotamento/atlas.spec` (onedir, dados do mediapipe, assets, conteúdo, Info.plist com uso de câmera)
- [ ] `release.yml` (tag `v*`: Windows + macOS em zip; imagem `ghcr.io/edpl22/atlas`)
- [ ] Tag `v0.0.1` com os dois zips e a imagem
- [ ] **Aceite:** o usuário baixa o zip da Release, abre e vê o cursor seguindo a mão

## Etapa 2 — Perfis e camada de entrada
- [ ] `perfis.py` com combinação de perfis + testes
- [ ] `tema.py` (escala, contraste, espaçamento) + teste de contraste WCAG
- [ ] `eventos.py`, `ponteiro.py`, `teclado.py`, `varredura.py`
- [ ] `mao.py` (One Euro, histerese, permanência, área ativa) com testes
- [ ] `camera.py` com fallback, `cursor.py` com o anel de permanência
- [ ] Área do adulto (segurar 2 s): criar aluno e escolher perfis
- [ ] **Aceite:** testes verdes e capturas (adulto; perfis padrão, TEA e baixa visão)

## Etapa 3 — Núcleo das atividades
- [ ] `AtividadeBase` (3 momentos, Agora/Depois, Pausa, pistas, ajuste de nível)
- [ ] `registro.py` (SQLite) e `audio.py` (WAV + QTextToSpeech)
- [ ] `gerar_audio.py` (google/offline) e `validar_conteudo.py`
- [ ] WAV gerados
- [ ] **Aceite:** testes de `progresso.py` e `erros.py` cobrem as regras

## Etapa 4 — Ímã das Sílabas
- [ ] Lógica pura, cena, níveis 1–4, 15 SVGs, áudios e erros classificados
- [ ] **Aceite:** BOLA completada por mouse, teclado e varredura nos testes + capturas (padrão, TEA, dislexia)
- [ ] Tag `v0.1.0`

## Etapa 5 — Mesa de Quantidades
- [ ] Modos Montar, Resolver, Comparar e Par/ímpar; 3 conjuntos de objetos; erros
- [ ] **Aceite:** testes da lógica e capturas

## Etapa 6 — Pizza de Frações
- [ ] Corte, pegar/devolver, soma de mesmo denominador, desafio, barra de chocolate e erros
- [ ] **Aceite:** testes da lógica e capturas
- [ ] Tag `v0.2.0`

## Etapa 7 — Painel do professor
- [ ] `seed_demo.py`, painel e recomendações
- [ ] **Aceite:** captura do painel com a turma de demonstração

## Etapa 8 — Entrega
- [ ] README final e capturas
- [ ] Tag `v1.0.0` e Release conferida
- [ ] Usuário muda o repositório para público e testamos o link numa aba anônima
