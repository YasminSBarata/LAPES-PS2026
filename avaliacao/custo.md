# Custo do benchmark — gpt-4o-mini

Medição real do consumo para rodar o benchmark completo (20 perguntas),
usando o contador de tokens do LangChain.

## Consumo

| Item | Tokens | Preço (US$/1M) | Custo (US$) |
|------|-------:|---------------:|------------:|
| Entrada (input)  | 25,991 | 0.15 | 0.003899 |
| Saída (output)   | 3,233 | 0.60 | 0.001940 |
| **Total**        | **29,224** | — | **0.005838** |

## Resumo

- Custo total do benchmark completo: **US$ 0.0058** (~R$ 0.0315).
- Custo médio por pergunta: **US$ 0.000292**.
- Embeddings e busca web (Tavily) não entram aqui: rodam localmente / no plano gratuito.

> Números medidos, não estimados — reproduza com `./.venv/bin/python avaliacao/custo.py`.
