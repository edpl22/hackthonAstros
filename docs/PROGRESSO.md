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
- [x] `docker compose run --rm verificar`, `demo` e `teste` funcionando numa build limpa (imagem base com 1,2 GB)
- [x] **Aceite:** o usuário testou a câmera com `python -m app.main`: o cursor segue a mão e a pinça muda de estado

## Etapa 1b — Empacotamento, Release e GHCR
- [ ] `empacotamento/atlas.spec` (onedir, dados do mediapipe, assets, conteúdo, Info.plist com uso de câmera)
- [ ] `release.yml` (tag `v*`: Windows + macOS em zip; imagem `ghcr.io/edpl22/atlas`)
- [ ] Tag `v0.0.1` com os dois zips e a imagem
- [ ] **Aceite:** o usuário baixa o zip da Release, abre e vê o cursor seguindo a mão

## Etapa 2 — Perfis e camada de entrada
- [x] `perfis.py`: 8 perfis, combinação "a opção mais acessível vence" + testes; `atlas perfis [--combinar]`
- [x] `tema.py` aplica o perfil (escala, alto contraste, contornos, espaçamento de letras) + teste WCAG
- [x] `eventos.py` (barramento), `alvos.py`, `ponteiro.py` (arrastar e clique-clique), `teclado.py`, `varredura.py`
- [x] `mao.py` com permanência; `mao_entrada.py` (pinça e permanência no barramento); `cursor.py` com anel
- [x] `mao_simulada.py` + `conteudo/simulacao_mao.json` (pontos sintéticos pelo `mao.py` real)
- [x] `camera.py`: reduz para 480 x 360 abaixo de 15 fps; miniatura desligada no perfil TEA
- [x] `anuncio.py` (frase de cada evento) e `registro.py` (alunos: apelido, bicho, perfis)
- [x] Área do adulto (segurar 2 s): criar, editar e apagar aluno, escolher perfis; 6 avatares SVG
- [x] "Quem vai jogar?" com os alunos e o Visitante
- [x] Treino de arrastar: atividade simples sobre o barramento, completada por mouse, clique-clique, teclado, varredura e mão simulada (com erro proposital)
- [x] `atlas demo` com `--perfil` e `--entrada`
- [x] **Aceite:** 132 testes verdes; capturas da área do adulto e do treino nos perfis padrão, TEA, baixa visão e dislexia revisadas

## Etapa 3 — Núcleo das atividades, demo e agente
- [x] `AtividadeBase`: 3 momentos, faixa Agora/Depois com ícones, Ouvir, Pausa (botão e Esc), pistas graduais, ajuste de nível, registro e `estado()`
- [x] Treino migrado para a base, com nível 2 (minúsculas) e as 3 pistas (repetir, realçar, modelo)
- [x] `progresso.py` (pistas, nível, travar) e `erros.py` (classificadores das 4 atividades) + `recomendacoes.json`
- [x] `registro.py`: tentativas com todos os campos, configurações, exportar JSON, apagar tudo; na área do adulto: volume, travar nível, exportar e apagar
- [x] `audio.py`: WAV pelo manifesto (frases compostas juntam trechos), backend nulo, legenda sempre, volume
- [x] `gerar_audio.py` (google/espeak) e `validar_conteudo.py`; 47 WAV gerados com espeak-ng e commitados
- [x] `atlas demo` completo: `relatorio.md`, capturas, `tentativas.json`, `eventos.jsonl`, `audio.log`
- [x] `atlas agente <atividade>`: protocolo JSON Lines da seção 7.4
- [x] **Aceite:** 211 testes verdes, incluindo `progresso.py`, `erros.py` e o protocolo do agente; capturas revisadas nos perfis padrão e baixa visão

## Etapa 4 — Ímã das Sílabas
- [x] `palavras.json` (15 palavras, pronúncia de cada sílaba) e lógica pura com testes (distratoras, par surdo/sonoro, tônica)
- [x] 15 figuras SVG desenhadas para o projeto (`assets/figuras/palavras/`)
- [x] Cena: figura, caixas, bolhas que flutuam (velocidade x 40 px/s), sílabas alternadas na dislexia, figura no momento 1
- [x] Níveis 1 a 4 (4 = "Qual bolha é a mais forte?"), minúsculas no nível 3, erros classificados e pistas
- [x] Áudio: pegar toca a sílaba, palavra pronta toca a palavra; 168 frases geradas com espeak-ng
- [x] `atlas demo silabas` e `atlas agente silabas` (começa em BOLA; `--palavra` troca)
- [x] **Aceite:** BOLA completada por arrastar, clique-clique, teclado, varredura e mão simulada; agente completa BOLA via JSON; capturas nos perfis padrão, TEA, dislexia e baixa visão revisadas; 266 testes
- [x] Tag `v0.1.0`

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
- [x] README de entrega: resumo, "Como executar e avaliar sem tela" (caminhos A, B e C), protocolo do agente, problemas comuns, privacidade, créditos
- [x] `docs/AVALIACAO.md` (afirmação → onde está → como verificar, limitações) e `docs/ARQUITETURA.md`
- [x] `scripts/gerar_saida_exemplo.sh` e `docs/saida-exemplo/` (saídas reais do Docker, sessão do agente)
- [x] `scripts/verificar_readme.sh` passou num clone limpo (Docker e Python)
- [ ] Atualizar README e AVALIACAO quando Mesa, Pizza e painel ficarem prontos; gerar de novo a saída de exemplo
- [ ] Tag `v1.0.0`, Release e imagem no GHCR (depende da Etapa 1b)
- [ ] Usuário muda o repositório (e o pacote do GHCR) para público; testar clone e pull sem login
