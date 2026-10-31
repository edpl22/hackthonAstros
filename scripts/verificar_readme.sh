#!/usr/bin/env bash
# Executa os comandos do README (Caminho A, Docker, e Caminho B, Python) a partir de um clone
# limpo e confere as saídas esperadas. Falha no primeiro passo que não der o resultado esperado.
#
# Uso: bash scripts/verificar_readme.sh [origem]
#   origem: URL ou pasta do repositório (padrão: o remoto "origin"; sem rede, esta pasta).
#   PULAR_DOCKER=1 ou PULAR_PYTHON=1 pulam um dos caminhos.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")/.." && pwd)"
ORIGEM="${1:-$(git -C "$AQUI" remote get-url origin 2>/dev/null || echo "$AQUI")}"
TMP="$(mktemp -d)"
CLONE="$TMP/hackthonAstros"
trap 'rm -rf "$TMP"' EXIT

passo() { printf '\n== %s\n' "$*"; }
ok() { printf 'OK   %s\n' "$*"; }
falha() { printf 'FALHA %s\n' "$*"; exit 1; }

passo "git clone $ORIGEM"
git clone -q "$ORIGEM" "$CLONE" || git clone -q "$AQUI" "$CLONE" || falha "git clone"
cd "$CLONE"
ok "clone em $CLONE"

if [ "${PULAR_DOCKER:-0}" != "1" ]; then
  passo "Caminho A: docker compose build"
  docker compose build >"$TMP/build.log" 2>&1 || { tail -20 "$TMP/build.log"; falha "build"; }
  ok "imagem construida"

  passo "Caminho A: docker compose run --rm verificar"
  docker compose run --rm verificar | tee "$TMP/verificar.txt"
  grep -q "RESULTADO: pronto" "$TMP/verificar.txt" || falha "verificar sem 'RESULTADO: pronto'"
  ok "RESULTADO: pronto"

  passo "Caminho A: docker compose run --rm demo"
  docker compose run --rm demo | tail -3
  for arquivo in relatorio.md tentativas.json eventos.jsonl audio.log captura-01-inicio.png; do
    test -s "saida/$arquivo" || falha "saida/$arquivo nao foi gerado"
  done
  ok "saida/ com relatorio.md, capturas, tentativas.json, eventos.jsonl e audio.log"

  passo "Caminho A: docker compose run --rm teste"
  docker compose run --rm teste | tail -2 | tee "$TMP/teste.txt"
  grep -q "passed" "$TMP/teste.txt" || falha "testes"
  grep -q "failed" "$TMP/teste.txt" && falha "algum teste falhou"
  ok "testes passaram"

  passo "Caminho A: agente por JSON Lines"
  echo '{"acao":"estado"}' | docker compose run --rm -T agente | tee "$TMP/agente.txt"
  grep -q '"pronto": true' "$TMP/agente.txt" || falha "agente nao respondeu 'pronto'"
  grep -q '"palavra": "BOLA"' "$TMP/agente.txt" || falha "agente sem o estado de BOLA"
  ok "agente respondeu com o estado"
fi

if [ "${PULAR_PYTHON:-0}" != "1" ]; then
  passo "Caminho B: Python 3.11 sem Docker"
  if command -v python3.11 >/dev/null 2>&1; then
    PY=python3.11
  elif command -v py >/dev/null 2>&1; then
    PY="py -3.11"
  else
    falha "Python 3.11 nao encontrado"
  fi
  $PY -m venv .venv
  if [ -f .venv/bin/activate ]; then . .venv/bin/activate; else . .venv/Scripts/activate; fi
  pip install -q -r requirements.txt
  pip install -q .
  export QT_QPA_PLATFORM=offscreen ATLAS_AUDIO=nulo ATLAS_DADOS="$TMP/dados"
  atlas verificar | tee "$TMP/verificar-b.txt"
  grep -q "RESULTADO: pronto" "$TMP/verificar-b.txt" || falha "atlas verificar"
  rm -rf saida
  atlas demo todas --saida ./saida | tail -3
  test -s saida/relatorio.md || falha "atlas demo"
  echo '{"acao":"estado"}' | atlas agente silabas | grep -q '"pronto": true' || falha "atlas agente"
  atlas perfis --combinar tea,dislexia | grep -q '"combinacao"' || falha "atlas perfis"
  ok "verificar, demo, agente e perfis pelo Python"
fi

printf '\nREADME VERIFICADO: todos os passos deram o resultado esperado.\n'
