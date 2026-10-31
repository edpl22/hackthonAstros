# Avaliação do Atlas

## O problema e a resposta

Numa turma de alfabetização convivem crianças com TEA, TDAH, dislexia, baixa visão, daltonismo e dificuldade motora. Hoje, para incluir cada uma, o professor precisa adaptar a mesma atividade várias vezes, ou a criança faz outra coisa, longe da turma.
O Atlas inverte isso: **uma atividade, vários perfis**. O professor marca os perfis do aluno uma vez (só apelido e um bicho, sem dados pessoais) e cada atividade se ajusta sozinha: quantidade de itens, velocidade, tamanho, contraste, espaçamento das letras, áudio automático, forma de entrada.
A criança joga com o corpo (pinça na frente da câmera), com toque, mouse, teclado ou varredura com uma tecla. O roteiro é sempre o mesmo (explicação, atividade, fim), o erro é neutro e vem com pistas graduais.
Cada resposta vira um registro com o tipo de erro (por exemplo, `par_surdo_sonoro`), que vira uma sugestão concreta para o professor.

## Afirmação → evidência

| Afirmação | Onde está | Como verificar |
| --- | --- | --- |
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
| Uma IA consegue jogar a atividade sem tela | `app/headless/agente.py` | `echo '{"acao":"estado"}' \| docker compose run --rm -T agente`; `docs/saida-exemplo/agente-respostas.jsonl` |
| O vídeo nunca sai do computador; nada de rede em execução | `app/entrada/camera.py` | `pytest tests/test_privacidade.py` (proíbe `imwrite` e módulos de rede em `app/`) |
| OpenCV e MediaPipe são opcionais | `app/entrada/camera.py` | `pytest tests/test_dependencias.py`; o job `testes` do CI roda sem eles |
| Contraste WCAG AA em todas as combinações de texto | `app/nucleo/tema.py` | `pytest tests/test_tema.py` |
| Todo controle tem nome acessível em pt-BR | telas em `app/telas/` e `app/atividades/` | `pytest tests/test_telas.py -k acessivel` |
| Conteúdo consistente (sílabas formam a palavra, figura e áudio existem) | `conteudo/palavras.json`, `scripts/validar_conteudo.py` | `python scripts/validar_conteudo.py` imprime `conteudo ok` |

Todas as capturas e saídas de `docs/saida-exemplo/` foram geradas pelo app real com `scripts/gerar_saida_exemplo.sh` (Docker). O aluno "Bia (exemplo)" das capturas é fictício e está rotulado assim.

## Limitações conhecidas

- **Matemática ainda em construção:** a Mesa de Quantidades e a Pizza de Frações ainda não existem como atividades. Os classificadores de erro delas (`um_a_mais_ou_menos`, `somou_denominadores` etc.) já estão prontos e testados em `app/nucleo/erros.py`.
- **Painel do professor ainda não existe:** os dados que ele vai mostrar já são registrados em `tentativas`.
- **Câmera real:** não é testável sem webcam. Foi testada manualmente por uma pessoa do time num notebook com Windows; em avaliação automática, vale a mão simulada.
- **Voz:** sintética (eSpeak NG), compreensível mas robótica. Com credencial do Google Cloud, `scripts/gerar_audio.py --provedor google --refazer` troca todos os WAV.
- **Áudio no Docker:** não há som; o `audio.log` registra o que tocaria.
- **Baixa visão em janela pequena:** em 1280 x 720 a área da atividade fica pequena, porque a instrução e a legenda grandes ocupam duas linhas. Em tela cheia (1366 x 768 ou maior) isso não acontece.
- **Instaladores (Windows e macOS) e imagem pronta no GHCR:** ainda não publicados; por enquanto, Docker com `build` ou Python.
- **Cegueira (parcial):** áudio automático e uso por teclado; ainda não há descrição em áudio de cada item focado.
