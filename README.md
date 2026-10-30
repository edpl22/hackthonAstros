# Atlas

> Rascunho. O README final sai na Etapa 8 (entrega).

Software desktop de português e matemática básica, da Educação Infantil ao 4º ano. A criança aprende com o corpo: mão na câmera, toque, mouse ou teclado. **A mesma atividade se ajusta ao perfil de cada aluno** (TEA, TDAH, dislexia, baixa visão, daltonismo, dificuldade motora), sem que o professor precise refazê-la.

É a nossa resposta ao Desafio 01 da Teachy: *"Como podemos ajudar professores, escolas e família a fazerem com que todos os alunos aprendam o mesmo conteúdo, junto com a turma?"*

## Rodar a partir do código

Requer Python 3.11.

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-camera.txt
pip install --no-deps .
atlas              # interface gráfica
atlas verificar    # confere o ambiente
atlas demo         # capturas e relatório em ./saida
```

Sem webcam, `requirements-camera.txt` é opcional: o Atlas usa mouse, toque e teclado.

## Docker

```bash
docker compose build
docker compose run --rm verificar
docker compose run --rm demo
docker compose run --rm teste
```

## Testes

```bash
ruff check .
pytest
```

## Privacidade

O Atlas não faz nenhuma chamada de rede enquanto está rodando. A câmera só liga dentro de uma atividade e nenhuma imagem é salva ou enviada.
