# CLAUDE.md — Atlas

Memória do projeto. Releia este arquivo se perder o contexto. A especificação completa está no prompt original (seções 1–12); o resumo está em `docs/PROGRESSO.md`.

## Modo de trabalho

- **Trabalhamos por etapas, com aprovação.** Ao fim de cada etapa: atualizar este arquivo e `docs/PROGRESSO.md`, fazer push, resumir em até 5 linhas e **parar até o usuário aprovar a próxima etapa**.
- Ciclo de cada tarefa: implementar → `ruff check .` → `pytest` → corrigir → commit. Nunca deixar `main` quebrado.
- Commits pequenos, padrão Conventional Commits em pt-BR, por exemplo `feat(silabas): ...` ou `fix(camera): ...`. Nunca usar `--force` nem reescrever histórico publicado.
- Decisões ambíguas: escolher a opção mais simples e registrar em `docs/DECISOES.md` (data | decisão | motivo).
- Nunca commitar `.env`, credenciais, `.venv/`, `build/` ou `dist/`.

## Comandos

```bash
py -3.11 -m venv .venv                       # Python 3.11 (o mediapipe exige 3.9–3.12)
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m app.main             # rodar o app (a partir da Etapa 1a)
.venv/Scripts/ruff check .
.venv/Scripts/python -m pytest               # roda em offscreen (tests/conftest.py)
# empacotar: Etapa 1b (PyInstaller onedir, empacotamento/atlas.spec)
```

## Estrutura

```text
app/          main.py, nucleo/, entrada/, telas/, atividades/{silabas,quantidades,pizza}/
conteudo/     palavras.json, objetos.json, recomendacoes.json, manifesto_audio.json
assets/       audio/, figuras/, fontes/, modelos/
scripts/      baixar_modelo.py, baixar_fonte.py, gerar_audio.py, validar_conteudo.py, capturas.py, seed_demo.py
tests/        pytest + pytest-qt (offscreen)
empacotamento/ atlas.spec, Info.plist.extra
docs/         DECISOES.md, PROGRESSO.md, capturas/
```

## Convenções

- Código, nomes e textos em pt-BR, sem acentos nos identificadores.
- As atividades só escutam o barramento `app/nucleo/eventos.py` e nunca sabem qual entrada foi usada.
- Toda regra fica em funções puras testadas (`mao.py`, `erros.py`, `progresso.py`, `logica.py` de cada atividade). Os widgets só desenham e repassam eventos.
- Frases mostradas à criança ficam em `conteudo/`, nunca no código.
- Interface: PySide6 Widgets + QGraphicsView. Não usar QML.
- Nenhuma chamada de rede e nenhum `cv2.imwrite` em `app/` (garantido por `tests/test_privacidade.py`).
- Design: no máximo 3 cores por tela; fundo `#F6F3EC`, texto `#2A2A2A`, primária `#2F6F6A`, destaque `#D9A441`, apoio `#8FA9C7`. Sem gradiente, sem sombra, sem vermelho para erro, raio máximo de 12 px, alvos de pelo menos 64 px.

## Estado das etapas

| Etapa | Estado |
| --- | --- |
| 0. Repositório | concluída |
| 1a. Esqueleto + câmera | pendente |
| 1b. Empacotamento + Release | pendente |
| 2. Perfis e entrada | pendente |
| 3. Núcleo das atividades | pendente |
| 4. Ímã das Sílabas | pendente |
| 5. Mesa de Quantidades | pendente |
| 6. Pizza de Frações | pendente |
| 7. Painel do professor | pendente |
| 8. Entrega | pendente |
