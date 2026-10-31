# Avaliação do Atlas

## O problema e a resposta

Numa turma de alfabetização convivem crianças com TEA, TDAH, dislexia, baixa visão, daltonismo e dificuldade motora. Hoje, para incluir cada uma, o professor precisa adaptar a mesma atividade várias vezes, ou a criança faz outra coisa, longe da turma.
O Atlas inverte isso: **uma atividade, vários perfis**. O professor marca os perfis do aluno uma vez (só apelido e um bicho, sem dados pessoais) e cada atividade se ajusta sozinha: quantidade de itens, velocidade, tamanho, contraste, espaçamento das letras, forma de entrada.
A criança joga com o corpo (pinça na frente da câmera), com toque, mouse, teclado ou varredura com uma tecla. O roteiro é sempre o mesmo (explicação, atividade, fim), o erro é neutro e vem com pistas graduais.
Cada resposta vira um registro com o tipo de erro (por exemplo, `par_surdo_sonoro`), que vira uma sugestão concreta para o professor.

## Afirmação → evidência

| Afirmação | Onde está | Como verificar |
| --- | --- | --- |
| Os instaladores funcionam e incluem o detector da mão | `empacotamento/atlas.spec`, `.github/workflows/release.yml` | Release: `Atlas.exe verificar --completo` termina com `OK  detector da mao` e `RESULTADO: pronto` |
| O app roda sem tela, sem webcam e sem áudio | `app/headless/`, `Dockerfile` | `docker compose run --rm verificar` termina com `RESULTADO: pronto` |
| Perfis combinam pela opção mais acessível | `app/nucleo/perfis.py` | `atlas perfis --combinar tea,dislexia`; `pytest tests/test_perfis.py` |
| A mesma atividade muda com o perfil (itens, escala, contraste, espaçamento, sílabas alternadas) | `app/nucleo/tema.py`, `app/atividades/silabas/tela.py` | `atlas demo silabas --perfil baixa_visao` e `--perfil dislexia`; `pytest tests/test_silabas_tela.py` |
| Funciona sem câmera, por mouse, clique-clique, teclado e varredura | `app/entrada/ponteiro.py`, `teclado.py`, `varredura.py` | `atlas demo silabas --entrada teclado`; `pytest tests/test_silabas_tela.py -k bola` |
| O caminho da câmera funciona (filtro, pinça com histerese, permanência) | `app/entrada/mao.py`, `mao_entrada.py`, `mao_simulada.py` | `atlas demo silabas --entrada mao-simulada`; `pytest tests/test_mao.py tests/test_entrada_pura.py` |
| As atividades não sabem qual entrada foi usada | `app/nucleo/eventos.py` (barramento) | `pytest tests/test_treino.py -k cada_entrada` (mesma atividade, 5 entradas) |
| Roteiro fixo em 3 momentos, faixa Agora/Depois, Pausa sempre visível | `app/atividades/base.py` | Capturas `captura-07`, `08`, `11` e `13` em `docs/saida-exemplo/`; `pytest tests/test_base.py` |
| Erro neutro com pistas graduais (repetir, realçar, modelo) | `app/nucleo/progresso.py`, `app/atividades/base.py` | `saida/relatorio.md`, colunas "Tipo de erro" e "Pista"; `pytest tests/test_progresso_erros.py` |
| Ajuste de nível: 4 acertos oferecem desafio, 2 modelos voltam um nível, professor trava | `app/nucleo/progresso.py` | `pytest tests/test_base.py -k nivel` |
| O erro é classificado e vira recomendação para o professor | `app/nucleo/erros.py`, `conteudo/recomendacoes.json` | `saida/tentativas.json`, campo `tipo_erro`; `pytest tests/test_progresso_erros.py` |
| Cada resposta é registrada com os campos pedidos | `app/nucleo/registro.py` | `saida/tentativas.json`; `pytest tests/test_registro.py` |
| Matemática com objetos: montar, comparar (um a um, sobra marcada) e contas até 20 | `app/atividades/quantidades/` | `atlas demo quantidades`; `pytest tests/test_quantidades_logica.py tests/test_quantidades_tela.py` |
| Frações: montar, somar com mesmo denominador, operar com 2 ou 3 pratos (soma e subtração) e impróprias; somar denominadores e trocar a operação são detectados | `app/atividades/pizza/`, `app/nucleo/erros.py` (`classificar_fracao`) | `atlas demo pizza`; `pytest tests/test_pizza_logica.py tests/test_pizza_tela.py` |
| Valor posicional com jogo dourado: o número é montado por ordem; trocar as ordens e contar uma peça a mais ou a menos são detectados | `app/atividades/dourado/`, `app/nucleo/erros.py` (`classificar_dourado`) | `atlas demo dourado`; `pytest tests/test_dourado.py` |
| Tabuada com tempo: +1 no monstrinho certo, -1 no errado; erro de somar em vez de multiplicar e de vizinho na tabuada detectados | `app/atividades/tabuada/`, `app/nucleo/erros.py` | `atlas demo tabuada --entrada mao-simulada`; `pytest tests/test_tabuada.py` |
| Gesto de arminha: indicador esticado e os outros dedos dobrados; com o dedão levantado a arminha engatilha, e abaixar o dedão atira na mira de um instante antes | `app/entrada/mao.py` (`eh_arminha`, `razao_gatilho`, `DetectorGatilho`), `app/entrada/mao_entrada.py` | `pytest tests/test_tabuada.py -k "arminha or dedao or tiro or pinca"` |
| A câmera pode ser desligada em qualquer atividade sem perder mouse e teclado | `app/atividades/base.py` (`botao_camera`) | `pytest tests/test_base.py -k camera`; captura `tabuada-camera-desligada` |
| O professor vê quem domina, quem progride e quem precisa de apoio, com uma sugestão concreta | `app/nucleo/painel.py`, `app/telas/painel.py` | `atlas demo painel`; `pytest tests/test_painel.py`; captura `captura-53-painel.png` em `docs/saida-exemplo/` |
| Uma IA consegue jogar a atividade sem tela | `app/headless/agente.py` | `echo '{"acao":"estado"}' \| docker compose run --rm -T agente`; `docs/saida-exemplo/agente-respostas.jsonl` |
| O vídeo nunca sai do computador; nada de rede em execução | `app/entrada/camera.py` | `pytest tests/test_privacidade.py` (proíbe `imwrite` e módulos de rede em `app/`) |
| OpenCV e MediaPipe são opcionais | `app/entrada/camera.py` | `pytest tests/test_dependencias.py`; o job `testes` do CI roda sem eles |
| Contraste WCAG AA em todas as combinações de texto | `app/nucleo/tema.py` | `pytest tests/test_tema.py` |
| Todo controle tem nome acessível em pt-BR | telas em `app/telas/` e `app/atividades/` | `pytest tests/test_telas.py -k acessivel` |
| Conteúdo consistente (sílabas formam a palavra, figura e áudio existem) | `conteudo/palavras.json`, `scripts/validar_conteudo.py` | `python scripts/validar_conteudo.py` imprime `conteudo ok` |

Todas as capturas e saídas de `docs/saida-exemplo/` foram geradas pelo app real com `scripts/gerar_saida_exemplo.sh` (Docker). O aluno "Bia (exemplo)" das capturas é fictício e está rotulado assim.

## Limitações conhecidas

- **Matemática:** a Mesa de Quantidades está pronta sem o modo Par/ímpar; na Pizza de Frações o corte é sorteado (a criança não o escolhe), os pratos de uma conta têm sempre o mesmo denominador e a resposta é escolhida em cartões (as fatias não são arrastadas para um prato de resultado).
- **Interface remota no navegador (noVNC):** não implementada; use os instaladores, o Docker sem tela ou o Python.
- **Câmera real:** não é testável sem webcam. Foi testada manualmente por uma pessoa do time num notebook com Windows; em avaliação automática, vale a mão simulada.
- **Voz:** só no português (a letra ou a sílaba pega e a palavra pronta); instruções e retornos aparecem na legenda. Sintética (eSpeak NG), compreensível mas robótica. Com credencial do Google Cloud, `scripts/gerar_audio.py --provedor google --refazer` troca todos os WAV.
- **Áudio no Docker:** não há som; o `audio.log` registra o que tocaria.
- **Baixa visão em janela pequena:** em 1280 x 720 a área da atividade fica pequena, porque a instrução e a legenda grandes ocupam duas linhas. Em tela cheia (1366 x 768 ou maior) isso não acontece.
- **Instaladores:** não são assinados (o Windows e o macOS pedem confirmação na primeira abertura) e o de macOS é só para Apple Silicon. A Release testa cada executável com `verificar --completo` e `demo silabas` antes de publicar.
- **Cegueira (parcial):** uso por teclado e leitor de tela pelos nomes acessíveis; as instruções não são lidas em voz (decisão do time: voz só para letra, sílaba e palavra).
