"""
Medidor de custo — roda o benchmark completo contando os tokens reais
consumidos no gpt-4o-mini e calcula o custo em dólares.

Usa o contador oficial do LangChain (get_openai_callback), que captura os
tokens de todas as chamadas ao LLM feitas dentro do grafo.

Obs: aqui NÃO salvamos traces (é só medição), para não misturar com os 20
traces do benchmark.

Rodar:  ./.venv/bin/python avaliacao/custo.py
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).parent.parent / "orquestracao"))
from orquestrador import construir_grafo  # noqa: E402
from langchain_community.callbacks import get_openai_callback  # noqa: E402

from perguntas import PERGUNTAS  # noqa: E402

AVALIACAO_DIR = Path(__file__).parent

# Preços oficiais do gpt-4o-mini (dólares por 1 milhão de tokens).
PRECO_ENTRADA = 0.15   # input
PRECO_SAIDA = 0.60     # output


def main():
    app = construir_grafo()

    print(f"Rodando {len(PERGUNTAS)} perguntas para medir o consumo...\n")
    # O contador soma os tokens de TODAS as chamadas ao LLM feitas aqui dentro.
    with get_openai_callback() as contador:
        for item in PERGUNTAS:
            app.invoke({"pergunta": item["pergunta"]})
            print(f"  ok  {item['id']}")

    tokens_entrada = contador.prompt_tokens
    tokens_saida = contador.completion_tokens
    total_tokens = contador.total_tokens

    # Custo = (tokens / 1 milhão) * preço por milhão, para entrada e saída.
    custo_entrada = tokens_entrada / 1_000_000 * PRECO_ENTRADA
    custo_saida = tokens_saida / 1_000_000 * PRECO_SAIDA
    custo_total = custo_entrada + custo_saida

    relatorio = f"""# Custo do benchmark — gpt-4o-mini

Medição real do consumo para rodar o benchmark completo ({len(PERGUNTAS)} perguntas),
usando o contador de tokens do LangChain.

## Consumo

| Item | Tokens | Preço (US$/1M) | Custo (US$) |
|------|-------:|---------------:|------------:|
| Entrada (input)  | {tokens_entrada:,} | {PRECO_ENTRADA:.2f} | {custo_entrada:.6f} |
| Saída (output)   | {tokens_saida:,} | {PRECO_SAIDA:.2f} | {custo_saida:.6f} |
| **Total**        | **{total_tokens:,}** | — | **{custo_total:.6f}** |

## Resumo

- Custo total do benchmark completo: **US$ {custo_total:.4f}** (~R$ {custo_total * 5.4:.4f}).
- Custo médio por pergunta: **US$ {custo_total / len(PERGUNTAS):.6f}**.
- Embeddings e busca web (Tavily) não entram aqui: rodam localmente / no plano gratuito.

> Números medidos, não estimados — reproduza com `./.venv/bin/python avaliacao/custo.py`.
"""

    saida = AVALIACAO_DIR / "custo.md"
    saida.write_text(relatorio, encoding="utf-8")

    print(f"\n=== Custo do benchmark ===")
    print(f"  Tokens: {tokens_entrada:,} entrada + {tokens_saida:,} saída = {total_tokens:,}")
    print(f"  Custo total: US$ {custo_total:.6f}")
    print(f"\n✓ Relatório salvo em {saida}")


if __name__ == "__main__":
    main()
