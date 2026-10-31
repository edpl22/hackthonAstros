#!/usr/bin/env bash
# Gera docs/saida-exemplo/ com saídas reais do Atlas, rodando dentro do Docker:
#   - o demo completo (capturas PNG, relatorio.md, tentativas.json, eventos.jsonl, audio.log);
#   - uma sessão do agente jogando BOLA por JSON Lines (pedidos e respostas).
# Uso: bash scripts/gerar_saida_exemplo.sh   (na raiz do repositório)
set -euo pipefail
cd "$(dirname "$0")/.."

DESTINO=docs/saida-exemplo
docker compose build verificar

rm -rf saida "$DESTINO"
mkdir -p saida "$DESTINO"
docker compose run --rm demo
cp saida/* "$DESTINO"/

# Sessão do agente: o mesmo jogo que o README mostra (com um erro proposital).
PEDIDOS='{"acao":"estado"}
{"acao":"proximo"}
{"acao":"pegar","id":"bolha-la-1"}
{"acao":"soltar","alvo":"caixa-1"}
{"acao":"pegar","id":"bolha-bo-3"}
{"acao":"soltar","alvo":"caixa-1"}
{"acao":"pegar","id":"bolha-la-1"}
{"acao":"soltar","alvo":"caixa-2"}
{"acao":"sair"}'
echo "$PEDIDOS" > "$DESTINO/agente-pedidos.jsonl"
echo "$PEDIDOS" | docker compose run --rm -T agente > "$DESTINO/agente-respostas.jsonl"

echo "saida de exemplo em $DESTINO:"
ls "$DESTINO"
