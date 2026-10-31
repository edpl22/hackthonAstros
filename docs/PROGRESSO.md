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
- [x] `empacotamento/atlas.spec` (onedir, `collect_all("mediapipe")`, assets e conteúdo, Info.plist com uso de câmera) e `atlas_launcher.py` (sem console)
- [x] `release.yml` (tag `v*`): Windows e macOS com teste de fumaça (`verificar --completo` e `demo silabas`), zips na Release, imagem `ghcr.io/edpl22/atlas`
- [x] Release `v0.2.2` com `Atlas-windows.zip` e `Atlas-macos.zip`; imagem `:v0.2.2` e `:latest` no GHCR
- [ ] Usuário: tornar públicos o repositório e o pacote do GHCR antes do envio
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
- [x] Lógica pura com testes: 4 níveis (Montar, Comparar, Resolver até 10, Resolver até 20), cartões errados com motivo (operação trocada, dígitos invertidos, um a mais)
- [x] 3 conjuntos de objetos (`objetos.json`) e 3 figuras SVG (maçã, peixe, bolinha de gude); o professor escolhe o conjunto
- [x] Bandejas com número grande que muda e é falado a cada objeto ("três maçãs"); Comparar liga um a um e marca a sobra com hachura, contorno e "sobrou"; subtração com "tirar estas"
- [x] Erros classificados (`um_a_mais_ou_menos`, `operacao_trocada`, `digitos_invertidos`, `chute`, `comparacao_errada`) e pista 2 que acende os objetos enquanto a voz conta
- [x] `atlas demo quantidades` e `atlas agente quantidades`
- [ ] Modo Par/ímpar (cortado pela ordem de corte da especificação)
- [x] **Aceite:** testes da lógica e da tela; demo por mouse, teclado e mão simulada; agente monta e conclui
## Etapa 6 — Pizza de Frações
- [x] Lógica pura com testes: Montar (n fatias de d), Somar (mesmo denominador) e Desafio (fração imprópria e número misto)
- [x] Cartões: sempre um de somar os denominadores; o outro troca numerador e denominador ou conta uma fatia a mais
- [x] Fatias escolhidas com hachura diagonal e contorno grosso; alternativa em barra de chocolate (`forma_pizza` ou `forma="barra"`)
- [x] Erros `somou_denominadores`, `contou_fatias_errado`, `confundiu_numerador_denominador`; pista 2 sobrepõe as pizzas com "As fatias continuam do mesmo tamanho."
- [x] `atlas demo pizza` e `atlas agente pizza`
- [ ] A criança escolher o corte (2, 3, 4, 6 ou 8): o corte vem sorteado na rodada
- [x] **Aceite:** testes da lógica e da tela; demo por mouse, teclado e mão simulada; agente monta a fração
- [x] Tag `v0.2.0`
## Etapa 7 — Painel do professor
- [x] Regras puras com testes (`app/nucleo/painel.py`): Domina, Em progresso, Precisa de apoio nos últimos 10 itens
- [x] Turma de demonstração (6 alunos fictícios, rotulada na tela) por `scripts/seed_demo.py` ou pelo botão na área do adulto
- [x] Tela do painel: grade com ícone + texto + contagem, recomendações com o erro mais frequente
- [x] `atlas demo painel` (captura)
- [ ] `docker/gui.sh` + noVNC (cortado: primeiro item da ordem de corte)
## Etapa 8 — Entrega
- [x] README de entrega: resumo, "Como executar e avaliar sem tela" (caminhos A, B e C), protocolo do agente, problemas comuns, privacidade, créditos
- [x] `docs/AVALIACAO.md` (afirmação → onde está → como verificar, limitações) e `docs/ARQUITETURA.md`
- [x] `scripts/gerar_saida_exemplo.sh` e `docs/saida-exemplo/` (saídas reais do Docker, sessão do agente)
- [x] `scripts/verificar_readme.sh` passou num clone limpo (Docker e Python)
- [x] README, AVALIACAO e saída de exemplo atualizados com Mesa, Pizza e painel (38 capturas)
- [x] `verificar_readme.sh` passou num clone limpo; tag `v1.0.0` com `Atlas-windows.zip`, `Atlas-macos.zip` e `ghcr.io/edpl22/atlas:v1.0.0`
- [x] Repositório público: página, Release, zips e `git clone` conferidos sem login
- [x] Pacote `atlas` do GHCR público: `docker pull` e `docker run ... verificar` sem login terminam com `RESULTADO: pronto`
- [x] Treino de arrastar com o alfabeto inteiro (blocos de 4 letras, voz com o nome da letra)
- [x] `verificar_readme.sh` passou num clone limpo; tag `v1.0.1` com os zips e `ghcr.io/edpl22/atlas:v1.0.1`/`latest`, conferidos sem login
- [x] Pausa de 150 ms antes de cada fala (Bluetooth/HDMI); Piper avaliado e não adotado por licença; tag `v1.0.2` conferida sem login
- [x] Voz só no português (letra, sílaba, palavra), sem o botão Ouvir; treino só em Português; Teste da mão na tela inicial; áudio de 52 MB para 3 MB; capturas regeneradas
- [x] Tag `v1.0.3` (zips de 155 e 142 MB, imagem de 1,66 GB) conferida sem login
- [x] Botão de câmera abaixo do Voltar em toda atividade (começa ligada)
- [x] Tabuada Protetora (matemática): 1 minuto, monstrinhos, +1/-1, arminha (no início com coice, depois com gatilho no dedão); demo, agente, painel e testes
- [x] Pizza: nível Operar com 2 ou 3 pratos, soma e subtração
- [x] Jogo Dourado (matemática): quadro valor de lugar até 9.999; demo, agente, painel e testes
- [x] Tag `v1.0.4` (zips de 156 e 142 MB, imagem de 1,66 GB) conferida sem login: `verificar` dá `RESULTADO: pronto` e a imagem traz a versão 1.0.4
