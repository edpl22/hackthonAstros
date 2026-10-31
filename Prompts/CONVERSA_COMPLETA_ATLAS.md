# Registro integral da conversa — Projeto Atlas (1º Hackathon LEPV & DAMA)

- **Participante:** Eduardo Calderari da Silveira e Palos (GitHub: edpl22)
- **Data da sessão:** 30 de outubro de 2026 (18h28 às 23h39, horário de Brasília)
- **Ferramenta:** Claude (Anthropic), sessão com ferramentas de agente. O modelo foi alternado durante a sessão entre Opus 5.5 e Sonnet 5.5.
- **Repositório do projeto:** `edpl22/hackthonAstros` (privado durante o desenvolvimento)

## Como ler este documento

- Cada mensagem do participante e cada resposta do assistente aparece **na ordem e com o texto literal** em que foi escrita.
- As chamadas de ferramenta (leitura de arquivos, edição do documento, geração de arquivos) aparecem resumidas em itálico, entre colchetes. O conteúdo que elas produziram está nos **anexos**.
- O **Anexo A** é o material de contexto enviado pelo participante (resumo da hackathon e especificação v1 do software).
- O **Anexo B** é a especificação v2 como ficou ao final da conversa.
- Os **Anexos C, D e E** são os três prompts para o Claude Code produzidos na conversa (versão desktop inicial, versão web e versão desktop com Docker, que é a vigente).
- O PDF do conteúdo programático (13 páginas) e o Manual do Participante (11 páginas) também foram enviados; eles são documentos oficiais e estão apenas referenciados.

---

## Turno 1 — 18h28

### Participante

> @"hackathon_teachy_contexto.md" @"conteudo_fundamental_1.pdf" @"Software_Hackthon.pdf" Considere o pdf criado que especifica o software que pensamos e adapte ele e melhore as suas especificações considerando o contexto da hackathon.

*(Anexos: `hackathon_teachy_contexto.md`, `conteudo_fundamental_1.pdf` e `Software_Hackthon.pdf`. O conteúdo de dois deles está no Anexo A.)*

### Assistente

Vou ler os dois PDFs e depois reescrever a especificação do software alinhada aos desafios e às regras da hackathon.

*[Ações: leitura dos dois PDFs (especificação v1 do participante e conteúdo programático do Ensino Fundamental) e do arquivo de contexto da hackathon; criação de um documento no Claude Docs com 13 seções.]*

Estrutura do documento pronta: https://claude.ai/artifact/JyASBWqw97uYcq7KEnVRk7 — agora preenchendo o resumo e o alinhamento com a banca.

*[Ações: preenchimento de cada seção do documento (resumo e mudanças, alinhamento com a hackathon, público e design, escopo, módulo Matemática, módulo Português, perfis de acessibilidade, pistas e painel, arquitetura com diagrama, privacidade, plano de execução, validação e pitch, decisões em aberto); conferência do diagrama de arquitetura por captura de tela.]*

A especificação v2 está pronta: [Especificação do Software — Hackathon LEPV & DAMA (v2)](https://claude.ai/artifact/JyASBWqw97uYcq7KEnVRk7). Você pode editar direto no documento ou comentar.

Seu PDF pedia para consultar antes de mudar algo, então estas são as mudanças que vocês precisam aprovar:

- **Visão computacional:** troquei o OpenCV no servidor pelo MediaPipe, que roda no navegador. Assim nenhum vídeo da criança sai do aparelho e o deploy fica mais simples. Também tirei o C++, porque nesse prazo ele não traria ganho.
- **Voz:** em vez de chamar o Google Cloud TTS a cada uso, os áudios são gerados uma vez, antes, por um script Python. Isso evita atraso e não deixa chave de API exposta.
- **Câmera opcional:** toda atividade também funciona por toque, teclado ou um botão só. Isso inclui quem tem dificuldade motora, e a banca vai testar o deploy talvez sem webcam.
- **Escopo:** o mínimo para o deploy são o Ímã das Sílabas, a Mesa de Quantidades e a Pizza de Frações, mais os perfis de acessibilidade. O resto virou extensão, com um horário de corte no sábado às 10h.
- **Correções de conteúdo:**
  - Em BOLA, a sílaba soa "BÓ", não "BÔ".
  - O exemplo 15/8 é conteúdo do 5º ano, então ficou como nível desafio.
  - Imitar o som do animal virou "ouvir e escolher". O microfone não consegue julgar a imitação de forma confiável, e a versão anterior excluiria crianças com TEA que não falam.

Se quiserem, salvo uma cópia no projeto para os próximos chats da hackathon.

---

## Turno 2 — 18h39

### Participante

> ok, só mude a ideia de ser uma aplicação web/navegador para aplicação software

### Assistente

Vou ajustar o documento para um software instalável no computador. Primeiro releio o texto atual para editar só o que depende do navegador.

*[Ações: busca no documento por "navegador" e "deploy"; cerca de 35 edições pontuais no texto, nas tabelas, na estrutura de pastas e no diagrama de arquitetura.]*

Atualizei o [documento](https://claude.ai/artifact/JyASBWqw97uYcq7KEnVRk7): agora é um software instalável no computador, sem referências a navegador.

- **Interface:** Python + PySide6 (Qt), com figuras em SVG e fonte embutida no app.
- **Visão computacional:** voltei ao OpenCV da sua v1 para a câmera, com o MediaPipe para rastrear a mão, tudo local.
- **Voz:** continua com os áudios pré-gerados por script (Cloud TTS). A reserva agora é a voz offline do sistema.
- **Dados e distribuição:** SQLite local; instalador para Windows e macOS via PyInstaller, publicado em GitHub Releases.
- **Outras partes:** o diagrama de arquitetura, o plano de execução e a seção de privacidade também mudaram. No plano, "deploy no Vercel" virou "instalador testado em outra máquina".

A Fase 1 exige "deploy funcionando" e a banca vai testar, e um instalador é mais difícil de entregar do que um link: a banca pode estar em outro sistema ou bloquear executável. Adicionei nas decisões em aberto que vocês confirmem com a organização se o instalador vale como deploy. Se não valer, a saída mais simples é publicar também uma versão web de demonstração.

Também deixei PySide6 como recomendação, mas Electron ou Tauri ficam como alternativa se vocês dominarem web. Nesse caso o MediaPipe teria de rodar em JavaScript.

---

## Turno 3 — 18h45

### Participante

> @"attachment.txt" Considerando o contexto, atue como professor experiente e engenheiro da computação full-stack especialista e monte um prompt otimizado em perfomance e otimizado para o claude code que coloque o projeto em prática, tudo deve ser commitado no github

*(Anexo: `attachment.txt`, a exportação em texto da especificação v2. Seu conteúdo está no Anexo B.)*

### Assistente

Vou montar o prompt como um arquivo pronto para colar no Claude Code, com a especificação embutida, marcos com critérios de aceite e o fluxo de commits no GitHub.

*[Ação: criação do arquivo `PROMPT_CLAUDE_CODE.md` (Anexo C) e envio ao participante.]*

Montei o prompt em `PROMPT_CLAUDE_CODE.md`. Ele já traz a especificação resumida, então o Claude Code não precisa do documento à parte. Preencha as 3 variáveis no topo, abra o Claude Code numa pasta vazia no seu computador e cole o texto. Precisa ser no seu computador por causa da webcam, e o `gh auth login` tem que estar feito.

Como o prompt faz o Claude Code trabalhar:
- **Marcos com tempo e critério de aceite:** são 9, com commits pequenos, push e uma tag de versão ao fim de cada marco.
- **Instalador logo no começo:** o empacotamento com câmera vem no M1, que era o maior risco do plano. Um GitHub Actions gera os instaladores de Windows e macOS a cada tag, então vocês não precisam ter as duas máquinas.
- **Testes sem você olhar a tela:** a lógica fica em funções testáveis, e o Claude Code salva capturas das telas para conferir o visual sozinho. Ele só para uma vez, no M1, para você testar a câmera.
- **Ordem de corte definida:** se o tempo apertar, ele sabe o que cortar e o que nunca cortar.

Mudei duas coisas em relação ao documento:
- **Áudio em WAV, não MP3:** o componente de som rápido do Qt (`QSoundEffect`) não toca MP3.
- **Telas em Python puro, sem QML:** assim toda a lógica fica testável em Python, sem tela.

Se quiser, atualizo o documento com essas duas mudanças.

---

## Turno 4 — 18h50

### Participante

> quais variaveis?

### Assistente

São as três linhas no topo do arquivo, na seção "Variáveis". Já deixei valores sugeridos:

- **`NOME_PRODUTO`** = Junto. É o nome do software; troque se o time escolher outro.
- **`REPO`** = edpl22/junto. É o repositório no GitHub, no formato `usuário/nome`. Usei seu handle; troque se quiser outro nome ou uma organização.
- **`VISIBILIDADE`** = public. A hackathon pede o link do GitHub, e a banca precisa abrir sem pedir acesso. Só mude se quiser deixar privado durante o desenvolvimento e abrir antes de enviar.

Se estiver tudo certo para vocês, não precisa editar nada: é só colar o prompt como está.

Só confirme antes que o `gh auth status` mostra você logado; senão o Claude Code para no primeiro marco e pede o `gh auth login`.

---

## Turno 5 — 18h51

### Participante

> *(imagem anexada: captura do cabeçalho de um repositório no GitHub mostrando `edpl22 / 🔒 hackthonAstros`, ou seja, um repositório privado)*
>
> vou deixar privado no desenvolvimento e o nome do produto é Atlas

### Assistente

*[Ação: edição do arquivo `PROMPT_CLAUDE_CODE.md` (nome do produto, repositório existente e privado, aviso para tornar público na entrega) e novo envio do arquivo.]*

Atualizei o `PROMPT_CLAUDE_CODE.md` com o nome Atlas e o repositório privado.

- **Nome:** Atlas aparece em toda a especificação (`~/.atlas`, `Atlas-windows.zip`, `Atlas.app`, texto da permissão da câmera).
- **Repositório:** o `REPO` é `edpl22/hackthonAstros`, que já existe e é privado. O M0 não cria o repositório. Ele só conecta o remoto e, se houver commits lá, faz o pull antes do primeiro push.
- **Visibilidade:** o Claude Code não torna o repositório público sozinho. No M8 ele avisa que precisa mudar e lembra de testar o link da Release em aba anônima depois.

Você precisa deixar o repositório público antes do envio de sábado, às 12h. Se continuar privado, a banca não consegue abrir o link nem baixar o instalador. Em Settings → General → Danger Zone → Change visibility, a mudança leva menos de um minuto. Faça isso, no mais tardar, antes de gravar o vídeo, para conferir o link com calma.

Os builds de Windows e macOS no GitHub Actions funcionam em repositório privado, mas gastam minutos da cota gratuita da conta (o macOS conta 10 vezes mais). Com uma Release por marco não deve estourar.

---

## Turno 6 — 18h52

### Participante

> qual modelo é o mais indicado para codar isso?

### Assistente

**Opus 5.5** para o grosso do trabalho. Este projeto é longo e tem partes difíceis de depurar: empacotamento com MediaPipe, thread da câmera, lógica da mão, CI de duas plataformas. Um modelo mais forte erra menos nessas partes, e cada erro no sábado de manhã custa caro.

Para economizar limite de uso, dá para alternar com `/model` no Claude Code:

- **Opus 5.5:** M0 a M3 (repositório, empacotamento, entrada, núcleo das atividades), a lógica de cada atividade e qualquer bug de câmera ou PyInstaller.
- **Sonnet 5.5:** as partes repetitivas e de baixo risco: figuras SVG, `palavras.json`, testes de lógica pura, README e capturas de tela. É mais rápido e gasta menos limite.
- **Haiku 5.5:** não recomendo aqui. O projeto tem muita coordenação entre arquivos.

O Fable 5.1 é o modelo mais capaz da lista. Se a sua conta tiver acesso e o limite de uso aguentar, vale usá-lo nos marcos M1 e M2, que concentram o risco técnico. Não tenho benchmark comparando os modelos neste tipo de projeto, então essa divisão é um julgamento meu, não uma medição.

Com o prazo curto, comecem no Opus e só desçam para o Sonnet quando o limite apertar.

---

## Turno 7 — 18h53

### Participante

> alto ou médio?

### Assistente

**Alto** nos marcos difíceis e **médio** no resto.

- **Alto:** M1 a M3 (empacotamento com câmera, camada de entrada, núcleo das atividades) e qualquer bug de câmera, PyInstaller ou CI. Esses erros custam caro e se escondem.
- **Médio:** as atividades em si (M4 a M6), SVGs, conteúdo em JSON, testes e README. A especificação já está detalhada, então o modelo precisa mais executar do que raciocinar.

O esforço alto gasta mais tempo e mais limite de uso por resposta. Com o prazo curto, evite usá-lo o tempo todo.

---

## Turno 8 — 19h16

### Participante

> considerando que vai ser uma ia que vai entrar na aplicação, dá para usar essa aplicação sem ser web?

### Assistente

Dá, e o fato de ser desktop não atrapalha. Desktop e IA são independentes. O que muda são o custo e o risco, e isso depende de onde a IA roda e de quem a usa.

**Onde a IA roda**
- **Na nuvem, por API:** o app instalado faz uma chamada HTTPS. É a opção mais simples e mais capaz. Precisa de internet na máquina da banca, e a chave de API não pode ir dentro do app, porque qualquer um extrai uma chave de um executável. Para o MVP, o jeito mais seguro é o professor colar a própria chave na área do adulto. O ideal é um pequeno servidor intermediário, mas isso adiciona um serviço que pode cair na hora do teste.
- **Local, no computador:** um modelo pequeno rodando offline (por exemplo via Ollama ou llama.cpp). Preserva a privacidade e funciona sem internet, mas deixa o instalador pesado (gigabytes) e lento em notebook comum. Num hackathon de 6 horas, é arriscado.

**Quem usa a IA**
- **Lado do professor, na área do adulto:** gerar recomendações a partir dos erros, adaptar um texto ou criar palavras novas para o Ímã, sempre com revisão antes de entrar. É a opção mais defensável: encaixa nos Desafios 03 e 05 e mantém a criança longe de um chatbot.
- **Lado da criança:** só com guardrails pedagógicos fortes (pistas, sem resposta pronta). É mais difícil de fazer bem e mais fácil de a banca questionar.

**Minha recomendação:** manter o app desktop e colocar a IA só no lado do professor, por API, como recurso opcional. O app continua funcionando por inteiro sem internet e sem a IA, e a IA aparece como diferencial na demo.

Isso muda dois pontos da especificação e do prompt: "nenhuma chamada de rede em tempo de execução" e "sem IA generativa". Eu os trocaria por "rede só na área do adulto, opcional".

Qual papel a IA teria no Atlas? Com isso eu ajusto o documento e o prompt.

---

## Turno 9 — 19h16

### Participante

> eu digo da avaliadora do projeto, ela vai avaliar o tech com uma ia

### Assistente

Entendi: a avaliação técnica será feita por uma IA. Isso muda a prioridade, porque **uma IA avaliadora não instala nem roda um app desktop com câmera**. Ela lê o que está no repositório e, se der, abre um link. Pelo seu documento, a Fase 1 pede GitHub, deploy funcionando e vídeo, e é nos dois primeiros que o desktop pesa contra vocês.

O que uma IA consegue avaliar num projeto desktop:
- **Código e arquitetura:** só vale se o repositório for fácil de ler.
- **Testes e CI:** testes verdes e um selo do CI no README são evidência concreta, que ela consegue verificar sem rodar nada.
- **Capturas de tela e GIFs:** ela só "vê" o produto se isso estiver commitado e referenciado no README.
- **A transcrição do vídeo**, se a banca a fornecer.

O que eu mudaria no prompt, sem trocar para web:
1. **Um `docs/AVALIACAO.md`** que liga cada afirmação do pitch a um arquivo ou teste ("perfis combinados → `nucleo/perfis.py`, `tests/test_perfis.py`"). É o que mais ajuda um avaliador automático.
2. **Um `docs/ARQUITETURA.md`** curto, com diagrama Mermaid.
3. **Capturas e GIFs gerados pelo CI** (o script de capturas já existe) e mostrados no README, incluindo as mesmas atividades em perfis diferentes.
4. **Um modo de demonstração sem câmera**, com entrada simulada por script, para o CI gerar o vídeo ou GIF sem hardware.

Há ainda um risco que só vocês podem decidir. Se a banca exigir um link que a IA abra e use, um instalador não atende. A saída mais barata é uma página web estática de demonstração de uma única atividade (por exemplo, a Mesa de Quantidades). Seria uma vitrine, não o produto, e o Atlas continuaria desktop. Eu perguntaria à organização, hoje, como a avaliadora vai testar o deploy e se ela aceita o instalador mais o vídeo.

Quer que eu inclua os itens 1 a 4 no prompt, e a vitrine web como marco opcional?

---

## Turno 10 — 19h19

### Participante

> @"Manual_do_Participante_1.pdf" Considere essa pivotação para web mesmo, pois a avaliadora é uma IA que precisa conseguir acessar o link

*(Anexo: `Manual_do_Participante_1.pdf`, o manual oficial da hackathon, 11 páginas.)*

### Assistente

*[Ação: leitura do manual do participante.]*

Li o manual. Ele confirma que a Fase 1 pede GitHub e um deploy testado pela banca, e não diz nada contra web. Vou refazer o prompt para web, pensando em uma avaliadora que é uma IA e precisa abrir o link.

*[Ação: criação do arquivo `PROMPT_CLAUDE_CODE_WEB.md` (Anexo D) e envio ao participante.]*

Refiz o prompt para web em `PROMPT_CLAUDE_CODE_WEB.md`. Ele substitui o desktop, que continua no outro arquivo se quiserem voltar.

Para uma IA avaliadora conseguir testar, o prompt exige:
- **Sem barreiras:** a URL abre sem login, sem câmera e sem pop-up. As telas usam DOM e SVG reais, não `<canvas>`, para a IA ler o conteúdo. Toda ação de arrastar tem alternativa por clique.
- **Links diretos:** cada atividade abre por URL com parâmetros, por exemplo `/#/atividade/silabas?perfil=tea&entrada=teclado`.
- **Leitura sem JavaScript:** o `index.html` já traz texto útil sobre o projeto. Também há `avaliacao.html` e `llms.txt`, páginas estáticas gerados de um `docs/AVALIACAO.md`. Esse arquivo traz um roteiro de teste de 2 minutos e uma tabela ligando cada afirmação do pitch ao arquivo e ao teste que a comprova.
- **Modo demonstração (`?demo=1`):** cada atividade se executa sozinha, com erro, pista e registro, sem webcam.
- **Testes como prova:**
  - o teste de privacidade falha se houver requisição para outra origem;
  - o teste de acessibilidade (axe) falha em violação grave;
  - o `smoke.mjs` testa a URL de produção como um cliente anônimo.

Duas coisas dependem de vocês:
- **Vercel:** precisam de uma conta gratuita. O Claude Code para uma vez no M1 para você rodar `vercel login`. Ele também confere se a URL abre para um anônimo, porque a Vercel às vezes liga uma proteção que redireciona para login. Se isso acontecer, ele pede para você desligar em Deployment Protection.
- **Repositório público:** continua obrigatório antes do envio de sábado, às 12h. A IA avaliadora precisa abrir o GitHub.

A pivotação também devolve o que eu havia cortado antes: os áudios voltam a ser MP3 e o MediaPipe roda no navegador, com WASM e modelo no próprio site. Mantive o instalável como PWA opcional (M7), para o Atlas ainda poder ser "instalado" como software.

O documento de especificação no Docs ainda descreve a versão desktop. Quer que eu o atualize para web também?

---

## Turno 11 — 19h28

### Participante

> Ok, vi aqui que se tiver uma orientação no readme é possivel utilizar o software sem ser navegador, então oriente tudo possivel que a IA vai ter que fazer para acessar no README, o orientador também deu a dica de utilizar o docker, volte para ser uma aplicação software sem ser web

### Assistente

Vou voltar o prompt para software desktop, agora com Docker e um README pensado para uma IA conseguir executar tudo. Um app de janelas não aparece para uma IA, então ele também terá modos de linha de comando que geram evidências.

*[Ação: criação do arquivo `PROMPT_CLAUDE_CODE_DESKTOP_DOCKER.md` (Anexo E) e envio ao participante.]*

Voltei o Atlas para software desktop, com Docker e um README para a IA avaliadora seguir. O prompt está em `PROMPT_CLAUDE_CODE_DESKTOP_DOCKER.md`.

**O problema que ele resolve:** uma IA que segue o README não vê janelas, não tem webcam e talvez nem tenha tela. Por isso o Atlas ganhou comandos de terminal que rodam sem tela:
- **`atlas verificar`:** confere o ambiente e termina com `RESULTADO: pronto`.
- **`atlas demo`:** executa cada atividade sozinha, com um erro proposital. Gera capturas PNG, um `relatorio.md`, o registro das tentativas em JSON e o log de áudio.
- **`atlas agente`:** a IA joga de verdade, mandando comandos em JSON (`pegar`, `soltar`, `escolher`) e recebendo o estado da atividade.
- **`--entrada mao-simulada`:** reproduz uma mão sintética pelo código real da câmera, para mostrar esse caminho sem webcam.

**O README tem três caminhos**, com os comandos exatos e a saída esperada de cada um:
- **Docker:** `docker compose run --rm verificar`, `demo` e `teste`. Há também uma imagem pronta no GHCR, para não depender do build.
- **Python direto**, sem Docker.
- **Só ler:** `docs/AVALIACAO.md` liga cada afirmação do pitch a um arquivo e a um teste. A pasta `docs/saida-exemplo/` traz saídas reais já geradas, caso a IA não consiga executar nada.

O orientador também sugeriu abrir a interface real num navegador por noVNC (`http://localhost:6080`). Deixei isso como opcional (M7), porque tem a menor prioridade.

Quatro coisas dependem de vocês:
- **Docker instalado:** o Claude Code precisa dele no seu computador para testar o README de verdade. O M8 roda cada comando do README a partir de um clone limpo.
- **Webcam:** só vale para testar a câmera real uma vez, no M1. A IA avaliadora não terá webcam, e o prompt diz isso com franqueza no README.
- **Repositório público:** antes do envio, o repositório precisa ficar público.
- **Pacote do GHCR público:** o pacote da imagem Docker também. Ele é privado por padrão, e sem isso o `docker pull` da IA falha. O Claude Code avisa os dois no M8 e pede para testar sem estar logado.

O documento de especificação no Docs já descrevia desktop, mas ainda não tem Docker nem a parte da avaliação por IA. Quer que eu acrescente?

---

## Turno 12 — 23h39

### Participante

> A competição requer que eu coloque algum documento que mostre a conversa integralmente, consegue produzir um .md que coloque tudo que discutimos integralmente nele?

### Assistente

*[Ação: criação deste arquivo, com a transcrição acima e os anexos abaixo.]*

---

# Anexos

Os anexos reproduzem, sem alterações, os arquivos enviados pelo participante e os arquivos produzidos durante a conversa.


## Anexo A — Material enviado pelo participante

### A.1 — hackathon_teachy_contexto.md (enviado no Turno 1)

`````markdown
# 1º Hackathon LEPV & DAMA — Contexto do Projeto

> Compilado do *Manual do Participante (v1.2)* e do deck *Desafios da Educação Brasileira (Teachy <> LEPV 2026)*.
> **Banca: Teachy** (patrocinadora) + investidores convidados (+ 1 representante de empresa de IA, se a parceria fechar).

---

## 1. Regras que importam

| Item | Regra |
|---|---|
| Tema | Educação (problema livre, mas os 5 desafios da Teachy são o norte) |
| Foco da avaliação | **Qualidade do raciocínio**: clareza do problema + solidez da solução. Não precisa gerar receita. |
| Construção | Tudo (código, protótipo, material) **feito durante os 2 dias**. Projeto pré-pronto = desclassificação. |
| IA | Liberada e incentivada, mas o time precisa **explicar e defender cada decisão** com domínio próprio. |
| Grupo | 2 a 4 pessoas; presença obrigatória nos 2 dias (ausência ≤ 3 h, justificada). |
| Critérios/pesos | Ainda não divulgados — definidos pela banca. Nota final = média dos avaliadores; Fase 2 independe da Fase 1. |
| Prêmio | R$ 1.100 de crédito por integrante (reembolso, 90 dias); possível extra para Top 3. |
| PI | O projeto continua sendo do grupo. |

### Fluxo recomendado pela banca
**Problema → Ideia → Validação → Desenvolvimento → Apresentação**
(Validação pode ser informal: pesquisa rápida, conversa com usuários, análise de concorrentes.)

### Entregáveis
- **Fase 1 (sábado, até 12h):** vídeo-pitch de **até 5 min** + **link do GitHub** + **deploy funcionando** (a banca vai testar). Fora do prazo ou acima de 5 min = não avaliado.
- **Fase 2 (sábado, 16h):** Top 5 faz pitch presencial de **5 min + 5 min de perguntas**.

### Cronograma
| Quando | O quê |
|---|---|
| Sex 15h00–16h30 | Credenciamento, abertura, regras |
| Sex 16h30–20h00 | Ideação, definição do problema, desenvolvimento, jantar |
| **Sáb 08h00–12h00** | **Desenvolvimento + envio do vídeo da Fase 1** |
| Sáb 13h00–16h00 | Banca avalia vídeos → divulga Top 5 → preparação |
| Sáb 16h00–17h00 | Pitches finais |
| Sáb 17h00–18h00 | Deliberação e resultado |

---

## 2. Os 5 desafios da Teachy

### Desafio 01 — Inclusão e acessibilidade
> **Como podemos ajudar professores, escolas e família a fazerem com que todos os alunos aprendam o mesmo conteúdo, junto com a turma?**

Princípio: **Todos** (com ou sem barreira) · **Juntos** (mesma sala, ninguém à parte) · **Aprendendo** (não só estar na sala).

- Matrículas de alunos com TEA: 294 mil (2021) → **1,30 mi (2025), 4,4×**. TEA virou o maior grupo da educação especial.
- Educação especial: **2,5 mi** de alunos em 2025 (+82% vs 2021); na educação infantil, **+293,6%** — onda chegando ao fundamental.
- TEA + deficiência intelectual = **83%** dos registros → pedem adaptação de conteúdo, material e avaliação.
- **96%** já estão em classe comum, mas **50,2%** sem AEE; só **25,1%** das escolas têm sala de recursos; só **6,4%** dos professores têm formação continuada em educação especial.
- Consequência: só **25,6%** dos adultos com deficiência concluem o ensino médio (vs 57,3%); analfabetismo 19,5% vs 4,1%.
- Exemplo do deck: Davi (daltônico) — um gráfico com cor + símbolo/listra funciona para todos.
- **Pergunta-chave do deck:** *"É necessário adaptar o mesmo conteúdo N vezes dependendo do número de alunos?"* Perfis: daltonismo (cor + símbolo), baixa visão (ampliado, contraste), cegueira (descrição/áudio/braille), TDAH (um passo por vez), dislexia (áudio, texto curto, avaliação oral), TEA não verbal (pictogramas, linguagem literal, rotina).
- Base legal: CF art. 205; LBI (Lei 13.146/2015), art. 3º IV e art. 27.

### Desafio 02 — Engajamento
> **Como podemos ajudar a despertar no aluno o gosto por aprender e a vontade de se dedicar ao conteúdo, dentro e fora de sala de aula?**

- Problemas citados pelos alunos (Datafolha, out/2026): **indisciplina 40%**, bullying 33%, internet/equipamento 33%, falta de professores 27%, **aulas pouco interessantes 24%**.
- **21%** do tempo de aula vai para manter a ordem (OCDE: 15%); 44% dos professores são interrompidos com frequência (OCDE: 18%).
- **72%** dos alunos de 15 anos abaixo do básico em matemática (PISA 2025); Brasil 377 pts vs 469 OCDE.
- Jogo: **55%** de 9–17 anos jogam online todo dia, mas só **27%** usaram jogos para aprender na escola (19% no EM). Duolingo: 58,7 mi usuários diários.
- Referências: **Kahoot!** (quiz ao vivo, ranking), **Duolingo** (lições curtas, streak, ligas), **Wayground/Quizizz** (quiz no ritmo do aluno).
- **6 elementos de jogo:** desafio na medida · feedback na hora · progresso visível · sequência e recompensa · competição com colaboração · narrativa.
  - Narrativa e competição **em times** foram os que mais se destacaram (Sailer & Homner, 2020).

### Desafio 03 — Adoção saudável de IA
> **Como podemos ajudar professores, estudantes e escolas a usarem IA no dia a dia de forma segura, economizando tempo e preservando a aprendizagem?**

- **30%** dos professores usam IA semanalmente (≈ 6 semanas de trabalho economizadas/ano); **70%** dos alunos do EM usam IA em pesquisas escolares (15% anos iniciais, 39% anos finais).
- Só **22%** das escolas têm guia de uso de IA; 78% não têm.
- IA devolve tempo: **5,9 h/semana** para quem usa semanalmente (2,9 h mensal) — valor aparece quando ajuda numa tarefa da rotina.
- **Concluir tarefa com IA ≠ aprender:** −17% na prova sem IA para quem praticou com chatbot sem proteções. **Tutor com orientações pedagógicas controladas mitigou o prejuízo** (Bastani et al., PNAS 2025). Dar pistas e apoiar o raciocínio é o caminho.
- Mensagem central da Teachy: *"A IA é inevitável, mas não incontrolável. Vai transformar a escola de qualquer forma — o resultado depende de nós."*

### Desafio 04 — Aprendizagem individualizada
> **Como podemos ajudar cada aluno a aprender com conteúdos que façam sentido para sua realidade e se adaptem ao seu progresso?**

- Abaixo do nível 2 no PISA 2025: **matemática 73%, ciências 52%, leitura 51%**.
- **Diagnóstico por habilidade** decide onde cada aluno precisa de apoio.
- **Regionalização** (BNCC p. 16): linguagem/repertório cultural da turma; situações do território (comércio, água, mobilidade, biomas); contexto da escola (calendário, recursos). *"A região informa o contexto. O diagnóstico mostra o que cada aluno precisa aprender."*
- Ciclo adaptativo: **identificar a dificuldade** (conceito, procedimento ou leitura?) → **ajustar o próximo passo** (pista, pré-requisito ou desafio maior) → **verificar e reajustar**. Objetivo comum; apoio e dificuldade mudam. **Professor acompanha e pode revisar o percurso.**
- Engajamento no percurso: escolha com propósito (tema de interesse, mesma habilidade) · feedback acionável · progresso percebido.

### Desafio 05 — Insights e diagnóstico
> **Como podemos transformar o desempenho de cada aluno em recomendações que professores, escolas e famílias consigam aplicar?**

- Só **59,2%** alfabetizados ao fim do 2º ano (2024); Ceará 85,3%; meta 2030: 80%.
- Chicago: alunos "no caminho" no 9º ano concluíram o EM em **81%** vs **22%** — sinais simples antecipam o desfecho.
- **Uma nota sozinha não mostra onde o aluno travou.** 4 sinais que a escola já produz:
  1. **Respostas e erros** — 1/2 + 1/3 = 2/5 revela falta do conceito de fração.
  2. **Produções abertas** — texto/áudio mostra se entendeu a ideia mesmo errando a conta.
  3. **Frequência e participação** — faltas e tarefas não entregues aparecem semanas antes da nota baixa.
  4. **Ritmo e tentativas** — rápido e errando = chute; lento e acertando = insegurança.
  *Juntos separam sintoma de causa.*
- Famílias: **88–89%** dos pais acham que o filho está no nível; nos testes, 30–50% está. Boletim é a fonte de 64% dos pais. Pais que sabem, agem.
- Professores gastam **6,1 h/semana corrigindo** (OCDE 4,6 h); 15,4 h/semana preparando + corrigindo; **60%** citam correção como fonte de estresse.
- **Feedback acelera quando o ciclo fecha rápido:** Diagnosticar → Recomendar → Agir → Medir de novo. Até **+6 meses** de progresso (EEF Toolkit; Letrus/ES via J-PAL).

---

## 3. Notas do time (anotadas durante a apresentação)

- **Inclusão:** mesmo conteúdo, junto com a turma — envolver professor, escola **e família**.
- **Engajamento:** indisciplina; motivação; ferramentas que já usam jogo; despertar o gosto por aprender.
- **IA saudável:** IA aliada no dia a dia; devolve tempo ao professor; concluir com IA ≠ aprender; tutor com guardrails pedagógicos mitiga o prejuízo; vai transformar a escola de qualquer forma; foco em segurança.
- **Individualizada:** lacunas na aprendizagem básica; diagnóstico por habilidade; regionalização palpável para o aluno.
- **Insights:** feedback acelera quando o ciclo fecha rápido; transformar desempenho em recomendações.

---

## 4. Leitura estratégica para a banca Teachy

*(Interpretação nossa a partir do deck — não é critério oficial.)*

**Temas que se repetem nos 5 desafios** — uma solução que toque vários tende a pontuar melhor:
- **Professor no controle** e **tempo devolvido** a ele (correção, adaptação, preparação).
- **Fechar o ciclo rápido:** diagnóstico → recomendação → ação → nova medição.
- **Um conteúdo, várias formas:** gerar adaptações sem o professor refazer tudo N vezes.
- **IA com guardrails pedagógicos:** pistas e apoio ao raciocínio, não respostas prontas.
- **Diagnóstico por habilidade e pelo tipo de erro**, não só nota.
- **Família como público**: recomendações acionáveis, não boletim.

**Checklist do pitch**
- [ ] Qual desafio (01–05) atacamos? Citar a pergunta literal da Teachy.
- [ ] Problema delimitado + 1–2 dados do deck que o sustentam.
- [ ] Quem é o usuário (professor / aluno / família / gestor) e qual tarefa da rotina melhora.
- [ ] Validação mínima (concorrentes: Kahoot!, Duolingo, Wayground; conversas; pesquisa).
- [ ] Demo funcionando no **deploy** + **GitHub** público.
- [ ] Como evitamos "concluir com IA ≠ aprender" (se usarmos IA).
- [ ] Como medimos que funcionou (métrica do ciclo de feedback).
- [ ] Vídeo ≤ 5 min; pitch ao vivo de 5 min + respostas preparadas para 5 min de perguntas.

---

## 5. Fontes citadas no deck (úteis para o pitch)
Inep, Censo Escolar 2025 · IBGE, PNAD Contínua 2022 · Todos Pela Educação, Anuário 2025 · Instituto Rodrigo Mendes, Panorama 2025 · LBI (Lei 13.146/2015) · Datafolha, out/2026 (Fundação Lemann, TPE) · OCDE/Inep, TALIS 2024 · Inep/OCDE, PISA 2022 e 2025 · Cetic.br, TIC Kids Online 2025 e TIC Educação 2024/2025 · Sailer & Homner (2020), *Educational Psychology Review* · Gallup/Walton Family Foundation 2025 · Bastani et al., *PNAS* 2025 · MEC, BNCC (2018) · EEF, Teaching and Learning Toolkit / Feedback (2021) · Inep, Indicador Criança Alfabetizada 2024 · UChicago Consortium, On-Track Indicator · Gallup & Learning Heroes, *B-flation* (2023) · J-PAL, avaliação Letrus (ES).

`````

### A.2 — Software_Hackthon.pdf, especificação v1 do participante (enviada no Turno 1; texto extraído)

`````text
Obs: Se considerar que é interessante fazer alguma modificação que irá melhorar o projeto
consultar!

Público: Ensino Fundamental 1 considerando acessibilidade, Pessoas com dificuldades em
português e matemática básica, mais ou menos até o quarto ano

Plataforma: Intuitiva, simplista, não aparencia vibe codada, poucas cores, tons agradaveis a
visão, etc

Ferramentas:
Linguagem C++ e Python
Bibliotecas Python
OpenCV
Frontend
Google CloudTTS
Visão Computacional
Outras opções tomadas pelo agente considerando performance e objetivo

Software Geral:
Plataforma de ensino com abas de português e matemática, separadas em níveis leitvos, no
qual existe um ambiente interativo, dispondo de visão computacional utilizando a camera, o
microfone (talvez), texto, figuras ludicas para o publico infantil e que sejam de fácil
entendimento para neurodivergentes, no qual o usuário seleciona qual matéria ele quer
aprender.

Aba de Matemática:
Composta por duas abas, uma com números e outra com imagens
- Na com números, é possivel realizar as operações básicas e a medida que elas aparecem na
tela figuras ludicas ilustram os resultados como maçãs, peixes, e outros itens relevantes, pode-
se representar tabuadas utilizando para tal jogo dourado, por exemplo, alguma forma de
representar uma relação de maior ou menor, etc. Tudo considerando o conteúdo programático
da matemática básica
-Na com imagens é possivel selecionar diversas matérias e cada matérias tem figuras
fidedignas a representação, por exemplo se selecionar frações, aparecem pizzas ou itens que
são usualmente representados, é possivel somar os itens/ possivel interagir com as imagens,
como retirar uma fatia e somar outra pizza inteira e por exemplo obter 15/8, ou seja as figuras
são traduzidas em números palpaveis.
Eventuais ideias que achar interessante considerando o conteudo programático

Aba de português:
O Ímã das Sílabas (Português): A tela mostra a foto de uma BOLA e bolhas flutuantes com
sílabas (BO, LA, CA). A criança "agarra" uma bolha no ar, e o sistema emite o fonema
correspondente ("BÔ"), construindo a consciência fonológica por meio do movimento e do som.
Aba de imagens que quando selecionada aparece a grafia da palavras e como falar
Aba de animais imagens/nomes que a crianças tem que imitar o som do animal
Aba para ensinar de forma lúdica o alfabeto e sua caligrafia cursiva utilizando visão
computacional
Eventuais ideais que achar interessante
`````

### A.3 — Arquivos oficiais enviados e apenas referenciados

- `conteudo_fundamental_1.pdf`: Conteúdo Programático da Educação Fundamental (13 páginas), usado para alinhar as atividades aos anos letivos.
- `Manual_do_Participante_1.pdf`: Manual Oficial do Participante, versão 1.2 (11 páginas), usado para conferir regras, entregáveis e cronograma da Fase 1 e da Fase 2.

## Anexo B — Especificação v2 do software (versão final, enviada como attachment.txt no Turno 3)

Texto exportado do documento criado no Claude Docs (https://claude.ai/artifact/JyASBWqw97uYcq7KEnVRk7), na versão desktop.

`````text
Especificação do Software — Hackathon LEPV & DAMA (v2)
30 de out. de 2026 · @edpl22
Resumo e mudanças em relação à v1
Software instalável (desktop) de português e matemática básica (Educação Infantil ao 4º ano) em que a criança aprende com o corpo — mão na câmera, toque ou teclado — e em que a mesma atividade se ajusta ao perfil de cada aluno (TEA, TDAH, dislexia, baixa visão, daltonismo, dificuldade motora) sem o professor refazê-la. A ideia central da v1 foi mantida; o que muda é foco, escopo e stack, para caber em ~6 h úteis de desenvolvimento e ser defensável diante da Teachy.
Na v1
Na v2
Por quê
Acessibilidade genérica
TEA como perfil-âncora + os 6 perfis do deck
Desafio 01; TEA é o maior grupo da educação especial (1,30 mi matrículas, 4,4× desde 2021)
Visão computacional como a forma de interagir
Câmera é um dos modos; toda atividade funciona também por toque, mouse e teclado
Crianças com dificuldade motora ou sem webcam não ficam de fora; a banca vai testar o software e pode estar sem webcam
Níveis por ano letivo visíveis à criança
Trilhas por habilidade; o ano só aparece para o professor
Um aluno do 4º ano com defasagem não deve ver "1º ano" na tela
OpenCV em Python/C++ no servidor
Python + OpenCV + MediaPipe Hand Landmarker, rodando local no app
Sem streaming de vídeo: menos latência, funciona sem internet e nenhuma imagem da criança sai do computador
Google Cloud TTS em tempo real
Áudios pré-gerados com Cloud TTS (script Python) + voz offline do sistema como reserva
Sem chave de API no app, sem latência, pronúncia revisada antes
6+ atividades
MVP com 3 atividades + perfis; o resto vira extensão
O que não estiver no instalador não é avaliado
Sem papel para o professor
Painel simples: habilidade × tipo de erro
"Professor no controle" e diagnóstico pelo erro aparecem nos Desafios 04 e 05
Fração 15/8 como exemplo base
Frações de mesmo denominador até o 4º ano; 15/8 vira nível desafio
Fração imprópria e número misto são do 5º ano no conteúdo programático
Imitar o som do animal no microfone
Ouvir o som e escolher o animal; imitar é opcional
Reconhecer a imitação de uma criança não é confiável e excluiria quem tem TEA não verbal
Alinhamento com a hackathon
Atacamos o Desafio 01 — Inclusão e acessibilidade, com apoio nos Desafios 02 e 05. Pergunta da Teachy, para citar literalmente no pitch: "Como podemos ajudar professores, escolas e família a fazerem com que todos os alunos aprendam o mesmo conteúdo, junto com a turma?"
Problema em uma frase. O professor do 1º ao 4º ano recebe alunos com TEA e outras barreiras na classe comum, mas não tem formação nem tempo para adaptar cada atividade N vezes — e o aluno está na sala sem aprender.
Dados do deck que sustentam:
• 96% dos alunos da educação especial já estão em classe comum, mas 50,2% não têm AEE e só 6,4% dos professores têm formação continuada na área.
• Só 59,2% das crianças estão alfabetizadas ao fim do 2º ano (2024).
• O deck pergunta: "É necessário adaptar o mesmo conteúdo N vezes?" — nossa resposta é não: uma atividade, vários perfis.
Como cada princípio da Teachy aparece no produto:
Princípio
No produto
Todos
Toda atividade tem modo câmera, toque, teclado e áudio; nenhuma depende só de fala ou só de visão
Juntos
Mesmo objetivo e mesmo conteúdo para a turma; muda só a forma. "Modo turma": atividade projetada no quadro, crianças vêm à frente e jogam com a mão
Aprendendo
Pistas graduais em vez da resposta pronta; o erro é classificado e vira recomendação para o professor
Usuários e a tarefa que melhora:
• Aluno — faz a atividade no modo e no ritmo que funcionam para ele.
• Professor — escolhe o perfil de cada aluno uma vez; deixa de preparar versões adaptadas e passa a ver onde cada um travou.
• Família (extensão) — recebe um resumo em linguagem simples com uma ação para fazer em casa.
O que o produto não é: não substitui o AEE nem o professor, e não usa IA generativa conversando com a criança — o conteúdo é curado e revisado. Isso elimina de saída o risco "concluir com IA ≠ aprender" que a banca deve perguntar.
Público e princípios de design
Público: crianças de ~5 a 10 anos, da Educação Infantil ao 4º ano, e alunos mais velhos com defasagem em leitura ou matemática básica. O perfil TEA guia as decisões de interface, porque o que funciona para ele (previsibilidade, uma coisa por vez, nada de surpresa sensorial) também ajuda TDAH e o restante da turma.
Regras de interação
1. Roteiro sempre igual. Toda atividade tem 3 momentos: "O que vamos fazer" (pictograma + áudio) → atividade → "Terminou" + "Próximo". Uma faixa fixa mostra Agora / Depois.
2. Uma instrução por vez, linguagem literal. Frases curtas, sem metáfora nem ironia ("Pegue a bolha BO", não "Vamos caçar sílabas!").
3. Nenhuma surpresa sensorial. Som só após ação da criança, volume ajustável, sem flashes, animações de até 300 ms e desligadas pela opção Reduzir movimento.
4. Erro neutro. Sem X vermelho nem som de "errado": "Vamos tentar de novo" + uma pista.
5. Nunca só cor. Toda informação vem em cor + forma ou ícone + texto + som (o caso do Davi, do deck).
6. Alvos grandes. Botões e objetos de no mínimo 64 px, com espaço entre eles.
7. Sem relógio e sem ranking individual. Competição só em times, e só no modo turma.
8. Botão "Pausa" sempre visível. Congela a atividade, suaviza a tela e silencia tudo.
Identidade visual (para não parecer "vibe-codado")
Evitar: gradientes roxo-azul, emoji como ícone, sombras e brilhos, glassmorphism, cards genéricos de template, mais de 3 cores por tela.
Papel
Cor
Uso
Fundo
#F6F3EC (creme)
Toda a interface; reduz o branco puro
Texto
#2A2A2A
Títulos e instruções
Primária
#2F6F6A (verde-petróleo)
Botões, seleção, progresso (contraste ~5:1 com o fundo)
Destaque
#D9A441 (mostarda suave)
Só preenchimento, sempre com texto escuro por cima
Apoio
#8FA9C7 (azul acinzentado)
Elementos secundários, bolhas de sílaba
• Fonte: Atkinson Hyperlegible (desenhada para baixa visão), corpo mínimo de 24 px na tela da criança. Validar contraste de toda combinação em 4,5:1 ou mais.
• Letra bastão (maiúscula) nas trilhas iniciais, como no conteúdo da Educação Infantil; minúscula e cursiva a partir das trilhas de 1º ano.
• Ilustrações em um único estilo: SVG chapado, traço simples, cores da paleta. Manipuláveis (maçã, peixe, pizza, material dourado, moedas) desenhados pelo time. Vocabulário com pictogramas ARASAAC, padrão em comunicação alternativa para TEA (licença CC BY-NC-SA — conferir e creditar).
Escopo: MVP e extensões
O MVP são três atividades completas mais os perfis de acessibilidade; isso basta para a demo provar a tese "uma atividade, vários perfis". Três atividades polidas valem mais que seis pela metade, porque a banca vai instalar o software e testar.
Prioridade
Item
Esforço
Por que nesta prioridade
P0
Tela inicial: escolher Português ou Matemática, depois a trilha
Baixo
Navegação mínima
P0
Perfis de acessibilidade (6 perfis + ajustes finos)
Médio
É o diferencial do Desafio 01
P0
Camada única de entrada: câmera, toque/mouse e teclado
Médio
Toda atividade usa a mesma camada; sem ela nada funciona sem câmera
P0
Português — Ímã das Sílabas (12–15 palavras)
Médio
Atividade-vitrine da visão computacional
P0
Matemática — Mesa de Quantidades (somar, tirar, comparar)
Médio
Núcleo do conteúdo da Infantil ao 2º ano
P0
Matemática — Pizza de Frações (mesmo denominador)
Médio
Mostra a ponte imagem → número pedida na v1
P0
Registro de cada tentativa (SQLite local)
Baixo
Alimenta progresso e painel
P1
Painel do professor: habilidade × tipo de erro
Médio
Forte no pitch (Desafios 04/05); pode usar dados de exemplo identificados como tal
P1
Palavras e Imagens (figura, grafia, áudio, sílabas)
Baixo
Reaproveita os áudios e figuras do Ímã
P1
Material Dourado (unidade, dezena, centena)
Médio
Valor posicional, 2º ao 4º ano
P1
Traçado de letras com o dedo (bastão e cursiva)
Alto
Muito vistoso, mas calibrar leva tempo
P2
Sons dos Bichos (ouvir e escolher; imitar é opcional)
Baixo
Bom para Educação Infantil, pouco peso na tese
P2
Resumo para a família
Baixo
Bom argumento, mas só depois do painel
P2
Modo turma com times
Médio
Engajamento (Desafio 02)
P2
Dinheiro, horas, tabuada
Médio
Mais conteúdo, mesma mecânica
Regra de corte: se no sábado às 10h00 um P0 não estiver funcionando no instalador, ele sai e nenhum P1 entra.
Módulo Matemática
As duas abas da v1 ("números" e "imagens") viram dois sentidos de uma mesma atividade, com figura e número sempre lado a lado e sincronizados:
• Montar — a criança mexe nas figuras e vê o número mudar (concreto → símbolo).
• Resolver — a criança vê a conta e a representa com figuras antes de responder (símbolo → concreto).
É a sequência concreto → pictórico → abstrato, um bom argumento pedagógico para defender diante da banca.
A. Mesa de Quantidades (P0)
Conteúdo: quantificação de 0 a 20, adição e subtração (juntar e tirar), maior/menor/igual, par e ímpar, dúzia e meia dúzia.
• Duas bandejas e um cesto. A criança pega objetos do cesto (pinça na câmera, arrastar no toque, setas + Enter no teclado) e o número de cada bandeja atualiza na hora, com áudio ("três maçãs").
• Resolver: aparece 3 + 4 = ?; a criança monta com objetos e escolhe a resposta entre 3 cartões.
• Comparar: em vez do "jacaré", os objetos das duas bandejas são ligados um a um; a bandeja com sobra é a maior. É mais literal e funciona melhor para TEA.
• Par/ímpar: os objetos se organizam em duplas; sobrou um, é ímpar.
• Contexto local: o professor escolhe o conjunto de objetos (frutas, peixes, bolinhas de gude, pipas). No MVP são 3 conjuntos.
Erros registrados: contou um a mais ou a menos; trocou a operação (somou quando era para tirar); inverteu dígitos (12 ↔ 21); resposta errada em menos de 1,5 s (provável chute).
B. Pizza de Frações (P0)
Conteúdo: partes de um inteiro e soma de mesmo denominador (4º ano). Nível desafio: fração imprópria, como o 15/8 da v1 (pizza de 8 fatias sem uma = 7/8; mais uma inteira = 15/8 = 1 e 7/8).
• A criança escolhe em quantas fatias cortar (2, 3, 4, 6 ou 8), pega e devolve fatias; a fração aparece embaixo (fatias pegas / fatias da pizza).
• Somar: duas pizzas com o mesmo corte; as fatias se juntam e a criança monta o resultado.
• Fatias selecionadas têm hachura e contorno, não só cor (daltonismo). Representação alternativa: barra de chocolate retangular.
Erro-chave: somar os denominadores (1/4 + 2/4 = 3/8), o mesmo tipo de erro que o deck usa como exemplo. A pista mostra as duas pizzas sobrepostas: "as fatias continuam do mesmo tamanho".
C. Material Dourado (P1)
Conteúdo: unidade, dezena, centena e milhar; composição e decomposição (234 = 200 + 30 + 4); antecessor e sucessor.
• Cubinho, barra, placa e cubo. Ao juntar 10 cubinhos, eles se agrupam numa barra ("trocar").
• Multiplicação como disposição retangular (linhas × colunas de objetos) é a extensão natural para a tabuada.
Erro registrado: troca de ordem (dezena lida como unidade).
Próximas atividades com a mesma mecânica
Atividade
Conteúdo programático
Anos
Blocos lógicos: separar por cor, forma, tamanho e espessura
Classificação por quatro atributos; formas geométricas
Infantil, 1º
Feira: pagar e dar troco com cédulas e moedas
Sistema monetário
3º, 4º
Relógio: mover os ponteiros com a mão
Hora exata, meia hora, minutos
2º ao 4º
Gráfico da turma: cada criança põe seu ícone e o pictograma se forma
Tabelas e gráficos simples
Infantil ao 4º
Módulo Português
A. Ímã das Sílabas (P0)
Conteúdo: consciência fonológica e divisão silábica; sílaba tônica nos níveis de 3º e 4º ano.
• Na tela: a figura da palavra (BOLA), caixas vazias, uma por sílaba, e até 4 bolhas com sílabas (as certas + 1 ou 2 distratoras).
• A criança agarra uma bolha (pinça, ou deixar o dedo parado 1 s sobre ela), ouve a sílaba e solta na caixa. Ao completar, ouve a palavra inteira com as sílabas realçadas em sequência.
• Bolhas lentas (até 40 px/s); nos perfis TEA e TDAH ficam paradas.
Cuidado com o áudio. A sílaba precisa soar como dentro da palavra: em BOLA o som é "BÓ" (aberto), não "BÔ" como estava na v1. Um TTS lendo "BO" isolado ainda pode soletrar "bê-ó". Por isso o áudio é gerado por palavra e por posição (bola_1.mp3, bola_2.mp3), com grafia fonética ou SSML, e ouvido por alguém do time antes de entrar.
Nível
Palavras
O que muda
1
BOLA, CASA, PATO, GATO, SAPO, VACA
2 sílabas simples
2
MACACO, SAPATO, BONECA, JANELA, TOMATE
3 sílabas
3
BRAÇO, PRATO, PÁSSARO, LIVRO
Sílabas complexas
4
As mesmas palavras
"Qual bolha é a mais forte?" (sílaba tônica)
Erros registrados: ordem trocada (LA-BO); troca de par surdo/sonoro (BO ↔ PO, TA ↔ DA, FA ↔ VA), sinal comum em dislexia; sílaba de outra palavra. Distratoras ficam mais parecidas à medida que a criança acerta.
B. Palavras e Imagens (P1)
• Grade de figuras por tema (casa, escola, comida, bichos). Ao tocar: a palavra em bastão, minúscula e cursiva, o áudio da palavra e o áudio sílaba por sílaba, com botão "ouvir devagar".
• Reaproveita figuras e áudios do Ímã; custo baixo.
C. Traçado de Letras e Números (P1)
Conteúdo: alfabeto maiúsculo (Infantil), cursiva maiúscula e minúscula (1º ano) e "grafia dos números com movimentação correta" (Infantil e 1º ano).
• A letra-guia aparece grande, com seta no ponto de início e pontos numerados. A criança segue com a ponta do indicador no ar (câmera) ou com o dedo na tela.
• Como verificar: o traço-modelo é uma lista ordenada de pontos; cada ponto "acende" quando o dedo passa a menos de R px dele, na ordem certa. Isso mede direção e cobertura sem precisar reconhecer escrita livre — mais robusto e exatamente o que o conteúdo pede (o movimento correto).
• Filtro de tremor no dedo e R maior para o perfil de dificuldade motora.
• Custo real: desenhar os traços-modelo. Começar com números 0–9 e maiúsculas de traço simples; cursiva só se sobrar tempo.
Erros registrados: começou no ponto errado, direção invertida, pulou um trecho.
D. Sons dos Bichos (P2)
• Ouvir e escolher: toca o som, a criança escolhe entre 3 figuras; depois vê o nome dividido em sílabas.
• Imitar (opcional): o microfone só detecta que houve voz e celebra, sem julgar se a imitação ficou "certa". Nunca é obrigatório.
• Onomatopeias ("au au", "miau") geradas pelo próprio TTS evitam problema de licença de sons reais.
Próximas atividades com a mesma mecânica
Atividade
Conteúdo programático
Anos
Meu Nome: montar o nome completo com bolhas de letras
Grafia do nome completo
Infantil, 1º
Ordem alfabética: pôr bolhas de letras ou palavras em ordem
Ordem alfabética (1ª, 2ª e 3ª letras)
1º ao 3º
Começo, meio e fim: ordenar 3 cenas de uma história
Sequência lógica, elementos da narrativa
Infantil ao 3º
Plural e ortografia: escolher a bolha certa (R/RR, S/SS, M antes de P/B)
Regras ortográficas
2º, 3º
Perfis de acessibilidade e modos de interação
O conteúdo e o objetivo de cada atividade são fixos; o perfil só muda a forma. O professor define o perfil de cada aluno uma vez (perfis podem ser combinados) e pode ajustar detalhes: velocidade, número de itens na tela, volume, tamanho, áudio automático e modo de entrada.
Perfil
O que muda na mesma atividade
TEA
Bolhas e objetos parados; pictograma em toda instrução; no máximo 3 itens na tela; celebração sem som (opcional); aviso antes de trocar de atividade
TDAH
Um passo por vez (só a etapa atual visível); menos distratores; rodadas de 5 itens com pausa
Dislexia
Áudio automático de toda instrução; fonte maior com mais espaço entre letras; sílabas alternadas com cor e sublinhado; resposta por escolha, nunca por digitação
Baixa visão
Zoom de 150–200%; alto contraste; contornos grossos; foco bem visível; menos itens
Daltonismo
Toda distinção por cor também tem hachura, símbolo ou texto (isso já vale para todos; o perfil só troca para uma paleta segura)
Dificuldade motora
"Deixar parado" em vez de pinça; tolerância maior de alvo; varredura com um botão
Cegueira
Suporte parcial e declarado: teclado + leitor de tela + áudio descritivo no Ímã e na Mesa. Material tátil e braille ficam fora do escopo
Uma camada única de entrada
Toda forma de entrada produz os mesmos 4 eventos — apontar(x, y), pegar, soltar, escolher — e as atividades só escutam esses eventos. Assim, cada atividade é escrita uma vez e funciona em todos os modos.
Modo
Apontar
Pegar e soltar
Câmera
Ponta do indicador
Pinça polegar-indicador, ou deixar a mão parada 1 s
Toque ou mouse
Dedo ou cursor
Arrastar e soltar, ou tocar no item e depois no destino
Teclado
Setas e Tab movem o foco
Enter ou Espaço pega e solta
Varredura (1 botão)
O foco passa sozinho pelas opções a cada 1,5 s
Qualquer tecla ou acionador adaptado
Se a câmera for negada ou não existir, o app entra direto no modo toque, sem mensagem de erro. Na demo, a banca consegue usar tudo mesmo sem webcam.
Pistas, erros, progresso e painel do professor
O erro é tratado como sinal, não como falha: cada tentativa errada recebe um tipo, gera uma pista e alimenta o painel. Toda a lógica é por regras simples e explicáveis — nada de IA decidindo pela criança.
Pistas graduais
A resposta nunca aparece no primeiro erro.
1. Repetir a instrução com áudio e pictograma.
2. Realçar o que importa: na Mesa, os objetos acendem um a um enquanto o áudio conta junto; no Ímã, a figura destaca a parte da palavra que falta.
3. Mostrar o modelo fazendo, e a criança repete.
Depois da 3ª pista, a atividade segue normalmente e registra "precisou de modelo".
Ajuste de nível
• 4 acertos seguidos na 1ª tentativa → oferece o próximo nível ("Quer um desafio?").
• 2 itens seguidos que precisaram de modelo → volta ao nível anterior ou ao pré-requisito.
• O professor pode travar um nível.
Isso corresponde ao ciclo do Desafio 04: identificar a dificuldade → ajustar o próximo passo → verificar e reajustar.
O que é registrado em cada tentativa
{"aluno": "a03", "atividade": "pizza", "habilidade": "fracao_soma_mesmo_denominador",
 "item": "1/4+2/4", "resposta": "3/8", "correta": false,
 "tipo_erro": "somou_denominadores", "pistas": 1, "tempo_ms": 6400,
 "modo": "camera", "ts": "2026-10-31T09:12:00"}
Painel do professor (P1)
• Grade aluno × habilidade com três estados — Domina, Em progresso, Precisa de apoio — sempre com ícone e texto, não só cor.
• Para cada "Precisa de apoio": o tipo de erro mais frequente e uma recomendação de uma frase, tirada de uma tabela tipo de erro → ação. Exemplo: "Ana somou os denominadores em 3 de 4 tentativas. Sugestão: pizzas sobrepostas, mostrando que o tamanho da fatia não muda."
• Na demo, uma "turma de demonstração" com dados de exemplo, rotulada como tal na tela.
Resumo para a família (P2)
Três linhas em linguagem simples: o que a criança praticou, onde está indo bem e uma coisa para fazer em casa ("Contem juntos os talheres ao pôr a mesa"). Responde ao dado do deck de que 88–89% dos pais acham que o filho está no nível esperado.
Como medir que funcionou
• Por habilidade: taxa de acerto na 1ª tentativa e número médio de pistas por item, ao longo das sessões. Sucesso = menos pistas para o mesmo nível.
• Para o professor: número de versões adaptadas que ele deixou de preparar (uma por perfil, por atividade).
Arquitetura técnica e stack
Tudo roda no computador da criança: aplicativo instalado, visão computacional local e áudios pré-gerados. Não há servidor para cair na hora em que a banca testar, e nenhuma imagem sai do dispositivo.
As quatro entradas viram os mesmos eventos; o perfil muda só a forma da atividade; o áudio é gerado uma vez, fora do aplicativo.
Camada
Escolha
Por quê
Interface
Python 3.11 + PySide6 (Qt Quick/QML); figuras em SVG; perfis como arquivo de tema (cores, fonte, tamanhos, opções)
Toolkit nativo e maduro, sem Electron; SVG escala sem perder nitidez no zoom de baixa visão; fonte Atkinson embutida no app
Visão computacional
OpenCV (captura e pré-processamento) + MediaPipe Hand Landmarker (21 pontos da mão), em thread própria
Volta ao OpenCV da v1 para a câmera; o MediaPipe entrega o rastreamento da mão pronto, sem treinar nada nem enviar vídeo a servidor
Voz
Google Cloud TTS pt-BR, rodado por script Python, gerando MP3 + manifesto JSON; reserva: voz offline do sistema (pyttsx3)
Pronúncia revisada, zero latência, nenhuma chave de API dentro do app instalado, funciona sem internet
Reprodução de áudio
Qt Multimedia (QSoundEffect)
Toca os MP3 pré-gerados com baixa latência
Microfone (P2)
sounddevice, só o nível de volume
Detecta que houve voz sem gravar nada
Dados
SQLite local, com exportação em JSON
Sem backend no MVP
Distribuição
PyInstaller → instalador para Windows (.exe) e macOS (.app); GitHub Releases + repositório público
A banca instala e testa; câmera usa a permissão do próprio sistema
Python
Scripts de conteúdo: gerar áudio, validar listas de palavras e sílabas, gerar traçados-modelo
Onde Python dá ganho real no prazo
C++
Fora do MVP
Qt e MediaPipe já são C++ por baixo; C++ próprio não traria ganho em ~6 h e complicaria o empacotamento. Se for importante usar, um módulo pequeno via pybind11 (comparação de traçado) é o único encaixe razoável
Pipeline da mão
1. Captura com OpenCV em 640 × 480, imagem espelhada, numa thread própria que envia os pontos da mão à interface; uma mão por vez.
2. Cursor = ponta do indicador (ponto 8), suavizado com filtro One Euro para tirar o tremor.
3. Pinça = distância polegar–indicador (pontos 4 e 8) dividida pelo tamanho da palma (pontos 0 e 9), para funcionar perto ou longe da câmera. Com histerese: pega abaixo de ~0,25 e solta acima de ~0,40 (calibrar no evento).
4. Permanecer = cursor parado sobre o alvo por 1 s; um círculo enche para mostrar o tempo.
5. Área ativa = 80% central do quadro, para a criança não precisar esticar o braço até a borda.
6. Se ficar abaixo de 15 quadros por segundo, a resolução cai. A miniatura da câmera é opcional e vem pequena por padrão (a própria imagem pode distrair no perfil TEA).
Estrutura do repositório
app/
  main.py
  entrada/      camera.py  ponteiro.py  teclado.py  varredura.py  -> barramento de eventos
  atividades/   silabas/  quantidades/  pizza/        (QML + Python)
  perfis/       perfis.py (tema + opções por perfil)
  registro/     tentativas.py (SQLite)
  conteudo/     palavras.json  manifesto-audio.json
  assets/       audio/ (bola_1.mp3, bola_2.mp3, bola.mp3 ...)  fontes/  figuras/
scripts/
  gerar_audio.py  validar_conteudo.py  empacotar.spec (PyInstaller)
Privacidade e segurança
A câmera de uma criança é o ponto mais sensível do projeto, e a banca citou segurança. A resposta é de arquitetura: o vídeo nunca sai do computador.
• Vídeo processado localmente. Nenhum quadro é salvo ou enviado. A tela de permissão diz isso ao adulto em uma frase simples.
• Câmera só dentro da atividade, com indicador visível; desliga ao sair.
• Microfone mede apenas volume; nada é gravado.
• Dados mínimos: apelido ou código do aluno, nunca nome completo nem foto; tudo fica no próprio dispositivo, com botão "Apagar dados".
• Sem login, sem anúncios, sem analytics de terceiros no MVP.
• LGPD, art. 14: dados de crianças exigem tratamento no melhor interesse delas e consentimento específico de um dos pais ou responsável. Numa versão com servidor, esse consentimento entra no cadastro feito pela escola.
• Sem IA generativa falando com a criança. O conteúdo é curado; nada é gerado na hora sem revisão.
Plano de execução para 2 pessoas
O primeiro entregável é um instalador vazio que já abre a câmera: o maior risco técnico é descobrir no sábado às 11h que o app empacotado não abre a câmera em outro computador.
Divisão: Pessoa A cuida de visão computacional, entrada e Português. Pessoa B cuida de Matemática, interface, perfis, conteúdo e empacotamento.
Quando
Pessoa A
Pessoa B
Sex, até 20h00
Python + PySide6 + OpenCV + MediaPipe; cursor e pinça numa tela de teste
Repositório, instalador vazio (PyInstaller) gerado e testado com câmera em outra máquina; cores e fonte; lista de palavras; gerar_audio.py rodando
Sex à noite (se o time seguir)
Barramento de eventos + toque e teclado; Ímã nível 1
Mesa de Quantidades; perfis
Sáb 08h00–10h00
Ímã completo, pistas, registro de tentativas
Pizza de Frações; perfis aplicados nas 3 atividades
Sáb 10h00 — corte
P0 que não funciona no instalador sai
Idem
Sáb 10h00–10h45
P1 se sobrar tempo (painel com dados de exemplo)
Teste cruzado: outro notebook (Windows e macOS), câmera negada, só teclado
Sáb 10h45–11h30
Gravar o vídeo (roteiro pronto na noite anterior)
README do GitHub com link do instalador (Releases), como testar e créditos (ARASAAC, fontes)
Sáb 11h30–11h50
Enviar vídeo + GitHub + instalador
Conferir duração (≤ 5 min) e instalador baixado e aberto em máquina limpa
Sáb 13h00–16h00 (se Top 5)
Ensaiar pitch ao vivo
Ensaiar respostas às perguntas
Regra da competição: nada de código antes da abertura. Este documento é planejamento; código, áudios e figuras são produzidos durante o evento.
Validação e pitch
Validação mínima durante o evento
[ ] Conversa de 5 min com 1 ou 2 pessoas (mentor, alguém da Teachy, professor ou pedagogo por WhatsApp). Perguntas: "Quantas versões de uma atividade você prepara para alunos com laudo?" e "O que faz um aluno com TEA abandonar uma atividade?" Guardar uma frase para citar.
[ ] Comparar com concorrentes: Kahoot! e Wayground (quiz igual para todos; ranking individual pode excluir), Duolingo (individual, sem professor), GraphoGame (consciência fonológica, sem perfis nem movimento — conferir). Nosso diferencial: a mesma atividade em vários modos e perfis, aprendizagem pelo movimento e erro classificado para o professor.
[ ] Alguém de fora do time usa o app só com teclado e com a câmera negada.
Roteiro do vídeo (até 5 min)
Tempo
Conteúdo
0:00–0:40
Problema e dados: 96% em classe comum, 6,4% dos professores com formação; "é preciso adaptar N vezes?"
0:40–1:10
A ideia: uma atividade, vários perfis; quem usa (aluno e professor)
1:10–3:30
Demo: Ímã com a mão → troca para perfil TEA na mesma tela → a mesma atividade pelo teclado → Pizza com erro de denominador e pista → painel
3:30–4:15
Como funciona e por que é seguro: vídeo local, sem IA generativa com a criança, LGPD
4:15–4:50
Validação, métrica e próximos passos
Terminar com 10 s de folga: acima de 5 min o vídeo não é avaliado.
Perguntas prováveis da banca
Pergunta
Resposta curta
Como sabem que funciona para autistas?
Usamos práticas consolidadas (pictogramas, previsibilidade, sem surpresa sensorial). A prova real é um piloto com o AEE, medindo a queda no número de pistas
Câmera não exclui quem não pode usar?
É um modo entre quatro; a mesma atividade funciona por toque, teclado ou um botão
E as imagens das crianças?
São processadas no próprio computador; nada é salvo ou enviado
Onde entra a IA?
Visão computacional para interagir e voz sintética. Sem chatbot para a criança, de propósito: o deck mostra −17% na prova sem proteções pedagógicas
Quanto custa escalar?
Software instalável com áudio pré-gerado, sem servidor: custo por aluno próximo de zero; roda em notebook comum
E o professor com 30 alunos?
Define o perfil uma vez por aluno; no modo turma, projeta a atividade e as crianças jogam no quadro
Como isso conversa com a Teachy?
A camada de perfis e de entrada pode ser aplicada a qualquer atividade, inclusive conteúdos que já existem
Decisões em aberto para o time
[ ] Nome do produto. Sugestões: Junto (eco do princípio "Juntos" da Teachy), Mão na Letra, Bolha.
[ ] C++ fica fora? Recomendação: sim; a justificativa está na seção de arquitetura.
[ ] PySide6 ou Electron. Recomendação: PySide6, que mantém Python e OpenCV da v1. Se um de vocês já domina web, Electron ou Tauri funcionam, mas o MediaPipe teria de rodar em JavaScript. Não é hora de aprender framework novo.
[ ] Pictogramas ARASAAC ou tudo desenhado pelo time. A licença não comercial serve para a hackathon; se virar produto, rever.
[ ] Voz do Cloud TTS. Ouvir 2 ou 3 vozes pt-BR e escolher uma. Precisa de conta Google Cloud com faturamento ativo; o volume (algumas centenas de áudios curtos) é pequeno.
[ ] Painel do professor entra no instalador? Decidir no corte das 10h00 de sábado.
[ ] Como a banca recebe o software. A Fase 1 pede "deploy funcionando" e link do GitHub. Proposta: instalador para Windows e macOS em GitHub Releases, com o vídeo-pitch mostrando tudo funcionando. Confirmar com a organização se o instalador vale como deploy e quais sistemas a banca usa.
[ ] Quem grava o vídeo e quem fala no pitch ao vivo.
`````

## Anexo C — PROMPT_CLAUDE_CODE.md (versão desktop inicial, já com o nome Atlas e o repositório privado após o Turno 5)

`````markdown
# Prompt para o Claude Code — Hackathon LEPV & DAMA

> Cole tudo abaixo da linha no Claude Code, aberto numa pasta vazia no seu computador (é preciso ter webcam para testar).
> Antes, preencha as 3 variáveis e confira que `gh auth status` mostra você logado.

---

## Variáveis

- `NOME_PRODUTO` = **Atlas**
- `REPO` = **edpl22/hackthonAstros** (já existe no GitHub, **privado**, e pode estar vazio)
- `VISIBILIDADE` = **private** durante o desenvolvimento; só vira público na entrega (M8)

## 1. Papel e missão

Você é engenheiro de software sênior (Python, Qt, visão computacional) e trabalha junto com uma professora experiente de alfabetização e educação inclusiva. Sua missão é construir, testar, empacotar e publicar no GitHub o software desktop **NOME_PRODUTO**, para uma hackathon de educação julgada pela Teachy.

O produto é um software instalável de português e matemática básica, da Educação Infantil ao 4º ano. A criança aprende com o corpo (mão na câmera, toque, mouse ou teclado), e **a mesma atividade se ajusta ao perfil de cada aluno** (TEA, TDAH, dislexia, baixa visão, daltonismo, dificuldade motora), sem o professor refazê-la. É uma resposta ao Desafio 01 da Teachy: *"Como podemos ajudar professores, escolas e família a fazerem com que todos os alunos aprendam o mesmo conteúdo, junto com a turma?"*

O prazo é curto. Os critérios de avaliação são, nesta ordem:
1. Funciona na máquina da banca, com ou sem webcam.
2. Qualidade pedagógica e de acessibilidade.
3. Código limpo que o time consegue explicar.

## 2. Como você deve trabalhar

1. **Autonomia.** Não faça perguntas, exceto se estiver bloqueado de verdade (credencial, permissão do GitHub). Quando algo for ambíguo, escolha a opção mais simples que cumpra a especificação e registre em `docs/DECISOES.md` (data, decisão, motivo, uma linha cada).
2. **Ciclo curto.** Para cada tarefa: implementar → rodar `ruff check` e `pytest` → corrigir → commit. Faça push ao fim de cada marco. Nunca deixe `main` quebrado.
3. **Commits.** Pequenos e atômicos, no padrão Conventional Commits em pt-BR, por exemplo `feat(silabas): bolhas arrastáveis com encaixe nas caixas` ou `fix(camera): histerese da pinça`. Nunca use `--force` nem reescreva o histórico publicado.
4. **Memória do projeto.** No Marco 0, crie um `CLAUDE.md` na raiz com: comandos (instalar, rodar, testar, empacotar), estrutura de pastas, convenções e o estado dos marcos. Atualize ao fim de cada marco. Releia-o se perder contexto.
5. **Plano visível.** Mantenha `docs/PROGRESSO.md` com a checklist dos marcos (seção 9), marcando o que está feito.
6. **Você não vê a tela, então verifique por imagem.** Há um script `scripts/capturas.py` que abre cada tela em modo offscreen, chama `widget.grab()` e salva PNG em `docs/capturas/`. Abra esses PNG com sua ferramenta de leitura de imagem e confira o layout contra o design system (seção 5) antes de fechar cada marco de interface.
7. **Subagentes.** Use subagentes para tarefas independentes e longas que não mexem nos mesmos arquivos:
   - desenhar as figuras SVG;
   - escrever `palavras.json` e os conjuntos de objetos;
   - escrever testes de lógica pura.

   A integração fica com você.
8. **Time-box.** Se um problema travar por mais de ~20 min de tentativas, simplifique (por exemplo, `mediapipe.solutions.hands` em vez da Tasks API), registre em `DECISOES.md` e siga em frente.
9. **Segredos.** Nunca commite credenciais, `.env`, `*.json` de conta de serviço, `.venv`, `build/` ou `dist/`. Configure o `.gitignore` antes do primeiro commit.

## 3. Stack travada

Não troque nada desta tabela sem registrar o motivo em `DECISOES.md`.

| Camada | Escolha | Observação |
| --- | --- | --- |
| Linguagem | Python 3.11 | Os wheels do mediapipe exigem 3.9–3.12; use 3.11 |
| Interface | PySide6, com **Widgets + QGraphicsView** para as atividades | Não use QML: assim toda a lógica fica em Python, testável com pytest-qt em offscreen |
| Figuras | SVG via `QGraphicsSvgItem` / `QSvgRenderer` | Escala sem perda no zoom de baixa visão |
| Câmera | OpenCV (`cv2.VideoCapture`) numa `QThread` | No Windows, `cv2.CAP_DSHOW`; no macOS, o padrão (AVFoundation) |
| Mão | MediaPipe Hand Landmarker (Tasks API, `running_mode=VIDEO`, `num_hands=1`) | Modelo `hand_landmarker.task` em `assets/modelos/`, baixado por `scripts/baixar_modelo.py` e commitado (Apache 2.0). Se a Tasks API falhar, use `mediapipe.solutions.hands` |
| Áudio | `QSoundEffect` com **WAV** (PCM 16 bits, 22 050 Hz, mono) | QSoundEffect não toca MP3. Gere WAV; arquivos curtos ficam pequenos |
| Voz de reserva | `QTextToSpeech` (módulo `PySide6.QtTextToSpeech`), voz pt-BR do sistema | Usada quando faltar o WAV de um texto |
| Geração de áudio | `scripts/gerar_audio.py` com dois provedores: `google` (Cloud TTS, voz pt-BR Neural2/WaveNet, saída LINEAR16) e `offline` (pyttsx3) | O provedor `google` só roda com `GOOGLE_APPLICATION_CREDENTIALS` definido. Se não houver, use `offline` e registre |
| Dados | SQLite (`sqlite3` da stdlib) em `~/.atlas/atlas.db` (use o caminho de dados do usuário de cada SO), com exportação JSON | Sem servidor |
| Qualidade | `ruff`, `pytest`, `pytest-qt` com `QT_QPA_PLATFORM=offscreen` | |
| Empacotamento | PyInstaller em modo **onedir** | onefile descompacta mediapipe a cada abertura e fica lento |
| CI/CD | GitHub Actions: testes no push; builds Windows e macOS anexados a uma Release quando houver tag `v*` | A banca baixa da Release |
| Rede | **Nenhuma chamada de rede em tempo de execução** | Só os scripts de preparo acessam a rede |

Para dependências, use `pyproject.toml` com versões mínimas fixadas e um `requirements.txt` gerado para o CI e o PyInstaller.

## 4. Arquitetura

```text
atlas/
  app/
    main.py                 # entrada; cria QApplication, carrega tema e perfis
    nucleo/
      eventos.py            # barramento: apontar(x,y), pegar, soltar, escolher (Qt Signals)
      perfis.py             # dataclass Perfil, perfis prontos, combinação de perfis
      tema.py               # paleta, fonte, escala; aplica o perfil (QSS + parâmetros)
      audio.py              # ServicoAudio: toca WAV pelo manifesto; reserva QTextToSpeech
      registro.py           # SQLite: alunos, tentativas; exporta JSON
      progresso.py          # pistas graduais, ajuste de nível, regras puras
      erros.py              # classificadores de erro + tabela erro -> recomendação
    entrada/
      ponteiro.py           # mouse e toque -> eventos
      teclado.py            # foco, setas, Tab, Enter, Espaço -> eventos
      varredura.py          # foco automático a cada 1,5 s; qualquer tecla seleciona
      camera.py             # QThread: OpenCV + MediaPipe -> pontos normalizados
      mao.py                # lógica PURA: filtro One Euro, pinça com histerese, permanência, área ativa
      cursor.py             # item visual do cursor com anel de permanência
    telas/
      inicio.py             # "Quem vai jogar?" (apelidos + avatar pictograma)
      materias.py           # Português | Matemática
      trilhas.py            # trilhas por habilidade (sem mostrar o ano à criança)
      adulto.py             # área do adulto (segurar botão 2 s): alunos, perfis, painel
      painel.py             # painel do professor (P1)
    atividades/
      base.py               # AtividadeBase: roteiro 3 momentos, Agora/Depois, Pausa, pistas, registro
      silabas/              # Ímã das Sílabas
      quantidades/          # Mesa de Quantidades
      pizza/                # Pizza de Frações
  conteudo/
    palavras.json
    objetos.json            # conjuntos de objetos da Mesa (frutas, peixes, bolinhas)
    recomendacoes.json      # tipo_erro -> frase para o professor
    manifesto_audio.json    # texto/chave -> arquivo WAV
  assets/
    audio/  figuras/  fontes/  modelos/
  scripts/
    baixar_modelo.py  baixar_fonte.py  gerar_audio.py  validar_conteudo.py  capturas.py  seed_demo.py
  tests/
  empacotamento/
    atlas.spec  Info.plist.extra
  .github/workflows/ci.yml  .github/workflows/release.yml
  docs/  DECISOES.md  PROGRESSO.md  capturas/
  README.md  CLAUDE.md  LICENSE (MIT para o código)  CREDITOS.md
```

Regras de arquitetura:
- As **atividades só escutam o barramento de eventos**. Nenhuma atividade sabe se a entrada veio da câmera, do mouse ou do teclado.
- Toda lógica com regra fica em **funções puras com testes**: classificar erros, pistas, nível, pinça, filtro, encaixe, comparação. Isso inclui `mao.py`, `erros.py`, `progresso.py` e a lógica de cada atividade (`logica.py` dentro da pasta da atividade).
- Os widgets só desenham e repassam eventos.

## 5. Design system (regras rígidas)

**Paleta.** Use no máximo 3 cores por tela, mais fundo e texto.

| Papel | Cor |
| --- | --- |
| Fundo | `#F6F3EC` |
| Texto | `#2A2A2A` |
| Primária | `#2F6F6A` |
| Destaque (só preenchimento, com texto escuro) | `#D9A441` |
| Apoio | `#8FA9C7` |

O perfil de alto contraste usa fundo `#FFFFFF`, texto `#000000` e primária `#00524C`. Escreva um teste que calcula o contraste WCAG de todas as combinações texto/fundo usadas e falha se alguma ficar abaixo de 4,5:1.

**Proibido:** gradientes, sombras, brilhos, transparência decorativa, emoji como ícone, cantos muito arredondados (raio máximo de 12 px), cards genéricos de template, vermelho para erro.

**Fonte.** Atkinson Hyperlegible (licença OFL), baixada por `scripts/baixar_fonte.py` para `assets/fontes/` e registrada com `QFontDatabase`. Se não houver rede, use a fonte sans do sistema e registre em `DECISOES.md`. O corpo mínimo na tela da criança é 24 px; instruções têm 32 px.

**Letras.** Use letra bastão (maiúscula) nas trilhas iniciais e minúscula a partir das trilhas de 1º ano.

**Ilustrações.** SVG chapado, traço de 3 px `#2A2A2A`, preenchimentos da paleta, viewBox 0 0 256 256, sem texto dentro. Desenhe à mão em SVG uma figura por palavra (15), os objetos da Mesa (maçã, peixe, bolinha de gude) e o avatar de cada aluno (6 bichos simples).

**Alvos.** Mínimo de 64 × 64 px, com 16 px de espaço entre eles. O foco do teclado é um contorno de 4 px na cor primária, sempre visível.

**Movimento.** Animações de até 300 ms, sem flash. Com "Reduzir movimento" ligado, todas as animações ficam com duração 0.

## 6. Regras pedagógicas e de acessibilidade (a professora exige)

Toda atividade herda de `AtividadeBase` e cumpre:

1. **Roteiro fixo em 3 momentos.** "O que vamos fazer" (figura + frase + áudio) → atividade → "Terminou!" + botão "Próximo". Uma faixa fixa no topo mostra **Agora / Depois** com ícones.
2. **Uma instrução por vez, literal.** "Pegue a bolha BO. Coloque na primeira caixa." Nada de metáfora ou ironia. Todas as frases ficam em `conteudo/`, nunca espalhadas no código.
3. **Som só depois de uma ação da criança.** Há volume ajustável e nenhum som de "errado".
4. **Erro neutro.** Diga "Vamos tentar de novo" e dê uma pista. Nunca X vermelho.
5. **Nunca só cor.** Seleção, acerto e categoria usam cor + forma ou hachura + texto.
6. **Botão Pausa sempre visível.** Congela a atividade, cobre a tela com o fundo a 85% de opacidade, silencia o áudio e mostra o botão "Continuar".
7. **Sem relógio e sem ranking.**
8. **Pistas graduais** (`progresso.py`): 1ª = repetir a instrução com áudio; 2ª = realçar o que importa; 3ª = mostrar o modelo fazendo. Depois da 3ª, a atividade segue e a tentativa é registrada com `precisou_modelo=True`.
9. **Ajuste de nível.** 4 acertos seguidos na 1ª tentativa → oferece o próximo nível ("Quer um desafio?", com Sim e Não). 2 itens seguidos com modelo → volta um nível. O professor pode travar o nível.
10. **Acessibilidade Qt.** Todo widget interativo tem `setAccessibleName` em pt-BR. A ordem do Tab segue a ordem visual.

### Perfis

`Perfil` é uma dataclass com: `velocidade` (0–1), `max_itens`, `escala` (1.0–2.0), `alto_contraste`, `paleta_segura`, `audio_auto`, `reduzir_movimento`, `som_celebracao`, `modo_entrada_preferido`, `tolerancia_alvo_px`, `tempo_permanencia_ms`, `espacamento_letras`, `um_passo_por_vez`, `rodada_itens`.

Perfis podem ser combinados pela regra **"a opção mais acessível vence"**: menor velocidade, menor `max_itens`, maior escala, `True` vence em flags de acessibilidade.

| Perfil | Valores |
| --- | --- |
| padrão | velocidade 0,5; max_itens 4; escala 1,0 |
| tea | velocidade 0; max_itens 3; som_celebracao False; aviso antes de trocar de atividade |
| tdah | um_passo_por_vez True; max_itens 3; rodada_itens 5 |
| dislexia | audio_auto True; espacamento_letras 0,12 em; escala 1,2; sílabas alternadas com cor **e** sublinhado; resposta sempre por escolha |
| baixa_visao | escala 1,75; alto_contraste True; contornos de 5 px; max_itens 3 |
| daltonismo | paleta_segura True (hachuras e símbolos em toda distinção) |
| motor | modo_entrada_preferido "permanencia"; tolerancia_alvo_px 60; tempo_permanencia_ms 1200; varredura disponível |
| cegueira (parcial) | audio_auto True; descrição em áudio de cada item focado; uso por teclado |

## 7. Camada de entrada

Todas as entradas emitem os mesmos sinais em `nucleo/eventos.py`: `apontar(x, y)` (coordenadas da cena), `pegar()`, `soltar()` e `escolher(id_item)`.

- **Mouse/toque:** arrastar e soltar, ou tocar no item e depois no destino. Habilite `Qt.WA_AcceptTouchEvents`.
- **Teclado:** setas e Tab movem o foco entre itens; Enter ou Espaço pega e solta; Esc abre a Pausa.
- **Varredura:** o foco avança sozinho a cada 1,5 s; qualquer tecla seleciona.
- **Câmera:**
  - `camera.py` roda numa `QThread`, captura em 640 × 480 e espelha a imagem.
  - Mantém só o quadro mais recente (descarta atrasados), com alvo de 30 fps.
  - Os timestamps do MediaPipe são em ms e sempre crescentes.
  - Emite `pontos(lista_normalizada, presente: bool)` e `fps(float)`.
  - Se a média ficar abaixo de 15 fps, reduz para 480 × 360.
  - Só converte o quadro para `QImage` se a miniatura estiver ligada; ela vem desligada no perfil TEA e pequena (160 × 120) nos demais.
- **`mao.py` (puro, 100% testado):**
  - Cursor = ponto 8, passado por um filtro One Euro com `min_cutoff=1.0` e `beta=0.02`, configuráveis.
  - Área ativa = 80% central do quadro, mapeada para a cena inteira.
  - Pinça = distância(4, 8) / distância(0, 9), com histerese: pega abaixo de 0,25 e solta acima de 0,40.
  - Permanência = cursor dentro de `tolerancia_alvo_px` por `tempo_permanencia_ms` → `pegar`; a mesma regra no destino → `soltar`.
- **Fallback.** Se a câmera não abrir em 3 s, ou não houver câmera, entre no modo mouse/toque **sem mensagem de erro** e mostre só um ícone discreto "câmera desligada".
- **Privacidade.** A câmera só liga dentro de uma atividade, mostra um indicador visível (ponto + texto "Câmera ligada") e desliga ao sair. Nenhum quadro é salvo. Um teste garante que o código não chama `cv2.imwrite` nem abre conexões de rede.
- **Overlay de depuração.** F12 mostra fps, a razão da pinça e o estado da mão.

## 8. Atividades do MVP

### 8.1 Ímã das Sílabas (Português)

- **Tela:** figura da palavra no centro alto; caixas vazias (uma por sílaba) abaixo; até `max_itens` bolhas com sílabas (as corretas + distratoras). As bolhas flutuam devagar (`velocidade × 40 px/s`) e ficam paradas quando a velocidade é 0.
- **Interação:**
  - Ao pegar uma bolha, toca a sílaba.
  - Ao soltá-la sobre uma caixa (a área da caixa expandida pela tolerância), ela encaixa.
  - Se a sílaba estiver certa, fica na caixa.
  - Se estiver errada, volta suavemente e a atividade dá uma pista.
  - Ao completar a palavra, toca a palavra inteira e realça as sílabas em sequência.
- **Distratoras.** Use o par surdo/sonoro (B↔P, T↔D, F↔V, C↔G) quando o nível for mais alto; caso contrário, uma sílaba de outra palavra.
- **Nível 4 (sílaba tônica):** "Qual bolha é a mais forte?" — a criança escolhe a sílaba tônica da palavra.
- **Erros classificados:** `ordem_trocada`, `par_surdo_sonoro`, `silaba_de_outra_palavra`.

Formato de `conteudo/palavras.json` (15 palavras):

```json
{"id": "bola", "texto": "BOLA", "silabas": ["BO", "LA"],
 "fala": {"palavra": "bola", "silabas": ["bó", "la"]},
 "tonica": 0, "nivel": 1, "figura": "figuras/bola.svg"}
```

Palavras por nível:
- **Nível 1:** BOLA, CASA, PATO, GATO, SAPO, VACA
- **Nível 2:** MACACO, SAPATO, BONECA, JANELA, TOMATE
- **Nível 3:** BRAÇO, PRATO, PÁSSARO, LIVRO
- **Nível 4:** as mesmas palavras, perguntando a tônica

Pronúncia: o campo `fala.silabas` é a grafia que o TTS deve ler para soar como dentro da palavra. Por exemplo, em BOLA a sílaba BO é "bó" (aberto), nunca "bô". `validar_conteudo.py` confere:
- que as sílabas concatenadas formam o texto;
- que existem a figura e os áudios;
- que `tonica` é um índice válido.

### 8.2 Mesa de Quantidades (Matemática)

- **Tela:** duas bandejas e um cesto de objetos (conjunto escolhido pelo professor). O número de cada bandeja fica grande ao lado dela e atualiza a cada objeto, com áudio ("três maçãs").
- **Modos** (o objetivo é o mesmo; muda a pergunta):
  - **Montar:** livre, mostrando o número.
  - **Resolver:** `3 + 4 = ?` ou `7 − 2 = ?` (até 20). A criança monta com objetos e escolhe a resposta entre 3 cartões.
  - **Comparar:** os objetos das duas bandejas são ligados um a um com linhas. A sobra fica destacada (hachura + contorno + texto "sobrou"), e a criança escolhe "maior", "menor" ou "igual".
  - **Par/ímpar:** os objetos se organizam em duplas; sobrou um, é ímpar.
- **Erros classificados:** `um_a_mais_ou_menos` (|resposta − certo| = 1), `operacao_trocada`, `digitos_invertidos` (12 ↔ 21), `chute` (errou em menos de 1 500 ms).
- **Pista 2:** os objetos acendem um a um enquanto o áudio conta.

### 8.3 Pizza de Frações (Matemática)

- **Tela:** a criança escolhe o corte (2, 3, 4, 6 ou 8 fatias), pega e devolve fatias. A fração aparece embaixo, grande (fatias pegas / total).
- **Resolver:** `1/4 + 2/4 = ?`. Duas pizzas com o mesmo corte; a criança junta as fatias numa terceira pizza e escolhe a resposta entre 3 cartões. Um dos cartões errados é sempre o de somar denominadores.
- **Desafio:** fração imprópria, por exemplo 7/8 + 8/8 = 15/8, mostrado também como 1 e 7/8.
- **Visual:** fatias selecionadas têm hachura diagonal + contorno grosso, não só cor. A alternativa é uma barra de chocolate retangular, ligada nas opções da atividade.
- **Erros classificados:** `somou_denominadores`, `contou_fatias_errado`, `confundiu_numerador_denominador`.
- **Pista 2:** as duas pizzas aparecem sobrepostas, com o texto "as fatias continuam do mesmo tamanho".

### 8.4 Registro de cada tentativa

Tabela `tentativas` com os campos: `aluno`, `atividade`, `habilidade`, `item`, `resposta`, `correta`, `tipo_erro`, `pistas`, `precisou_modelo`, `tempo_ms`, `modo_entrada`, `perfis`, `ts`. Os alunos têm apenas apelido e avatar (nunca nome completo nem foto). A área do adulto tem os botões "Exportar JSON" e "Apagar todos os dados".

### 8.5 Painel do professor (P1)

- Grade aluno × habilidade com 3 estados, sempre com ícone e texto: **Domina** (≥ 80% de acerto na 1ª tentativa nas últimas 10), **Em progresso** e **Precisa de apoio** (< 50% ou ≥ 2 modelos nas últimas 10).
- Para cada "Precisa de apoio": o tipo de erro mais frequente e a frase de `recomendacoes.json`. Exemplo: *"Ana somou os denominadores em 3 de 4 tentativas. Sugestão: pizzas sobrepostas, mostrando que o tamanho da fatia não muda."*
- `scripts/seed_demo.py` cria a turma "Turma de demonstração" (6 alunos fictícios), rotulada assim na tela.

## 9. Marcos (execute em ordem; push e atualização do PROGRESSO.md ao fim de cada um)

**M0 — Repositório (≤ 20 min)**

- [ ] Rodar `gh auth status`. Se não estiver logado, pare e peça para eu rodar `gh auth login`. Rode também `gh repo view REPO` para confirmar que o repositório existe e que você tem acesso de escrita.
- [ ] Criar a estrutura da seção 4, `.gitignore`, `pyproject.toml`, `requirements.txt`, `CLAUDE.md`, `docs/DECISOES.md`, `docs/PROGRESSO.md`, `README.md` (rascunho), `LICENSE`, `CREDITOS.md`.
- [ ] Criar `ci.yml`:
  - `ubuntu-latest`, Python 3.11;
  - `apt-get install -y libegl1 libgl1 libxkbcommon0 libdbus-1-3`;
  - `QT_QPA_PLATFORM=offscreen`;
  - rodar `ruff check` e `pytest`.
- [ ] O repositório `REPO` **já existe e é privado**; não o crie nem mude a visibilidade. Rode `git init -b main`, `git remote add origin https://github.com/REPO.git` e `git fetch origin`. Se o remoto tiver commits (por exemplo, só um README), faça `git pull origin main --rebase` antes do primeiro push; se estiver vazio, vá direto ao primeiro commit e `git push -u origin main`.
- **Aceite:** código no repositório privado com o CI verde.

**M1 — Esqueleto que já empacota com câmera (risco nº 1; ≤ 60 min)**

- [ ] Janela principal, tema, fonte e navegação Início → Matérias → Trilhas, com uma atividade "Teste de câmera" que mostra o cursor da mão e o estado da pinça.
- [ ] Rodar `baixar_modelo.py` e `baixar_fonte.py`.
- [ ] Criar `empacotamento/atlas.spec`:
  - onedir;
  - `collect_data_files('mediapipe')`;
  - `assets/` e `conteudo/` como datas;
  - no macOS, `info_plist` com `NSCameraUsageDescription` = "O Atlas usa a câmera só para ver a mão da criança. Nenhuma imagem é salva ou enviada." e `NSMicrophoneUsageDescription`.
- [ ] Criar `release.yml`, disparado por tag `v*`:
  - matriz `windows-latest` e `macos-latest`;
  - instalar dependências e rodar PyInstaller;
  - zipar como `Atlas-windows.zip` e `Atlas-macos.zip`;
  - publicar com `softprops/action-gh-release`.
- [ ] Criar a tag `v0.0.1` e conferir que a Release saiu com os dois zips.
- **Aceite:** consigo baixar o zip da Release, abrir o app e ver o cursor seguindo minha mão. Rode o app localmente com `python -m app.main` e me peça para testar a câmera **uma vez** aqui. Este é o único ponto em que você espera por mim.

**M2 — Perfis e camada de entrada (≤ 60 min)**

- [ ] `perfis.py` com combinação de perfis + testes.
- [ ] `tema.py` aplicando escala, contraste e espaçamento.
- [ ] `eventos.py`, `ponteiro.py`, `teclado.py`, `varredura.py`, `mao.py` (com testes cobrindo One Euro, histerese, permanência e área ativa), `camera.py` com fallback e `cursor.py` com o anel de permanência.
- [ ] Área do adulto (segurar 2 s): criar aluno (apelido + avatar) e escolher perfis.
- **Aceite:** testes verdes; capturas de tela da área do adulto e de um mesmo protótipo com os perfis padrão, TEA e baixa visão salvas em `docs/capturas/` e revisadas por você.

**M3 — Núcleo das atividades (≤ 45 min)**

- [ ] `AtividadeBase` com roteiro de 3 momentos, faixa Agora/Depois, Pausa, pistas graduais e ajuste de nível.
- [ ] `registro.py` (SQLite) e `audio.py` (manifesto WAV + reserva QTextToSpeech).
- [ ] `gerar_audio.py` (provedores `google` e `offline`) e `validar_conteudo.py`.
- [ ] Gerar os WAV com o provedor disponível.
- **Aceite:** testes de `progresso.py` e `erros.py` cobrem todas as regras das seções 6 e 8.

**M4 — Ímã das Sílabas (≤ 75 min)**

- [ ] Lógica pura, cena, níveis 1–4, 15 figuras SVG, áudios e erros classificados.
- **Aceite:** completar BOLA com mouse, teclado e varredura nos testes pytest-qt (simulando eventos); capturas nos perfis padrão, TEA e dislexia.
- [ ] Tag `v0.1.0`.

**M5 — Mesa de Quantidades (≤ 60 min)**

- [ ] Os 4 modos, 3 conjuntos de objetos e os erros classificados.
- **Aceite:** testes da lógica e capturas.

**M6 — Pizza de Frações (≤ 60 min)**

- [ ] Corte, pegar/devolver fatias, soma de mesmo denominador, nível desafio, alternativa em barra e os erros.
- **Aceite:** testes da lógica e capturas.
- [ ] Tag `v0.2.0`.

**M7 — Painel do professor (P1, ≤ 45 min)**

- [ ] `seed_demo.py`, painel e recomendações.
- **Aceite:** captura do painel com a turma de demonstração.

**M8 — Entrega (≤ 30 min)**

- [ ] README final em pt-BR:
  - o problema em 3 linhas;
  - link de download da Release;
  - como abrir no macOS sem assinatura (botão direito → Abrir, ou `xattr -dr com.apple.quarantine Atlas.app`);
  - como testar sem webcam;
  - atalhos de teclado;
  - arquitetura em 1 diagrama Mermaid;
  - privacidade;
  - créditos (Atkinson Hyperlegible/OFL, MediaPipe/Apache 2.0, voz usada).
- [ ] Capturas no README.
- [ ] Tag `v1.0.0` e conferir a Release.
- [ ] **Não torne o repositório público por conta própria.** Ao final, avise que a visibilidade precisa mudar para pública antes do envio (Settings → General → Danger Zone → Change visibility), porque a banca precisa abrir o link e baixar a Release sem pedir acesso. Teste o link da Release numa aba anônima depois que eu mudar.
- **Aceite:** CI verde, Release v1.0.0 com os zips Windows e macOS, `PROGRESSO.md` completo.

Se o tempo apertar, a ordem de corte é: M7 → nível desafio da Pizza → modo Par/ímpar → nível 4 do Ímã. **Nunca corte** a camada de entrada sem câmera, os perfis, a Pausa ou o empacotamento.

## 10. Requisitos de desempenho

- A interface roda a 60 fps durante as atividades. Nada pesado na thread principal: câmera e MediaPipe ficam só na `QThread`.
- A latência do movimento da mão até o cursor fica abaixo de 100 ms em um notebook comum.
- O app abre em menos de 5 s (onedir). O mediapipe é importado só quando uma atividade com câmera começa (import preguiçoso).
- O áudio de uma sílaba começa a tocar em menos de 100 ms (WAV pré-carregado com `QSoundEffect` para os itens da tela atual).
- Figuras SVG são renderizadas uma vez por tamanho e mantidas em cache (`QPixmapCache`).

## 11. Fora do escopo

Login, servidor, nuvem, IA generativa conversando com a criança, analytics, anúncios, gravação de imagem ou de áudio e qualquer chamada de rede em tempo de execução.

## 12. Ao terminar cada marco

Responda em até 5 linhas: o que ficou pronto, o link do commit ou da Release, o que eu preciso testar manualmente (se houver) e a decisão mais importante registrada.

`````

## Anexo D — PROMPT_CLAUDE_CODE_WEB.md (versão web, Turno 10)

`````markdown
# Prompt para o Claude Code — Atlas (versão web)

> Cole tudo abaixo da linha no Claude Code, aberto numa pasta vazia no seu computador.
> Antes: `gh auth status` deve mostrar você logado, e você precisa de uma conta gratuita na Vercel (o Claude Code vai pedir um `vercel login` uma única vez, no M1).

---

## Variáveis

- `NOME_PRODUTO` = **Atlas**
- `REPO` = **edpl22/hackthonAstros** (já existe no GitHub, **privado**, pode estar vazio)
- `HOSPEDAGEM` = **Vercel** (plano gratuito)

## 1. Papel e missão

Você é engenheiro full-stack sênior (TypeScript, front-end, acessibilidade, visão computacional no navegador) e trabalha junto com uma professora experiente de alfabetização e educação inclusiva. Sua missão é construir, testar, publicar e documentar a aplicação web **NOME_PRODUTO** para uma hackathon de educação julgada pela Teachy, com tudo versionado no GitHub.

O produto ensina português e matemática básica, da Educação Infantil ao 4º ano. A criança aprende com o corpo (mão na câmera, toque, mouse ou teclado), e **a mesma atividade se ajusta ao perfil de cada aluno** (TEA, TDAH, dislexia, baixa visão, daltonismo, dificuldade motora), sem o professor refazê-la. É uma resposta ao Desafio 01 da Teachy: *"Como podemos ajudar professores, escolas e família a fazerem com que todos os alunos aprendam o mesmo conteúdo, junto com a turma?"*

### Quem vai avaliar a parte técnica

**Uma IA** vai receber o link do deploy e o link do GitHub e testar o projeto. Ela provavelmente: abre a URL num navegador automatizado ou só busca o HTML, lê a árvore de acessibilidade, clica em elementos, lê o README e o código. Ela **não tem webcam, não faz login e não instala nada**. Todo o projeto precisa ser avaliável nessas condições. Isto é um requisito de primeira classe (seção 7).

Prioridades, nesta ordem:
1. A URL pública abre e funciona **sem câmera, sem login e sem configuração**.
2. Qualidade pedagógica e de acessibilidade, **demonstrável** por testes e por um roteiro de avaliação.
3. Código limpo, testado e documentado, que o time consegue explicar.

## 2. Como você deve trabalhar

1. **Autonomia.** Não faça perguntas, exceto se estiver bloqueado de verdade (login na Vercel, permissão no GitHub, teste de câmera previsto no M1). Quando algo for ambíguo, escolha a opção mais simples que cumpra a especificação e registre em `docs/DECISOES.md` (data, decisão, motivo, uma linha cada).
2. **Ciclo curto.** Para cada tarefa: implementar → `npm run lint`, `npm run typecheck`, `npm test` → corrigir → commit. Faça push ao fim de cada marco. Nunca deixe `main` quebrado.
3. **Commits.** Pequenos e atômicos, em Conventional Commits em pt-BR, por exemplo `feat(silabas): bolhas com encaixe nas caixas` ou `fix(mao): histerese da pinça`. Nunca use `--force` nem reescreva o histórico publicado.
4. **Memória do projeto.** No M0, crie um `CLAUDE.md` na raiz com: comandos (instalar, rodar, testar, build, deploy), estrutura de pastas, convenções, a URL do deploy e o estado dos marcos. Atualize ao fim de cada marco. Releia-o se perder contexto.
5. **Plano visível.** Mantenha `docs/PROGRESSO.md` com a checklist da seção 9.
6. **Verifique o visual por imagem.** Você não vê a tela. O script `npm run capturas` usa o Playwright para abrir cada tela em perfis diferentes e salvar PNG em `docs/capturas/`. Abra os PNG com sua ferramenta de leitura de imagem e confira o layout contra o design system (seção 5) antes de fechar cada marco de interface.
7. **Subagentes.** Use subagentes para tarefas independentes que não mexem nos mesmos arquivos: desenhar as figuras SVG, escrever `palavras.json` e os conjuntos de objetos, escrever testes de lógica pura. A integração fica com você.
8. **Time-box.** Se um problema travar por mais de ~20 min, simplifique, registre em `DECISOES.md` e siga em frente.
9. **Segredos.** Nunca commite credenciais, `.env`, JSON de conta de serviço, `node_modules/`, `dist/` nem `.vercel/`. Configure o `.gitignore` antes do primeiro commit.
10. **Origem do conteúdo.** Todo o código, áudio e figura é produzido neste evento. Cite no `CREDITOS.md` cada biblioteca, fonte e modelo de terceiros com a licença.

## 3. Stack travada

Não troque nada desta tabela sem registrar o motivo em `DECISOES.md`.

| Camada | Escolha | Observação |
| --- | --- | --- |
| Build | Vite + TypeScript (`strict`) | |
| UI | React 18, **DOM e SVG reais** (nunca `<canvas>` para elementos interativos) | A IA avaliadora lê a árvore do DOM e de acessibilidade; um canvas seria opaco para ela |
| Rotas | `react-router` com `HashRouter` | Evita configuração de rewrite; links profundos funcionam em qualquer hospedagem |
| Estilo | CSS puro com variáveis CSS (perfis trocam variáveis) | Sem Tailwind e sem biblioteca de componentes: evita o visual genérico |
| Estado | React Context + `useReducer`; um pequeno armazenamento em `localStorage` versionado (`atlas:v1`) | Sem backend |
| Fonte | `@fontsource/atkinson-hyperlegible` (self-hosted, WOFF2, só latin) | Nenhuma fonte de CDN |
| Figuras | SVG em `src/figuras/*.svg` importados como componentes (`vite-plugin-svgr`) | Permite hachura e estilo por perfil |
| Entrada | **Pointer Events** + teclado + varredura + câmera, todos via barramento de eventos próprio | Não use a API HTML5 de drag and drop: ela não funciona bem com toque nem com entrada simulada |
| Mão | `@mediapipe/tasks-vision` (HandLandmarker, `runningMode: "VIDEO"`, `numHands: 1`, delegate GPU com reserva em CPU) | Import dinâmico (só ao ligar a câmera). WASM e modelo **self-hosted** em `public/mediapipe/` |
| Voz | MP3 pré-gerados com `scripts/gerar_audio.py` (Google Cloud TTS pt-BR, voz Neural2/WaveNet) + **`speechSynthesis` (pt-BR) como reserva** | Sem credencial, só use a reserva e registre. Nunca coloque chave de API no front-end |
| Testes | Vitest (lógica pura e componentes), Playwright (e2e e capturas), `@axe-core/playwright` (acessibilidade) | |
| Qualidade | ESLint + Prettier + `tsc --noEmit` | |
| CI | GitHub Actions: lint, typecheck, vitest, build, Playwright | Ver M0 |
| Hospedagem | Vercel, publicação pela CLI (`vercel deploy --prod`) | Se a Vercel falhar, Netlify ou Cloudflare Pages; registre em `DECISOES.md` |
| PWA (P2) | `vite-plugin-pwa` | Só depois do M6; instalável e offline |
| Rede em tempo de execução | **Só a mesma origem** (HTML, JS, CSS, fontes, áudio, modelo) | Nenhum CDN, nenhuma fonte externa, nenhum analytics, nenhuma API |

Use Node 20 ou superior e `npm`. Fixe as versões no `package-lock.json`.

## 4. Arquitetura

```text
atlas/
  index.html                  # com conteúdo estático útil dentro de #root e <noscript> (seção 7)
  public/
    mediapipe/                # wasm/ e hand_landmarker.task (self-hosted)
    audio/                    # MP3 pré-gerados
    avaliacao.html            # GERADO de docs/AVALIACAO.md no prebuild
    llms.txt                  # resumo curto para agentes, com links
    robots.txt
  src/
    main.tsx  App.tsx  rotas.tsx
    nucleo/
      eventos.ts              # barramento: apontar(x,y), pegar, soltar, escolher(id)
      perfis.ts               # tipo Perfil, perfis prontos, combinação
      tema.ts                 # aplica o perfil como variáveis CSS em <html>
      audio.ts                # ServicoAudio: MP3 pelo manifesto; reserva speechSynthesis
      registro.ts             # tentativas e alunos em localStorage; exporta JSON
      progresso.ts            # pistas graduais, ajuste de nível (puro)
      erros.ts                # classificadores de erro + tabela erro -> recomendação (puro)
      anuncio.ts              # região aria-live que narra os eventos da atividade
      demo.ts                 # executor de roteiros de demonstração (seção 7)
    entrada/
      ponteiro.ts             # Pointer Events -> eventos
      teclado.ts              # foco, setas, Tab, Enter, Espaço, Esc
      varredura.ts            # foco automático a cada 1,5 s
      camera.ts               # getUserMedia + HandLandmarker, import dinâmico
      mao.ts                  # lógica PURA: One Euro, pinça com histerese, permanência, área ativa
      Cursor.tsx              # cursor visual com anel de permanência
    telas/
      Inicio.tsx  Materias.tsx  Trilhas.tsx  Adulto.tsx  Painel.tsx  Avaliacao.tsx
    atividades/
      AtividadeBase.tsx       # roteiro de 3 momentos, Agora/Depois, Pausa, pistas, registro, demo
      silabas/  quantidades/  pizza/      # cada uma: Tela.tsx, logica.ts, logica.test.ts, demo.ts
    figuras/                  # SVGs
    conteudo/
      palavras.json  objetos.json  recomendacoes.json  frases.json  manifesto_audio.json
    estilos/                  # tokens.css, base.css, perfis.css
  scripts/
    copiar_mediapipe.mjs      # copia o wasm do node_modules para public/mediapipe (postinstall)
    baixar_modelo.mjs         # baixa hand_landmarker.task para public/mediapipe (commitar o arquivo)
    gerar_audio.py            # Cloud TTS -> public/audio + manifesto
    validar_conteudo.mjs      # confere sílabas, figuras, áudios, tônica
    gerar_avaliacao.mjs       # docs/AVALIACAO.md -> public/avaliacao.html
    capturas.mjs              # Playwright -> docs/capturas/
    smoke.mjs                 # testa uma URL como um cliente anônimo (seção 7)
    seed_demo.ts              # turma de demonstração
  e2e/                        # testes Playwright
  .github/workflows/ci.yml
  docs/  DECISOES.md  PROGRESSO.md  ARQUITETURA.md  AVALIACAO.md  capturas/
  README.md  CLAUDE.md  CREDITOS.md  LICENSE (MIT)
```

Regras de arquitetura:
- As **atividades só escutam o barramento de eventos**. Nenhuma atividade sabe se a entrada veio da câmera, do mouse ou do teclado.
- Toda regra fica em **funções puras com testes**: erros, pistas, nível, pinça, filtro, encaixe, comparação, soma de frações. Cada atividade tem um `logica.ts` sem React.
- A posição do cursor e dos itens arrastados é atualizada por `ref` e `transform`, **nunca por `setState` a cada quadro**. A detecção da mão roda fora do ciclo de renderização do React.
- O **alvo de um ponteiro** é descoberto com `document.elementsFromPoint(x, y)` procurando o ancestral mais próximo com `data-alvo`. Assim, câmera, mouse e teclado usam o mesmo caminho.

## 5. Design system (regras rígidas)

**Paleta.** No máximo 3 cores por tela, além de fundo e texto.

| Papel | Cor |
| --- | --- |
| Fundo | `#F6F3EC` |
| Texto | `#2A2A2A` |
| Primária | `#2F6F6A` |
| Destaque (só preenchimento, com texto escuro) | `#D9A441` |
| Apoio | `#8FA9C7` |

O perfil de alto contraste usa fundo `#FFFFFF`, texto `#000000` e primária `#00524C`. Escreva um teste Vitest que calcula o contraste WCAG de todas as combinações texto/fundo declaradas em `tokens.css` e falha se alguma ficar abaixo de 4,5:1.

**Proibido:** gradientes, sombras, brilhos, transparência decorativa, emoji como ícone, cantos com raio acima de 12 px, cards genéricos de template, vermelho para erro.

**Tipografia.** Atkinson Hyperlegible. O corpo mínimo na tela da criança é 24 px; instruções têm 32 px. Use `rem` e respeite o zoom do navegador até 200% sem quebrar o layout.

**Letras.** Letra bastão (maiúscula) nas trilhas iniciais; minúscula a partir das trilhas de 1º ano.

**Ilustrações.** SVG chapado, traço de 3 px `#2A2A2A`, preenchimentos da paleta, `viewBox="0 0 256 256"`, sem texto dentro. Desenhe uma figura por palavra (15), os objetos da Mesa (maçã, peixe, bolinha de gude) e 6 avatares de bichos simples. Toda figura informativa tem `<title>` ou `aria-label`.

**Alvos.** Mínimo de 64 × 64 px, com 16 px de espaço. O foco de teclado é um contorno de 4 px na cor primária, sempre visível.

**Movimento.** Animações de até 300 ms, sem flash. Respeite `prefers-reduced-motion` **e** a opção "Reduzir movimento" do perfil: com qualquer uma ligada, a duração das animações é 0.

**Sem distrações para quem avalia.** Nenhum pop-up, banner de cookies, captcha, tela de login, animação de entrada que atrase o conteúdo ou pedido de permissão automático.

## 6. Regras pedagógicas e de acessibilidade (a professora exige)

Toda atividade usa `AtividadeBase` e cumpre:

1. **Roteiro fixo em 3 momentos.** "O que vamos fazer" (figura + frase + áudio) → atividade → "Terminou!" + botão "Próximo". Uma faixa fixa no topo mostra **Agora / Depois** com ícones.
2. **Uma instrução por vez, literal.** "Pegue a bolha BO. Coloque na primeira caixa." Sem metáfora nem ironia. Todas as frases ficam em `conteudo/frases.json`, nunca espalhadas no código.
3. **Som só depois de uma ação da criança** (a política de autoplay dos navegadores exige isso de qualquer forma). Volume ajustável; nenhum som de "errado".
4. **Erro neutro.** "Vamos tentar de novo" + uma pista. Nunca X vermelho.
5. **Nunca só cor.** Seleção, acerto e categoria usam cor + forma ou hachura + texto.
6. **Botão Pausa sempre visível.** Congela a atividade, cobre a tela com o fundo, silencia o áudio e mostra "Continuar". Esc também pausa.
7. **Sem relógio e sem ranking.**
8. **Pistas graduais** (`progresso.ts`): 1ª = repetir a instrução com áudio; 2ª = realçar o que importa; 3ª = mostrar o modelo fazendo. Depois da 3ª, a atividade segue e a tentativa é registrada com `precisouModelo: true`.
9. **Ajuste de nível.** 4 acertos seguidos na 1ª tentativa → oferece o próximo nível ("Quer um desafio?", Sim/Não). 2 itens seguidos com modelo → volta um nível. O professor pode travar o nível.
10. **Toda ação por arrastar tem uma alternativa por clique:** selecionar o item (`aria-pressed="true"`) e depois clicar no destino. É o que faz a aplicação funcionar por teclado, por toque simples e para uma IA que só clica.
11. **ARIA e semântica.** Use `<button>`, `<main>`, `<nav>`, títulos em ordem, `aria-label` em pt-BR em tudo que for interativo, `aria-live="polite"` na região de anúncio (`anuncio.ts`: "Bolha BO colocada na caixa 1", "Faltam 2 sílabas"). A ordem do Tab segue a ordem visual. Todo elemento interativo tem `data-testid` estável.
12. **Teste automático de acessibilidade.** O e2e roda `axe-core` em cada tela e atividade e **falha** com qualquer violação `serious` ou `critical`.

### Perfis

`Perfil` é um tipo TypeScript com: `velocidade` (0–1), `maxItens`, `escala` (1.0–2.0), `altoContraste`, `paletaSegura`, `audioAuto`, `reduzirMovimento`, `somCelebracao`, `modoEntrada` (`"auto" | "ponteiro" | "permanencia" | "varredura"`), `toleranciaAlvoPx`, `tempoPermanenciaMs`, `espacamentoLetras`, `umPassoPorVez`, `rodadaItens`.

O perfil vira atributos e variáveis CSS em `<html>` (`data-perfil="tea"`, `--escala`, etc.). Perfis podem ser combinados pela regra **"a opção mais acessível vence"**: menor velocidade, menor `maxItens`, maior escala, `true` vence em flags de acessibilidade.

| Perfil | Valores |
| --- | --- |
| padrão | velocidade 0,5; maxItens 4; escala 1,0 |
| tea | velocidade 0; maxItens 3; somCelebracao false; aviso antes de trocar de atividade |
| tdah | umPassoPorVez true; maxItens 3; rodadaItens 5 |
| dislexia | audioAuto true; espacamentoLetras 0,12 em; escala 1,2; sílabas alternadas com cor **e** sublinhado; resposta sempre por escolha |
| baixa_visao | escala 1,75; altoContraste true; contornos de 5 px; maxItens 3 |
| daltonismo | paletaSegura true (hachuras e símbolos em toda distinção) |
| motor | modoEntrada "permanencia"; toleranciaAlvoPx 60; tempoPermanenciaMs 1200; varredura disponível |
| cegueira (parcial) | audioAuto true; descrição em áudio de cada item focado; uso por teclado |

O perfil e o modo de entrada também podem ser definidos pela URL (`?perfil=tea,dislexia&entrada=teclado`), o que serve às demonstrações e à avaliação (seção 7).

## 7. Avaliação por uma IA (requisito de primeira classe)

Tudo abaixo é testado em CI e no deploy.

### 7.1 A URL pública

- Abre **sem login, sem cookies obrigatórios, sem câmera**. A primeira tela já mostra o produto e um botão "Começar".
- **Links profundos** (hash) para tudo, com parâmetros:
  - `/#/` início
  - `/#/avaliacao` roteiro de avaliação interativo
  - `/#/atividade/silabas?palavra=bola&perfil=tea&entrada=teclado`
  - `/#/atividade/quantidades?modo=resolver&perfil=baixa_visao`
  - `/#/atividade/pizza?corte=4&perfil=daltonismo`
  - `/#/painel?demo=1` painel com a turma de demonstração
- O `index.html` tem **conteúdo estático útil dentro de `#root` e em `<noscript>`**: nome, problema, o que o produto faz, como testar em 2 minutos, links para o GitHub, `/avaliacao.html` e `/llms.txt`. Assim, uma IA que só busca o HTML (sem executar JavaScript) ainda entende o projeto. O React substitui esse conteúdo ao montar.
- `public/avaliacao.html` é uma página **100% estática**, gerada de `docs/AVALIACAO.md` por `scripts/gerar_avaliacao.mjs` no `prebuild`.
- `public/llms.txt` (formato llms.txt): título, resumo de 5 linhas, links para `/avaliacao.html`, README e as principais pastas do código.
- `robots.txt` permite tudo.

### 7.2 Modo demonstração (`?demo=1`)

- Cada atividade do MVP exporta `demo.ts` com um roteiro (`PassoDemo[]`): passos de entrada simulada pelo **mesmo barramento de eventos** (apontar, pegar, soltar, escolher), com uma legenda na tela e no anúncio aria-live ("Demonstração: a criança arrasta a bolha BO para a primeira caixa").
- `src/nucleo/demo.ts` executa o roteiro com atrasos curtos, mostra "Demonstração em andamento — clique em qualquer lugar para assumir o controle" e **não depende de câmera**.
- A demonstração deve incluir um **erro proposital**, a pista e o registro, para que o ciclo de diagnóstico apareça.
- `/#/avaliacao` tem um botão para cada demonstração.

### 7.3 `docs/AVALIACAO.md`

Escrito para uma IA e um humano. Contém:
1. O problema e a resposta do produto, em 8 linhas.
2. **Roteiro de teste em 2 minutos**, com 5 links diretos e o que esperar de cada um.
3. **Tabela afirmação → evidência** (arquivo e teste), por exemplo:

| Afirmação | Onde está | Como verificar |
| --- | --- | --- |
| Perfis combinam pela opção mais acessível | `src/nucleo/perfis.ts` | `npm test -- perfis` |
| O vídeo da câmera nunca sai do navegador | `src/entrada/camera.ts`, `e2e/privacidade.spec.ts` | o teste falha se houver requisição para outra origem |
| Funciona sem câmera, por teclado e por clique | `src/entrada/*`, `e2e/entradas.spec.ts` | `npm run e2e` |
| Sem violações de acessibilidade graves | `e2e/acessibilidade.spec.ts` | `npm run e2e` |
| O erro vira recomendação para o professor | `src/nucleo/erros.ts`, `conteudo/recomendacoes.json` | `npm test -- erros` |

4. As limitações conhecidas, sem enfeite (por exemplo: "a câmera exige HTTPS e uma webcam; sem elas, o app usa mouse/teclado automaticamente").

### 7.4 Testes que provam a privacidade e o funcionamento anônimo

- `e2e/privacidade.spec.ts`: registra todas as requisições de rede durante uma sessão completa (incluindo o modo câmera com webcam falsa) e **falha se qualquer requisição for para outra origem**. Um teste de lint (busca no código) também falha se `toDataURL` ou `toBlob` forem chamados sobre o vídeo da câmera.
- `e2e/entradas.spec.ts`: completa a mesma atividade por mouse, por teclado, por clique-clique e por varredura.
- `e2e/camera.spec.ts`: Chromium com `--use-fake-device-for-media-stream --use-fake-ui-for-media-stream`; confirma que o pipeline carrega o modelo e **não quebra** quando nenhuma mão aparece. Com a câmera negada, a aplicação cai para mouse/toque sem erro visível.
- `scripts/smoke.mjs <URL>`: age como um cliente anônimo contra a URL de produção: `fetch` do HTML (200, sem redirecionar para login, contém o conteúdo estático), de `/avaliacao.html`, `/llms.txt`, do `.wasm` e do modelo (status 200 e tamanho > 0), e abre as 3 atividades com Playwright verificando que não há erros no console.

## 8. Camada de entrada

Todas as entradas emitem os mesmos eventos de `nucleo/eventos.ts`: `apontar(x, y)` (coordenadas da viewport), `pegar()`, `soltar()` e `escolher(idItem)`.

- **Mouse/toque/caneta:** Pointer Events com `setPointerCapture`; arrastar e soltar, ou clique no item e depois no destino. Use `touch-action: none` nas áreas de arrasto.
- **Teclado:** setas e Tab movem o foco entre itens; Enter ou Espaço pega e solta; Esc pausa.
- **Varredura:** o foco avança sozinho a cada 1,5 s; qualquer tecla seleciona.
- **Câmera (`camera.ts` + `mao.ts`):**
  - Liga **somente** quando a criança ou o adulto clica em "Usar câmera" dentro de uma atividade. Nunca automático.
  - `getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } })`; o `<video>` fica oculto, ou como miniatura de 160 × 120 (desligada por padrão no perfil TEA); imagem espelhada.
  - Laço com `requestVideoFrameCallback` (ou `requestAnimationFrame`), alvo de 30 detecções por segundo, descartando quadros atrasados. Timestamps crescentes.
  - Se a média ficar abaixo de 15 fps, reduza para 480 × 360.
  - `mao.ts` (puro, 100% testado):
    - Cursor = ponto 8, passado por filtro One Euro (`minCutoff=1.0`, `beta=0.02`, configuráveis).
    - Área ativa = 80% central do quadro, mapeada para a viewport inteira.
    - Pinça = distância(4, 8) / distância(0, 9), com histerese: pega abaixo de 0,25 e solta acima de 0,40.
    - Permanência = cursor dentro de `toleranciaAlvoPx` por `tempoPermanenciaMs` → `pegar`; a mesma regra no destino → `soltar`.
  - Se a câmera for negada, não existir, ou o modelo não carregar em 5 s: entre no modo mouse/toque **sem mensagem de erro**, com só um ícone discreto "câmera desligada".
  - Indicador visível "Câmera ligada" enquanto ativa; desliga ao sair da atividade (`track.stop()`).
- **Overlay de depuração (`?debug=1`):** fps, razão da pinça e estado da mão.

## 9. Atividades do MVP

### 9.1 Ímã das Sílabas (Português)

- **Tela:** figura da palavra no centro alto; caixas vazias (uma por sílaba) abaixo; até `maxItens` bolhas com sílabas (as corretas + distratoras). As bolhas flutuam devagar (`velocidade × 40 px/s`) e ficam paradas quando a velocidade é 0. Cada bolha é um `<button>`.
- **Interação:**
  - Ao pegar uma bolha, toca a sílaba.
  - Ao soltá-la sobre uma caixa (a área expandida pela tolerância), ela encaixa.
  - Sílaba certa: fica na caixa. Errada: volta suavemente e a atividade dá uma pista.
  - Ao completar a palavra, toca a palavra inteira e realça as sílabas em sequência.
- **Distratoras.** Par surdo/sonoro (B↔P, T↔D, F↔V, C↔G) nos níveis altos; nos demais, uma sílaba de outra palavra.
- **Nível 4 (sílaba tônica):** "Qual bolha é a mais forte?"
- **Erros classificados:** `ordem_trocada`, `par_surdo_sonoro`, `silaba_de_outra_palavra`.

Formato de `conteudo/palavras.json` (15 palavras):

```json
{"id": "bola", "texto": "BOLA", "silabas": ["BO", "LA"],
 "fala": {"palavra": "bola", "silabas": ["bó", "la"]},
 "tonica": 0, "nivel": 1, "figura": "bola"}
```

- **Nível 1:** BOLA, CASA, PATO, GATO, SAPO, VACA
- **Nível 2:** MACACO, SAPATO, BONECA, JANELA, TOMATE
- **Nível 3:** BRAÇO, PRATO, PÁSSARO, LIVRO
- **Nível 4:** as mesmas palavras, perguntando a tônica

Pronúncia: `fala.silabas` é a grafia que o TTS deve ler para soar como dentro da palavra. Em BOLA, a sílaba BO é "bó" (aberto), nunca "bô". `validar_conteudo.mjs` confere que as sílabas concatenadas formam o texto, que existem a figura e os áudios (ou aviso de que a reserva será usada) e que `tonica` é um índice válido.

### 9.2 Mesa de Quantidades (Matemática)

- **Tela:** duas bandejas e um cesto de objetos (conjunto escolhido pelo professor). O número de cada bandeja é grande ao lado dela e atualiza a cada objeto, com áudio ("três maçãs").
- **Modos:**
  - **Montar:** livre, mostrando o número.
  - **Resolver:** `3 + 4 = ?` ou `7 − 2 = ?` (até 20). Monta com objetos e escolhe a resposta entre 3 cartões.
  - **Comparar:** os objetos das duas bandejas são ligados um a um por linhas; a sobra fica destacada (hachura + contorno + texto "sobrou"), e a criança escolhe "maior", "menor" ou "igual".
  - **Par/ímpar:** os objetos se organizam em duplas; sobrou um, é ímpar.
- **Erros classificados:** `um_a_mais_ou_menos` (|resposta − certo| = 1), `operacao_trocada`, `digitos_invertidos` (12 ↔ 21), `chute` (errou em menos de 1 500 ms).
- **Pista 2:** os objetos acendem um a um enquanto o áudio conta.

### 9.3 Pizza de Frações (Matemática)

- **Tela:** a criança escolhe o corte (2, 3, 4, 6 ou 8 fatias), pega e devolve fatias. A fração aparece embaixo, grande.
- **Resolver:** `1/4 + 2/4 = ?`. Duas pizzas com o mesmo corte; a criança junta as fatias numa terceira pizza e escolhe a resposta entre 3 cartões. Um dos cartões errados é sempre o de somar denominadores.
- **Desafio:** fração imprópria, por exemplo 7/8 + 8/8 = 15/8, mostrado também como 1 e 7/8.
- **Visual:** fatias selecionadas têm hachura diagonal + contorno grosso, não só cor. A alternativa é uma barra de chocolate retangular, nas opções da atividade.
- **Erros classificados:** `somou_denominadores`, `contou_fatias_errado`, `confundiu_numerador_denominador`.
- **Pista 2:** as duas pizzas aparecem sobrepostas, com o texto "as fatias continuam do mesmo tamanho".

### 9.4 Registro de cada tentativa

Estrutura em `localStorage`: `aluno`, `atividade`, `habilidade`, `item`, `resposta`, `correta`, `tipoErro`, `pistas`, `precisouModelo`, `tempoMs`, `modoEntrada`, `perfis`, `ts`. Os alunos têm apenas apelido e avatar (nunca nome completo nem foto). A área do adulto (segurar um botão por 2 s, ou pelo link `/#/adulto`) tem "Exportar JSON" e "Apagar todos os dados".

### 9.5 Painel do professor (P1)

- Grade aluno × habilidade com 3 estados, sempre com ícone e texto: **Domina** (≥ 80% de acerto na 1ª tentativa nas últimas 10), **Em progresso** e **Precisa de apoio** (< 50% ou ≥ 2 modelos nas últimas 10).
- Para cada "Precisa de apoio": o tipo de erro mais frequente e a frase de `recomendacoes.json`. Exemplo: *"Ana somou os denominadores em 3 de 4 tentativas. Sugestão: pizzas sobrepostas, mostrando que o tamanho da fatia não muda."*
- `seed_demo.ts` cria a "Turma de demonstração" (6 alunos fictícios), rotulada assim na tela. `/#/painel?demo=1` a carrega.

## 10. Marcos (execute em ordem; push e atualização do PROGRESSO.md ao fim de cada um)

**M0 — Repositório e ferramentas (≤ 25 min)**

- [ ] `gh auth status`; depois `gh repo view REPO` para confirmar acesso de escrita. Se não estiver logado, pare e peça `gh auth login`.
- [ ] O repositório **já existe e é privado**: não o crie nem mude a visibilidade. `git init -b main`, `git remote add origin https://github.com/REPO.git`, `git fetch origin`. Se houver commits remotos, `git pull origin main --rebase` antes do primeiro push.
- [ ] `npm create vite` (React + TS), ESLint, Prettier, Vitest, Playwright, axe, estrutura da seção 4, `.gitignore`, `CLAUDE.md`, `docs/*`, `README.md` (rascunho), `LICENSE`, `CREDITOS.md`.
- [ ] `ci.yml`: Node 20; `npm ci`; lint; typecheck; vitest; build; `npx playwright install --with-deps chromium`; e2e contra `vite preview`; sobe as capturas como artefato.
- **Aceite:** código no repositório privado com o CI verde.

**M1 — Esqueleto publicado, com câmera e página de avaliação (≤ 75 min; o maior risco)**

- [ ] Tema, fonte, navegação Início → Matérias → Trilhas e uma atividade "Teste de câmera" (cursor da mão + estado da pinça).
- [ ] `copiar_mediapipe.mjs` e `baixar_modelo.mjs`; commitar `public/mediapipe/`.
- [ ] `index.html` com conteúdo estático e `<noscript>`; `avaliacao.html`, `llms.txt`, `robots.txt` (versões iniciais).
- [ ] **Parada única:** peça para eu rodar `npx vercel login`. Depois, `vercel link --yes` e `vercel deploy --prod --yes`. Anote a URL no `CLAUDE.md`.
- [ ] Confirme que a URL é pública para um anônimo: `curl -sI URL` deve responder 200, **sem** redirecionar para `vercel.com/login` nem responder 401. Se houver proteção, peça para eu desligar "Vercel Authentication" em Project Settings → Deployment Protection, e repita.
- [ ] Rode `node scripts/smoke.mjs URL` e corrija até passar.
- [ ] Peça para eu abrir a URL no meu celular ou notebook e testar a câmera **uma vez**.
- **Aceite:** a URL pública abre, o cursor segue minha mão e o smoke test passa.

**M2 — Perfis e camada de entrada (≤ 60 min)**

- [ ] `perfis.ts` com combinação + testes; `tema.ts`; `eventos.ts`, `ponteiro.ts`, `teclado.ts`, `varredura.ts`, `mao.ts` (testes de One Euro, histerese, permanência, área ativa), `camera.ts` com fallback, `Cursor.tsx`, `anuncio.ts`.
- [ ] Área do adulto: criar aluno (apelido + avatar) e escolher perfis; perfis pela URL.
- **Aceite:** testes verdes; capturas de um protótipo com os perfis padrão, TEA e baixa visão revisadas por você; axe sem violações graves.

**M3 — Núcleo das atividades (≤ 45 min)**

- [ ] `AtividadeBase` (3 momentos, Agora/Depois, Pausa, pistas, ajuste de nível), `registro.ts`, `audio.ts` (MP3 + reserva), `demo.ts`.
- [ ] `gerar_audio.py` (se houver credencial do Google; caso contrário, registre e use a reserva), `validar_conteudo.mjs`.
- **Aceite:** testes de `progresso.ts` e `erros.ts` cobrem todas as regras das seções 6 e 9.

**M4 — Ímã das Sílabas (≤ 75 min)**

- [ ] Lógica pura, tela, níveis 1–4, 15 figuras SVG, áudios, erros e `demo.ts`.
- **Aceite:** e2e completa BOLA por mouse, por teclado, por clique-clique e por varredura; axe sem violações graves; capturas nos perfis padrão, TEA e dislexia; deploy de produção e smoke test.
- [ ] Tag `v0.1.0`.

**M5 — Mesa de Quantidades (≤ 60 min)**

- [ ] Os 4 modos, 3 conjuntos de objetos, erros e `demo.ts`.
- **Aceite:** testes da lógica, e2e, capturas, deploy e smoke test.

**M6 — Pizza de Frações (≤ 60 min)**

- [ ] Corte, pegar/devolver fatias, soma de mesmo denominador, desafio, alternativa em barra, erros e `demo.ts`.
- **Aceite:** testes da lógica, e2e, capturas, deploy e smoke test.
- [ ] Tag `v0.2.0`.

**M7 — Painel e instalação (P1/P2, ≤ 45 min)**

- [ ] `seed_demo.ts`, painel e recomendações.
- [ ] **PWA** com `vite-plugin-pwa`, instalável e com cache do modelo e do WASM. Cuide do cache: a estratégia deve atualizar sozinha (`autoUpdate`) e **nunca** impedir um cliente novo de ver a versão atual.
- **Aceite:** captura do painel; o app abre offline depois da primeira visita.

**M8 — Entrega (≤ 40 min)**

- [ ] `docs/AVALIACAO.md` completo (seção 7.3), `docs/ARQUITETURA.md` (diagrama Mermaid), `gerar_avaliacao.mjs`, `llms.txt` final.
- [ ] README em pt-BR: problema em 3 linhas, **link do deploy no topo**, "teste em 2 minutos", como usar sem webcam, atalhos de teclado, selo do CI, capturas, arquitetura, privacidade, créditos (Atkinson Hyperlegible/OFL, MediaPipe/Apache 2.0, voz usada).
- [ ] Deploy de produção, `smoke.mjs` na URL final, Lighthouse (desempenho ≥ 90 e acessibilidade 100 na página inicial).
- [ ] **Não torne o repositório público por conta própria.** Avise que precisa ficar público antes do envio (Settings → General → Danger Zone → Change visibility) e que eu devo abrir o link do GitHub numa aba anônima depois.
- [ ] Tag `v1.0.0`.
- **Aceite:** CI verde, produção passando no smoke test, `PROGRESSO.md` completo.

Se o tempo apertar, a ordem de corte é: M7 → desafio da Pizza → modo Par/ímpar → nível 4 do Ímã. **Nunca corte** a entrada sem câmera, os perfis, a Pausa, o modo demonstração, a página de avaliação nem o deploy público.

## 11. Requisitos de desempenho

- Carregamento inicial: JavaScript da primeira tela abaixo de 200 kB comprimido, sem contar o MediaPipe (carregado só ao ligar a câmera, por import dinâmico). Fonte em WOFF2 só latin, com `font-display: swap`. Áudio carregado por atividade, sob demanda.
- Interface a 60 fps durante as atividades: sem `setState` por quadro; cursor e itens por `transform`; detecção da mão fora do ciclo do React.
- Latência da mão até o cursor abaixo de 100 ms em um notebook comum.
- Áudio de uma sílaba começa em menos de 100 ms (pré-carregado para os itens da tela atual).
- Figuras SVG inline ou importadas como componentes; nenhuma imagem raster.
- Lighthouse na página inicial: desempenho ≥ 90, acessibilidade 100, boas práticas ≥ 95.

## 12. Fora do escopo

Login, backend, banco de dados em servidor, nuvem própria, IA generativa conversando com a criança, analytics, anúncios, gravação ou envio de imagem ou áudio, CDN ou fonte externos, e qualquer requisição para outra origem em tempo de execução.

## 13. Ao terminar cada marco

Responda em até 5 linhas: o que ficou pronto, o link do commit e da URL de produção, o que eu preciso testar manualmente (se houver) e a decisão mais importante registrada.

`````

## Anexo E — PROMPT_CLAUDE_CODE_DESKTOP_DOCKER.md (versão desktop com Docker, Turno 11; é a versão vigente)

`````markdown
# Prompt para o Claude Code — Atlas (software desktop + Docker)

> Cole tudo abaixo da linha no Claude Code, aberto numa pasta vazia no seu computador.
> Antes: `gh auth status` deve mostrar você logado e o **Docker** deve estar instalado e rodando (`docker --version`; no Windows e no macOS, o Docker Desktop). Para testar a câmera no M1, o computador precisa ter webcam.

---

## Variáveis

- `NOME_PRODUTO` = **Atlas**
- `REPO` = **edpl22/hackthonAstros** (já existe no GitHub, **privado**, pode estar vazio)
- `IMAGEM` = **ghcr.io/edpl22/atlas** (tudo em minúsculas)

## 1. Papel e missão

Você é engenheiro de software sênior (Python, Qt, visão computacional, Docker) e trabalha junto com uma professora experiente de alfabetização e educação inclusiva. Sua missão é construir, testar, empacotar, documentar e publicar no GitHub o software desktop **NOME_PRODUTO**, para uma hackathon de educação julgada pela Teachy.

O produto é um software instalável de português e matemática básica, da Educação Infantil ao 4º ano. A criança aprende com o corpo (mão na câmera, toque, mouse ou teclado), e **a mesma atividade se ajusta ao perfil de cada aluno** (TEA, TDAH, dislexia, baixa visão, daltonismo, dificuldade motora), sem o professor refazê-la. É uma resposta ao Desafio 01 da Teachy: *"Como podemos ajudar professores, escolas e família a fazerem com que todos os alunos aprendam o mesmo conteúdo, junto com a turma?"*

### Quem vai avaliar a parte técnica

**Uma IA** vai receber o link do GitHub e **seguir as instruções do README** para executar o software. A organização também orientou usar **Docker**. Portanto, parta destas premissas sobre a avaliadora:

- Ela lê o README e executa comandos de terminal, provavelmente num ambiente Linux, **sem tela, sem webcam, sem login e sem instalar nada além do que o README disser**.
- Um aplicativo de janelas é invisível para ela. Por isso o Atlas, além da interface gráfica, tem **modos de linha de comando que rodam sem tela** (seção 7) e produzem evidências que ela consegue ler: texto, JSON e imagens PNG.
- Ela pode falhar em qualquer passo do README. Por isso há **três caminhos** (Docker, Python direto e "só ler") e **saídas de exemplo já commitadas** no repositório.

Prioridades, nesta ordem:
1. O README leva a IA, passo a passo, de "acabei de clonar" a "vi o software funcionando", e **cada comando foi realmente executado por você a partir de um clone limpo**.
2. Qualidade pedagógica e de acessibilidade, demonstrável por testes e pelas saídas dos modos headless.
3. Código limpo, testado e documentado, que o time consegue explicar.

## 2. Como você deve trabalhar

1. **Autonomia.** Não faça perguntas, exceto se estiver bloqueado de verdade (permissão do GitHub, Docker ausente, teste de câmera previsto no M1). Quando algo for ambíguo, escolha a opção mais simples que cumpra a especificação e registre em `docs/DECISOES.md` (data, decisão, motivo, uma linha cada).
2. **Ciclo curto.** Para cada tarefa: implementar → `ruff check` e `pytest` → corrigir → commit. Faça push ao fim de cada marco. Nunca deixe `main` quebrado.
3. **Commits.** Pequenos e atômicos, em Conventional Commits em pt-BR, por exemplo `feat(silabas): bolhas arrastáveis com encaixe` ou `fix(docker): libs do plugin xcb`. Nunca use `--force` nem reescreva o histórico publicado.
4. **Memória do projeto.** No M0, crie um `CLAUDE.md` na raiz com: comandos (instalar, rodar, testar, empacotar, Docker), estrutura de pastas, convenções e o estado dos marcos. Atualize ao fim de cada marco. Releia-o se perder contexto.
5. **Plano visível.** Mantenha `docs/PROGRESSO.md` com a checklist da seção 10.
6. **Verifique o visual por imagem.** Você não vê a tela. O comando `atlas demo` (seção 7) já salva PNG de cada passo; abra-os com sua ferramenta de leitura de imagem e confira o layout contra o design system (seção 5) antes de fechar cada marco de interface.
7. **Subagentes.** Use subagentes para tarefas independentes que não mexem nos mesmos arquivos: desenhar as figuras SVG, escrever `palavras.json` e `objetos.json`, escrever testes de lógica pura. A integração fica com você.
8. **Time-box.** Se um problema travar por mais de ~20 min, simplifique, registre em `DECISOES.md` e siga em frente.
9. **Segredos.** Nunca commite credenciais, `.env`, JSON de conta de serviço, `.venv`, `build/`, `dist/` nem `saida/` (exceto `docs/saida-exemplo/`). Configure o `.gitignore` antes do primeiro commit.
10. **Origem do conteúdo.** Todo o código, áudio e figura é produzido neste evento. Cite no `CREDITOS.md` cada biblioteca, fonte, modelo e voz de terceiros com a licença.

## 3. Stack travada

Não troque nada desta tabela sem registrar o motivo em `DECISOES.md`.

| Camada | Escolha | Observação |
| --- | --- | --- |
| Linguagem | Python 3.11 | Os wheels do mediapipe exigem 3.9–3.12 |
| Interface | **PySide6-Essentials**, com **Widgets + QGraphicsView** para as atividades | Sem QML: toda a lógica fica em Python, testável com pytest-qt em offscreen. O pacote Essentials é bem menor que o PySide6 completo |
| Figuras | SVG via `QSvgRenderer` / `QGraphicsSvgItem` | Escala sem perda no zoom de baixa visão |
| Câmera | OpenCV (`cv2.VideoCapture`) numa `QThread` | No Windows, `cv2.CAP_DSHOW`; no macOS, o padrão. **Dependência opcional**: ver abaixo |
| Mão | MediaPipe Hand Landmarker (Tasks API, `running_mode=VIDEO`, `num_hands=1`) | Modelo `hand_landmarker.task` em `assets/modelos/`, baixado por `scripts/baixar_modelo.py` e commitado (Apache 2.0). Se a Tasks API falhar, use `mediapipe.solutions.hands` |
| Áudio | `QSoundEffect` com **WAV** (PCM 16 bits, 22 050 Hz, mono) | QSoundEffect não toca MP3. Sem dispositivo de áudio (Docker), use o backend nulo: `ATLAS_AUDIO=nulo` registra no log "toca bola_1.wav" em vez de tocar |
| Reserva de voz | Legenda na tela com a frase | Sem WAV para um texto, mostre a legenda e registre no log |
| Geração de áudio | `scripts/gerar_audio.py` com dois provedores: `google` (Cloud TTS, voz pt-BR Neural2/WaveNet, saída LINEAR16) e `espeak` (`espeak-ng -v pt-br -w`, offline) | `google` só roda com `GOOGLE_APPLICATION_CREDENTIALS`. Sem ela, use `espeak`, registre a qualidade e **commite os WAV gerados** |
| Dados | SQLite (`sqlite3` da stdlib) em `ATLAS_DADOS` (padrão: pasta de dados do usuário de cada SO; no Docker, `/dados`), com exportação JSON | Sem servidor |
| CLI | `argparse` da stdlib; script de console `atlas` no `pyproject.toml` | `atlas` sem subcomando abre a interface gráfica |
| Qualidade | `ruff`, `pytest`, `pytest-qt` com `QT_QPA_PLATFORM=offscreen` | |
| Instalador | PyInstaller em modo **onedir** | onefile descompacta o mediapipe a cada abertura |
| Contêiner | `Dockerfile` + `docker-compose.yml` (seção 8) | Imagem publicada no GHCR |
| CI/CD | GitHub Actions: testes e build Docker a cada push; builds Windows e macOS e imagem no GHCR a cada tag `v*` | |
| Rede | **Nenhuma chamada de rede em tempo de execução** | Só os scripts de preparo e o build acessam a rede |

**Dependências em dois níveis** (obrigatório, para que o modo headless funcione em qualquer lugar):
- `requirements.txt`: núcleo (PySide6-Essentials, pytest etc.), sem câmera.
- `requirements-camera.txt`: `opencv-python` + `mediapipe`. **Importe `cv2` e `mediapipe` de forma preguiçosa**, só dentro de `entrada/camera.py` e só quando a câmera for ligada. Todo o resto (testes, `verificar`, `demo`, `agente`) deve rodar sem eles. Se estiverem ausentes, o app cai para mouse/toque e `atlas verificar` informa isso.

Use `pyproject.toml` com versões mínimas fixadas; gere o `requirements*.txt` a partir dele.

## 4. Arquitetura

```text
atlas/
  app/
    main.py                 # interface gráfica
    cli.py                  # ponto de entrada de `atlas`: subcomandos da seção 7
    nucleo/
      eventos.py            # barramento: apontar(x,y), pegar, soltar, escolher (Qt Signals)
      perfis.py             # dataclass Perfil, perfis prontos, combinação
      tema.py               # paleta, fonte, escala; aplica o perfil
      audio.py              # ServicoAudio: WAV pelo manifesto; backend nulo; legenda
      registro.py           # SQLite: alunos, tentativas; exporta JSON
      progresso.py          # pistas graduais, ajuste de nível (puro)
      erros.py              # classificadores de erro + tabela erro -> recomendação (puro)
      anuncio.py            # frase narrando cada evento ("Bolha BO colocada na caixa 1")
    headless/
      verificar.py          # atlas verificar
      demo.py               # atlas demo: executa roteiros e salva evidências
      agente.py             # atlas agente: protocolo JSON Lines (seção 7.4)
      relatorio.py          # gera relatorio.md
    entrada/
      ponteiro.py  teclado.py  varredura.py
      camera.py             # QThread: OpenCV + MediaPipe (import preguiçoso)
      mao.py                # lógica PURA: One Euro, pinça com histerese, permanência, área ativa
      mao_simulada.py       # reproduz landmarks sintéticos de conteudo/simulacao_mao.json
      cursor.py
    telas/
      inicio.py  materias.py  trilhas.py  adulto.py  painel.py
    atividades/
      base.py               # AtividadeBase: roteiro 3 momentos, Agora/Depois, Pausa, pistas, registro, estado()
      silabas/  quantidades/  pizza/   # cada uma: logica.py (pura), cena.py, demo.py, testes
  conteudo/
    palavras.json  objetos.json  recomendacoes.json  frases.json
    manifesto_audio.json  simulacao_mao.json
  assets/  audio/  figuras/  fontes/  modelos/
  scripts/
    baixar_modelo.py  baixar_fonte.py  gerar_audio.py  validar_conteudo.py
    seed_demo.py  gerar_saida_exemplo.sh  verificar_readme.sh
  tests/
  empacotamento/  atlas.spec
  docker/  entrypoint.sh  gui.sh
  Dockerfile  docker-compose.yml  .dockerignore
  .github/workflows/ci.yml  .github/workflows/release.yml
  docs/  DECISOES.md  PROGRESSO.md  ARQUITETURA.md  AVALIACAO.md  saida-exemplo/
  README.md  CLAUDE.md  CREDITOS.md  LICENSE (MIT)
```

Regras de arquitetura:
- As **atividades só escutam o barramento de eventos**. Nenhuma atividade sabe se a entrada veio da câmera, do mouse, do teclado, de um roteiro de demonstração ou do agente. Esse é o princípio que torna a demo e o agente baratos.
- Toda regra fica em **funções puras com testes** (`logica.py`, `progresso.py`, `erros.py`, `mao.py`). Os widgets só desenham e repassam eventos.
- Toda atividade expõe `estado() -> dict` (serializável em JSON): tela, instrução atual, itens (com `id`, `rotulo`, `tipo`, `posicao`, `disponivel`), alvos, nível, pista atual, se concluiu. Os **ids são estáveis**: `bolha-bo-0`, `caixa-1`, `cartao-7`, `fatia-3`, `objeto-maca-2`.

## 5. Design system (regras rígidas)

**Paleta.** No máximo 3 cores por tela, além de fundo e texto.

| Papel | Cor |
| --- | --- |
| Fundo | `#F6F3EC` |
| Texto | `#2A2A2A` |
| Primária | `#2F6F6A` |
| Destaque (só preenchimento, com texto escuro) | `#D9A441` |
| Apoio | `#8FA9C7` |

O perfil de alto contraste usa fundo `#FFFFFF`, texto `#000000` e primária `#00524C`. Escreva um teste que calcula o contraste WCAG de todas as combinações texto/fundo usadas e falha se alguma ficar abaixo de 4,5:1.

**Proibido:** gradientes, sombras, brilhos, transparência decorativa, emoji como ícone, cantos com raio acima de 12 px, cards genéricos de template, vermelho para erro.

**Fonte.** Atkinson Hyperlegible (licença OFL), baixada por `scripts/baixar_fonte.py` para `assets/fontes/`, **commitada** e registrada com `QFontDatabase`. O corpo mínimo na tela da criança é 24 px; instruções têm 32 px.

**Letras.** Letra bastão (maiúscula) nas trilhas iniciais; minúscula a partir das trilhas de 1º ano.

**Ilustrações.** SVG chapado, traço de 3 px `#2A2A2A`, preenchimentos da paleta, `viewBox="0 0 256 256"`, sem texto dentro. Desenhe à mão uma figura por palavra (15), os objetos da Mesa (maçã, peixe, bolinha de gude) e 6 avatares de bichos simples.

**Alvos.** Mínimo de 64 × 64 px, com 16 px de espaço. O foco de teclado é um contorno de 4 px na cor primária, sempre visível.

**Movimento.** Animações de até 300 ms, sem flash. Com "Reduzir movimento" ligado, a duração é 0.

## 6. Regras pedagógicas e de acessibilidade (a professora exige)

Toda atividade herda de `AtividadeBase` e cumpre:

1. **Roteiro fixo em 3 momentos.** "O que vamos fazer" (figura + frase + áudio) → atividade → "Terminou!" + botão "Próximo". Uma faixa fixa no topo mostra **Agora / Depois** com ícones.
2. **Uma instrução por vez, literal.** "Pegue a bolha BO. Coloque na primeira caixa." Sem metáfora nem ironia. Todas as frases ficam em `conteudo/frases.json`.
3. **Som só depois de uma ação da criança.** Volume ajustável; nenhum som de "errado".
4. **Erro neutro.** "Vamos tentar de novo" + uma pista. Nunca X vermelho.
5. **Nunca só cor.** Seleção, acerto e categoria usam cor + forma ou hachura + texto.
6. **Botão Pausa sempre visível.** Congela a atividade, cobre a tela com o fundo a 85% de opacidade, silencia o áudio e mostra "Continuar". Esc também pausa.
7. **Sem relógio e sem ranking.**
8. **Pistas graduais** (`progresso.py`): 1ª = repetir a instrução com áudio; 2ª = realçar o que importa; 3ª = mostrar o modelo fazendo. Depois da 3ª, a atividade segue e a tentativa é registrada com `precisou_modelo=True`.
9. **Ajuste de nível.** 4 acertos seguidos na 1ª tentativa → oferece o próximo nível ("Quer um desafio?", Sim/Não). 2 itens seguidos com modelo → volta um nível. O professor pode travar o nível.
10. **Acessibilidade Qt.** Todo widget interativo tem `setAccessibleName` em pt-BR. A ordem do Tab segue a ordem visual.
11. **Toda ação de arrastar tem alternativa por clique:** selecionar o item e depois o destino.

### Perfis

`Perfil` é uma dataclass com: `velocidade` (0–1), `max_itens`, `escala` (1.0–2.0), `alto_contraste`, `paleta_segura`, `audio_auto`, `reduzir_movimento`, `som_celebracao`, `modo_entrada_preferido`, `tolerancia_alvo_px`, `tempo_permanencia_ms`, `espacamento_letras`, `um_passo_por_vez`, `rodada_itens`.

Perfis podem ser combinados pela regra **"a opção mais acessível vence"**: menor velocidade, menor `max_itens`, maior escala, `True` vence em flags de acessibilidade.

| Perfil | Valores |
| --- | --- |
| padrao | velocidade 0,5; max_itens 4; escala 1,0 |
| tea | velocidade 0; max_itens 3; som_celebracao False; aviso antes de trocar de atividade |
| tdah | um_passo_por_vez True; max_itens 3; rodada_itens 5 |
| dislexia | audio_auto True; espacamento_letras 0,12 em; escala 1,2; sílabas alternadas com cor **e** sublinhado; resposta sempre por escolha |
| baixa_visao | escala 1,75; alto_contraste True; contornos de 5 px; max_itens 3 |
| daltonismo | paleta_segura True (hachuras e símbolos em toda distinção) |
| motor | modo_entrada_preferido "permanencia"; tolerancia_alvo_px 60; tempo_permanencia_ms 1200; varredura disponível |
| cegueira | audio_auto True; descrição em áudio de cada item focado; uso por teclado (suporte parcial) |

Os nomes acima são os valores aceitos por `--perfil` nos comandos da CLI (combináveis com vírgula: `--perfil tea,dislexia`).

## 7. Execução sem tela: a interface da avaliadora

Este é o requisito que decide se uma IA consegue avaliar o software. Tudo roda com `QT_QPA_PLATFORM=offscreen`, sem webcam e sem áudio. `atlas` é o comando; no Docker, o entrypoint já é `atlas`.

### 7.1 `atlas verificar`

Confere o ambiente e imprime uma linha por checagem, com `OK` ou `--` (não essencial) ou `FALHA`:

```text
OK  python 3.11
OK  qt offscreen
OK  fonte Atkinson Hyperlegible
OK  conteudo: 15 palavras, 3 conjuntos de objetos, 8 perfis
OK  audio: 63 arquivos WAV; backend nulo
--  camera: pacote opencv/mediapipe ausente ou sem dispositivo; o modo mouse/toque sera usado
OK  banco de dados: criado em /dados
RESULTADO: pronto
```

Sai com código 0 se não houver `FALHA`, e 1 caso contrário.

### 7.2 `atlas demo`

`atlas demo {silabas|quantidades|pizza|painel|todas} [--perfil LISTA] [--entrada {mouse|teclado|varredura|mao-simulada}] [--saida DIR] [--tamanho 1280x720]`

Executa o **roteiro de demonstração** da atividade (`demo.py` de cada atividade) pelo barramento de eventos e, a cada passo, salva uma captura (`widget.grab()`), a frase narrada e o estado. O roteiro inclui **um erro proposital**, a pista e o registro, para mostrar o ciclo de diagnóstico. Em `--saida` (padrão `./saida`) escreve:

- `captura-NN-<passo>.png` (uma por passo);
- `relatorio.md` (tabela: passo, evento, frase narrada, captura, tipo de erro, pista);
- `tentativas.json` (o registro SQLite dessa execução);
- `eventos.jsonl` (um evento por linha);
- `audio.log` (cada áudio que tocaria).

Imprime no terminal um resumo curto e termina com código 0. Com `--entrada mao-simulada`, os eventos vêm de `conteudo/simulacao_mao.json` (landmarks sintéticos de uma mão que aponta, faz pinça e solta), passando por `mao.py` real: isso demonstra o caminho da câmera **sem webcam**. `atlas demo painel` gera a captura do painel do professor com a "Turma de demonstração".

### 7.3 `atlas perfis`

Imprime em JSON todos os perfis e as regras de combinação, para a IA conferir contra o README. `atlas perfis --combinar tea,dislexia` mostra o resultado combinado.

### 7.4 `atlas agente <atividade> [--perfil LISTA]`: a IA joga de verdade

Protocolo **JSON Lines** em stdin/stdout (uma requisição JSON por linha, uma resposta JSON por linha), sem tela. O primeiro retorno é:

```json
{"pronto": true, "atividade": "silabas", "acoes": ["estado","apontar","pegar","soltar","escolher","pausar","continuar","captura","proximo","sair"]}
```

Requisições:

```json
{"acao": "estado"}
{"acao": "pegar", "id": "bolha-bo-0"}
{"acao": "soltar", "alvo": "caixa-1"}
{"acao": "escolher", "id": "cartao-7"}
{"acao": "apontar", "x": 640, "y": 360}
{"acao": "captura", "arquivo": "passo1.png"}
{"acao": "sair"}
```

Resposta padrão:

```json
{"ok": true, "anuncio": "Bolha BO colocada na caixa 1.",
 "estado": {"tela": "silabas", "nivel": 1, "instrucao": "Coloque a bolha LA na segunda caixa.",
            "itens": [{"id": "bolha-la-1", "rotulo": "LA", "tipo": "bolha", "disponivel": true}],
            "alvos": [{"id": "caixa-2", "rotulo": "segunda caixa"}],
            "pista_nivel": 0, "concluida": false}}
```

Erros retornam `{"ok": false, "erro": "item inexistente: bolha-xx", "dica": "ids disponíveis: ..."}`. O agente é só um adaptador fino sobre o barramento de eventos e `estado()`: **não reimplemente regras**.

### 7.5 Docker: o caminho recomendado no README

Seção 8.

### 7.6 O que a avaliadora deve conseguir fazer só com o README

1. Ver o que é o produto e por que existe (5 linhas).
2. Executar `docker compose run --rm verificar` e ver `RESULTADO: pronto`.
3. Executar `docker compose run --rm demo` e ler `saida/relatorio.md` e abrir os PNG.
4. Executar `docker compose run --rm teste` e ver os testes passarem.
5. Jogar uma atividade pelo agente (`docker compose run --rm -T agente`, enviando JSON por stdin).
6. (Opcional) Abrir a interface gráfica real no navegador por `docker compose up gui` e acessar `http://localhost:6080`.
7. Sem Docker: o mesmo por `pip install` e `atlas ...`.
8. Sem executar nada: ler `docs/AVALIACAO.md` e olhar `docs/saida-exemplo/`.

## 8. Docker

### 8.1 `Dockerfile`

- Base `python:3.11-slim-bookworm`; executa como **root** (evita problemas de permissão em volumes montados; registre em `DECISOES.md`).
- `apt-get install -y --no-install-recommends`: `libegl1 libgl1 libxkbcommon0 libdbus-1-3 libfontconfig1 libglib2.0-0 fonts-dejavu-core xvfb x11vnc novnc websockify tini` mais as bibliotecas xcb que o Qt precisar para o modo `gui` (`libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0`). Teste de verdade: se o plugin `xcb` não iniciar sob Xvfb, descubra a biblioteca faltante e acrescente.
- `pip install --no-cache-dir -r requirements.txt -r requirements-camera.txt` e `pip install .` (instala o comando `atlas`).
- `ENV QT_QPA_PLATFORM=offscreen ATLAS_AUDIO=nulo ATLAS_DADOS=/dados PYTHONUNBUFFERED=1`.
- Pastas `/saida` e `/dados`; `ENTRYPOINT ["tini","--","atlas"]`; `CMD ["verificar"]`.
- `.dockerignore` enxuto (`.git`, `.venv`, `dist`, `build`, `saida`, `node_modules`).
- Alvo de tamanho: abaixo de 1,5 GB. Se mediapipe não tiver wheel para a arquitetura, instale só em `amd64` e registre; o headless não depende dele.
- **Sem acesso à rede em tempo de execução.** O build usa rede; o contêiner não precisa.

### 8.2 `docker-compose.yml`

```yaml
services:
  verificar:
    build: .
    command: ["verificar"]
  demo:
    build: .
    command: ["demo", "todas", "--saida", "/saida"]
    volumes: ["./saida:/saida"]
  teste:
    build: .
    entrypoint: ["python", "-m", "pytest", "-q"]
  agente:
    build: .
    stdin_open: true
    command: ["agente", "silabas"]
  gui:
    build: .
    command: ["gui"]
    ports: ["6080:6080"]
```

Prefira também a imagem pronta do GHCR: `docker run --rm IMAGEM:latest verificar`. O README traz as duas formas (`build` e `pull`).

### 8.3 `docker/gui.sh` (opcional, P1)

Sobe `Xvfb :99 -screen 0 1280x720x24`, `x11vnc` e `websockify` com o noVNC na porta 6080, e inicia `atlas` com `QT_QPA_PLATFORM=xcb`, `DISPLAY=:99`. Sem webcam: a entrada é mouse e teclado pelo navegador. Quem abrir `http://localhost:6080/vnc.html` vê e usa o software real.

### 8.4 Câmera real em Linux (opcional)

Documente no README: `docker run --device /dev/video0 ...` funciona em Linux. No macOS e no Windows, o Docker não expõe a webcam; use o instalador nativo ou a `mao-simulada`.

## 9. Camada de entrada

Todas as entradas emitem os mesmos sinais em `nucleo/eventos.py`: `apontar(x, y)` (coordenadas da cena), `pegar()`, `soltar()` e `escolher(id_item)`.

- **Mouse/toque:** arrastar e soltar, ou clique no item e depois no destino. Habilite `Qt.WA_AcceptTouchEvents`.
- **Teclado:** setas e Tab movem o foco entre itens; Enter ou Espaço pega e solta; Esc pausa.
- **Varredura:** o foco avança sozinho a cada 1,5 s; qualquer tecla seleciona.
- **Câmera (`camera.py` + `mao.py`):**
  - Roda numa `QThread`, captura em 640 × 480, espelha a imagem, descarta quadros atrasados, alvo de 30 fps; timestamps do MediaPipe em ms, sempre crescentes.
  - Se a média ficar abaixo de 15 fps, reduz para 480 × 360. Só converte para `QImage` se a miniatura estiver ligada (desligada no perfil TEA; 160 × 120 nos demais).
  - `mao.py` (puro, 100% testado):
    - Cursor = ponto 8, passado por filtro One Euro (`min_cutoff=1.0`, `beta=0.02`).
    - Área ativa = 80% central do quadro, mapeada para a cena inteira.
    - Pinça = distância(4, 8) / distância(0, 9), com histerese: pega abaixo de 0,25 e solta acima de 0,40.
    - Permanência = cursor dentro de `tolerancia_alvo_px` por `tempo_permanencia_ms` → `pegar`; a mesma regra no destino → `soltar`.
  - Se a câmera não abrir em 3 s ou não existir, entra no modo mouse/toque **sem mensagem de erro**, com só um ícone discreto "câmera desligada".
  - A câmera só liga **dentro de uma atividade**, com indicador visível ("Câmera ligada") e desliga ao sair. Nenhum quadro é salvo. Um teste garante que o código não chama `cv2.imwrite` nem abre conexões de rede.
- **Overlay de depuração:** F12 mostra fps, razão da pinça e estado da mão.

## 10. Atividades do MVP

Cada atividade entrega: lógica pura + testes, cena, `estado()`, `demo.py` (com um erro proposital), erros classificados e áudios.

### 10.1 Ímã das Sílabas (Português)

- **Tela:** figura da palavra no centro alto; caixas vazias (uma por sílaba) abaixo; até `max_itens` bolhas com sílabas (as corretas + distratoras). As bolhas flutuam devagar (`velocidade × 40 px/s`) e ficam paradas quando a velocidade é 0.
- **Interação:** ao pegar uma bolha, toca a sílaba; ao soltá-la sobre uma caixa (área expandida pela tolerância), ela encaixa. Certa: fica. Errada: volta suavemente e a atividade dá uma pista. Ao completar, toca a palavra inteira e realça as sílabas em sequência.
- **Distratoras.** Par surdo/sonoro (B↔P, T↔D, F↔V, C↔G) nos níveis altos; nos demais, uma sílaba de outra palavra.
- **Nível 4 (sílaba tônica):** "Qual bolha é a mais forte?"
- **Erros classificados:** `ordem_trocada`, `par_surdo_sonoro`, `silaba_de_outra_palavra`.

Formato de `conteudo/palavras.json` (15 palavras):

```json
{"id": "bola", "texto": "BOLA", "silabas": ["BO", "LA"],
 "fala": {"palavra": "bola", "silabas": ["bó", "la"]},
 "tonica": 0, "nivel": 1, "figura": "figuras/bola.svg"}
```

- **Nível 1:** BOLA, CASA, PATO, GATO, SAPO, VACA
- **Nível 2:** MACACO, SAPATO, BONECA, JANELA, TOMATE
- **Nível 3:** BRAÇO, PRATO, PÁSSARO, LIVRO
- **Nível 4:** as mesmas palavras, perguntando a tônica

Pronúncia: `fala.silabas` é a grafia que a síntese deve ler para soar como dentro da palavra. Em BOLA, a sílaba BO é "bó" (aberto), nunca "bô". `validar_conteudo.py` confere que as sílabas concatenadas formam o texto, que existem a figura e os áudios e que `tonica` é um índice válido.

### 10.2 Mesa de Quantidades (Matemática)

- **Tela:** duas bandejas e um cesto de objetos (conjunto escolhido pelo professor). O número de cada bandeja fica grande ao lado dela e atualiza a cada objeto, com áudio ("três maçãs").
- **Modos:** **Montar** (livre); **Resolver** (`3 + 4 = ?` ou `7 − 2 = ?`, até 20; monta com objetos e escolhe a resposta entre 3 cartões); **Comparar** (objetos das duas bandejas ligados um a um por linhas; a sobra fica destacada com hachura + contorno + texto "sobrou"; a criança escolhe "maior", "menor" ou "igual"); **Par/ímpar** (objetos em duplas; sobrou um, é ímpar).
- **Erros classificados:** `um_a_mais_ou_menos` (|resposta − certo| = 1), `operacao_trocada`, `digitos_invertidos` (12 ↔ 21), `chute` (errou em menos de 1 500 ms).
- **Pista 2:** os objetos acendem um a um enquanto o áudio conta.

### 10.3 Pizza de Frações (Matemática)

- **Tela:** a criança escolhe o corte (2, 3, 4, 6 ou 8 fatias), pega e devolve fatias. A fração aparece embaixo, grande.
- **Resolver:** `1/4 + 2/4 = ?`. Duas pizzas com o mesmo corte; a criança junta as fatias numa terceira pizza e escolhe a resposta entre 3 cartões. Um dos cartões errados é sempre o de somar denominadores.
- **Desafio:** fração imprópria, por exemplo 7/8 + 8/8 = 15/8, mostrado também como 1 e 7/8.
- **Visual:** fatias selecionadas têm hachura diagonal + contorno grosso. Alternativa: barra de chocolate retangular, nas opções.
- **Erros classificados:** `somou_denominadores`, `contou_fatias_errado`, `confundiu_numerador_denominador`.
- **Pista 2:** as duas pizzas aparecem sobrepostas, com o texto "as fatias continuam do mesmo tamanho".

### 10.4 Registro de cada tentativa

Tabela `tentativas`: `aluno`, `atividade`, `habilidade`, `item`, `resposta`, `correta`, `tipo_erro`, `pistas`, `precisou_modelo`, `tempo_ms`, `modo_entrada`, `perfis`, `ts`. Os alunos têm apenas apelido e avatar (nunca nome completo nem foto). A área do adulto (segurar um botão por 2 s) tem "Exportar JSON" e "Apagar todos os dados".

### 10.5 Painel do professor (P1)

- Grade aluno × habilidade com 3 estados, sempre com ícone e texto: **Domina** (≥ 80% de acerto na 1ª tentativa nas últimas 10), **Em progresso** e **Precisa de apoio** (< 50% ou ≥ 2 modelos nas últimas 10).
- Para cada "Precisa de apoio": o tipo de erro mais frequente e a frase de `recomendacoes.json`. Exemplo: *"Ana somou os denominadores em 3 de 4 tentativas. Sugestão: pizzas sobrepostas, mostrando que o tamanho da fatia não muda."*
- `seed_demo.py` cria a "Turma de demonstração" (6 alunos fictícios), rotulada assim na tela.

## 11. README e documentos para a avaliadora

### 11.1 Estrutura obrigatória do `README.md` (em pt-BR)

1. **Título, selo do CI e resumo de 5 linhas**: o problema, o desafio da Teachy e a ideia ("uma atividade, vários perfis").
2. **Para a IA avaliadora: como executar** (logo no topo; veja 11.2).
3. **Para uma pessoa**: download do instalador (Releases: `Atlas-windows.zip`, `Atlas-macos.zip`), como abrir no macOS sem assinatura (botão direito → Abrir, ou `xattr -dr com.apple.quarantine Atlas.app`), como usar sem webcam, atalhos de teclado.
4. Capturas (de `docs/saida-exemplo/`).
5. Arquitetura (diagrama Mermaid) e link para `docs/ARQUITETURA.md`.
6. Privacidade (o vídeo nunca sai do computador; sem rede em tempo de execução).
7. Créditos e licenças.

### 11.2 Seção "Para a IA avaliadora: como executar"

Escreva-a assim, com os comandos exatos e a saída esperada de cada um:

```markdown
## Para a IA avaliadora: como executar

Este é um software desktop (Qt). Ele não abre no navegador. Para avaliá-lo sem tela e sem webcam, use os modos de linha de comando abaixo. Tudo foi testado a partir de um clone limpo.

Requisito: Docker (ou Python 3.11). Tempo estimado: 5 a 10 min no total.

### Caminho A — Docker (recomendado)
1. `git clone https://github.com/edpl22/hackthonAstros && cd hackthonAstros`
2. `docker compose build`   (alternativa, sem build: `docker pull ghcr.io/edpl22/atlas:latest`)
3. `docker compose run --rm verificar`     → deve terminar com `RESULTADO: pronto`
4. `docker compose run --rm demo`          → gera `./saida/` com `relatorio.md`, `captura-*.png`, `tentativas.json`
5. `docker compose run --rm teste`         → deve terminar com `passed`
6. Jogar via agente (JSON por stdin):
   `echo '{"acao":"estado"}' | docker compose run --rm -T agente`
7. (Opcional) Ver a interface real: `docker compose up gui` e abrir http://localhost:6080/vnc.html

### Caminho B — Python, sem Docker
`python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pip install .`
`export QT_QPA_PLATFORM=offscreen ATLAS_AUDIO=nulo`
`atlas verificar && atlas demo todas --saida ./saida`

### Caminho C — Só ler
`docs/AVALIACAO.md` (afirmação → arquivo → teste) e `docs/saida-exemplo/` (saídas reais já geradas).

### O que olhar
(lista dos arquivos de `saida/` e o que cada um prova)

### Problemas comuns
(Apple Silicon, `docker compose` vs `docker-compose`, permissões, falta de rede no build)
```

Itens obrigatórios da seção: o que é cada arquivo de saída; o protocolo do agente com 2 exemplos; a lista de `ids`; como usar `--perfil` e `--entrada`; e uma frase honesta: **"A câmera real não é testável sem webcam; o caminho dela é coberto por `--entrada mao-simulada` e pelos testes de `mao.py`."**

### 11.3 `docs/AVALIACAO.md`

Escrito para uma IA e um humano:
1. O problema e a resposta do produto, em 8 linhas.
2. **Tabela afirmação → evidência**, por exemplo:

| Afirmação | Onde está | Como verificar |
| --- | --- | --- |
| Perfis combinam pela opção mais acessível | `app/nucleo/perfis.py` | `atlas perfis --combinar tea,dislexia`; `pytest tests/test_perfis.py` |
| O erro vira recomendação para o professor | `app/nucleo/erros.py`, `conteudo/recomendacoes.json` | `atlas demo pizza` e leia `saida/relatorio.md` |
| Funciona sem câmera, por mouse, teclado e varredura | `app/entrada/*` | `atlas demo silabas --entrada teclado` |
| O caminho da câmera funciona | `app/entrada/mao.py` | `atlas demo silabas --entrada mao-simulada`; `pytest tests/test_mao.py` |
| O vídeo nunca sai do computador | `app/entrada/camera.py` | `pytest tests/test_privacidade.py` |

3. As limitações conhecidas, sem enfeite.

### 11.4 `docs/saida-exemplo/`

Gerada por `scripts/gerar_saida_exemplo.sh` (roda `docker compose run --rm demo` e copia o resultado): `relatorio.md`, as capturas PNG, `tentativas.json` e uma transcrição de uma sessão do agente. Commitada, para que a avaliadora tenha evidências mesmo que não consiga executar nada.

### 11.5 `scripts/verificar_readme.sh`

Clona o repositório numa pasta temporária (de `origin`, ou do diretório atual se não houver rede) e **executa cada comando do Caminho A e do Caminho B**, conferindo as saídas esperadas com `grep` (`RESULTADO: pronto`, `passed`, existência de `saida/relatorio.md`, resposta JSON do agente). Falha se qualquer passo falhar. **Rode-o antes de cada tag.**

## 12. Marcos (execute em ordem; push e atualização do PROGRESSO.md ao fim de cada um)

**M0 — Repositório (≤ 25 min)**

- [ ] `gh auth status`; depois `gh repo view REPO` para confirmar acesso de escrita. `docker --version` e `docker info`: se o Docker não estiver rodando, pare e peça que eu o inicie.
- [ ] O repositório **já existe e é privado**: não o crie nem mude a visibilidade. `git init -b main`, `git remote add origin https://github.com/REPO.git`, `git fetch origin`; se houver commits remotos, `git pull origin main --rebase` antes do primeiro push.
- [ ] Estrutura da seção 4, `.gitignore`, `pyproject.toml` (com o script `atlas`), `requirements*.txt`, `CLAUDE.md`, `docs/*`, `README.md` (rascunho), `LICENSE`, `CREDITOS.md`.
- [ ] `ci.yml`: job `testes` (ubuntu, Python 3.11, `apt-get install -y libegl1 libgl1 libxkbcommon0 libdbus-1-3 libfontconfig1`, `QT_QPA_PLATFORM=offscreen`, `ruff`, `pytest`) e job `docker` (`docker compose build`, `verificar`, `demo`, `teste`; sobe `saida/` como artefato).
- **Aceite:** código no repositório privado com o CI verde.

**M1 — Esqueleto que roda em Docker, empacota e abre a câmera (≤ 90 min; o maior risco)**

- [ ] Janela principal, tema, fonte, navegação Início → Matérias → Trilhas e uma atividade "Teste de câmera" (cursor da mão + estado da pinça).
- [ ] `atlas verificar` completo e `atlas demo` mínimo (gera 1 captura da tela inicial e `relatorio.md`).
- [ ] `Dockerfile`, `docker-compose.yml`, `.dockerignore`. **`docker compose run --rm verificar` e `... demo` precisam funcionar numa build limpa.**
- [ ] `baixar_modelo.py` e `baixar_fonte.py`; commitar modelo e fonte.
- [ ] `empacotamento/atlas.spec` (onedir; `collect_data_files('mediapipe')`; `assets/` e `conteudo/` como datas; no macOS, `NSCameraUsageDescription` = "O Atlas usa a câmera só para ver a mão da criança. Nenhuma imagem é salva ou enviada." e `NSMicrophoneUsageDescription`).
- [ ] `release.yml` (tag `v*`): matriz `windows-latest` e `macos-latest` com PyInstaller, zips `Atlas-windows.zip` e `Atlas-macos.zip`; job que publica a imagem no GHCR (`IMAGEM:<tag>` e `latest`, `linux/amd64`; `arm64` se o build passar). Crie a tag `v0.0.1` e confirme a Release e a imagem.
- [ ] Peça para eu testar a câmera **uma vez** rodando `python -m app.main` (parada única).
- **Aceite:** `docker compose run --rm verificar` imprime `RESULTADO: pronto`; a Release tem os dois zips; o cursor segue a minha mão.

**M2 — Perfis e camada de entrada (≤ 60 min)**

- [ ] `perfis.py` com combinação + testes; `atlas perfis`; `tema.py`.
- [ ] `eventos.py`, `ponteiro.py`, `teclado.py`, `varredura.py`, `mao.py` (testes de One Euro, histerese, permanência, área ativa), `mao_simulada.py` + `simulacao_mao.json`, `camera.py` com fallback, `cursor.py`, `anuncio.py`.
- [ ] Área do adulto: criar aluno (apelido + avatar) e escolher perfis.
- **Aceite:** testes verdes; capturas do protótipo com os perfis padrão, TEA e baixa visão (geradas por `atlas demo`) revisadas por você.

**M3 — Núcleo das atividades e modos headless (≤ 60 min)**

- [ ] `AtividadeBase` (3 momentos, Agora/Depois, Pausa, pistas, ajuste de nível, `estado()`), `registro.py`, `audio.py` (WAV + backend nulo + legenda).
- [ ] `headless/demo.py` completo (executor de roteiros, capturas, `relatorio.md`, `tentativas.json`, `eventos.jsonl`, `audio.log`) e `headless/agente.py` (protocolo da 7.4).
- [ ] `gerar_audio.py` (provedores `google` e `espeak`) e `validar_conteudo.py`; gere e commite os WAV.
- **Aceite:** testes de `progresso.py`, `erros.py` e do protocolo do agente verdes.

**M4 — Ímã das Sílabas (≤ 75 min)**

- [ ] Lógica pura, cena, níveis 1–4, 15 figuras SVG, áudios, erros, `estado()` e `demo.py`.
- **Aceite:** pytest-qt completa BOLA por mouse, teclado, clique-clique e varredura; `docker compose run --rm demo` produz `relatorio.md` e capturas; o agente completa BOLA via JSON; capturas nos perfis padrão, TEA e dislexia.
- [ ] Tag `v0.1.0`.

**M5 — Mesa de Quantidades (≤ 60 min)**

- [ ] Os 4 modos, 3 conjuntos de objetos, erros, `estado()` e `demo.py`.
- **Aceite:** testes da lógica, demo e agente funcionando em Docker.

**M6 — Pizza de Frações (≤ 60 min)**

- [ ] Corte, pegar/devolver fatias, soma de mesmo denominador, desafio, alternativa em barra, erros, `estado()` e `demo.py`.
- **Aceite:** testes da lógica, demo e agente funcionando em Docker.
- [ ] Tag `v0.2.0`.

**M7 — Painel e interface remota (P1, ≤ 45 min)**

- [ ] `seed_demo.py`, painel, recomendações e `atlas demo painel`.
- [ ] `docker/gui.sh` + serviço `gui` (noVNC). Se não funcionar em 30 min, corte e registre.
- **Aceite:** captura do painel; `docker compose up gui` mostra o software em `http://localhost:6080/vnc.html`.

**M8 — Entrega (≤ 45 min)**

- [ ] `README.md` final conforme a seção 11, `docs/AVALIACAO.md`, `docs/ARQUITETURA.md`, `scripts/gerar_saida_exemplo.sh` e `docs/saida-exemplo/` commitada.
- [ ] Rode `scripts/verificar_readme.sh` **num clone limpo** e corrija o README até passar sem nenhuma intervenção.
- [ ] Tag `v1.0.0`; confirme a Release (zips) e a imagem no GHCR; teste `docker pull IMAGEM:latest && docker run --rm IMAGEM:latest verificar`.
- [ ] **Não torne o repositório nem o pacote públicos por conta própria.** Avise que, antes do envio, eu preciso: (a) mudar o repositório para público (Settings → General → Danger Zone → Change visibility) e (b) tornar o pacote `atlas` do GHCR público (perfil → Packages → atlas → Package settings → Change visibility). Depois disso, teste o `git clone` e o `docker pull` **sem estar logado** (por exemplo, numa aba anônima ou com `docker logout ghcr.io`).
- **Aceite:** CI verde, `verificar_readme.sh` passando, Release `v1.0.0` com os zips e a imagem, `PROGRESSO.md` completo.

Se o tempo apertar, a ordem de corte é: M7 → desafio da Pizza → modo Par/ímpar → nível 4 do Ímã. **Nunca corte** `atlas verificar`, `atlas demo`, `atlas agente`, o Docker, o README da avaliadora, a entrada sem câmera, os perfis ou a Pausa.

## 13. Requisitos de desempenho e robustez

- A interface roda a 60 fps durante as atividades; nada pesado na thread principal (câmera e MediaPipe na `QThread`).
- Latência da mão até o cursor abaixo de 100 ms em um notebook comum.
- O app abre em menos de 5 s (onedir); `mediapipe` e `cv2` só são importados quando a câmera liga.
- `atlas verificar` termina em menos de 5 s; `atlas demo todas` em menos de 60 s; `docker compose build` em menos de 10 min em máquina comum.
- Os modos headless **não dependem de rede, de áudio, de câmera nem de tela** e devem ser determinísticos (semente fixa nas bolhas e nos distratores quando `--saida` é usado), para que as saídas sejam reproduzíveis.
- Figuras SVG renderizadas uma vez por tamanho e mantidas em cache (`QPixmapCache`).

## 14. Fora do escopo

Login, servidor, nuvem, interface web, IA generativa conversando com a criança, analytics, anúncios, gravação ou envio de imagem ou áudio e qualquer chamada de rede em tempo de execução.

## 15. Ao terminar cada marco

Responda em até 5 linhas: o que ficou pronto, o link do commit ou da Release, o que eu preciso testar manualmente (se houver) e a decisão mais importante registrada.

`````
