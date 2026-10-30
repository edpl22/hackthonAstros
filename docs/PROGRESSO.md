# Progresso

## Etapa 0 — Repositório
- [x] Acesso ao `edpl22/hackthonAstros` conferido (privado, permissão de escrita)
- [x] Estrutura de pastas, `.gitignore`, `pyproject.toml`, `requirements*.txt`, `CLAUDE.md`, `DECISOES.md`, `PROGRESSO.md`, `README.md` (rascunho), `LICENSE`, `CREDITOS.md`
- [x] `ci.yml`: ubuntu, Python 3.11, libs do Qt, offscreen, `ruff check` e `pytest`
- [ ] **Aceite:** CI verde no repositório privado

## Etapa 1a — Esqueleto + câmera (local)
- [ ] Janela principal, tema, fonte e navegação Início → Matérias → Trilhas
- [ ] Atividade "Teste de câmera" com o cursor da mão e o estado da pinça
- [ ] `baixar_modelo.py` e `baixar_fonte.py` executados
- [ ] **Aceite:** o usuário testa a câmera com `python -m app.main`

## Etapa 1b — Empacotamento
- [ ] `empacotamento/atlas.spec` (onedir, dados do mediapipe, assets, conteúdo, Info.plist com uso de câmera)
- [ ] `release.yml` (tag `v*`, Windows + macOS, zips, `action-gh-release`)
- [ ] Tag `v0.0.1` com os dois zips
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
