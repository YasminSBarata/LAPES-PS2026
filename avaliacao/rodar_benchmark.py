"""
Runner do benchmark — roda as 20 perguntas pelo orquestrador e avalia.

O que ele faz:
  1. Roda cada pergunta pelo grafo (isso já salva o trace JSON em traces/).
  2. Confere AUTOMATICAMENTE o roteamento: a pergunta foi pra fonte certa?
     (corpus → rota "rag"; fallback → rota "web")
  3. Salva os resultados em avaliacao/resultados.json (dados completos)
     e avaliacao/resultados.md (tabela legível).
  4. A CORREÇÃO da resposta (certo/errado) é feita MANUALMENTE depois,
     lendo cada resposta gerada.

Rodar:  ./.venv/bin/python avaliacao/rodar_benchmark.py
"""

import sys
import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# O orquestrador está na pasta orquestracao/ — colocamos ela no caminho de import.
sys.path.insert(0, str(Path(__file__).parent.parent / "orquestracao"))
from orquestrador import construir_grafo, salvar_trace  # noqa: E402

from perguntas import PERGUNTAS  # noqa: E402

AVALIACAO_DIR = Path(__file__).parent


def fonte_recuperada(estado: dict) -> str:
    """Descreve de onde veio a resposta, para a coluna 'fonte' da tabela."""
    if estado.get("origem") == "web":
        return "web (Tavily)"
    fontes = sorted({t["fonte"] for t in estado.get("trechos", [])})
    return ", ".join(fontes)


def main():
    app = construir_grafo()
    resultados = []

    print(f"\nRodando {len(PERGUNTAS)} perguntas...\n")
    for item in PERGUNTAS:
        estado = app.invoke({"pergunta": item["pergunta"]})
        salvar_trace(estado)  # gera o trace JSON exigido

        rota = estado.get("rota")
        rota_esperada = "rag" if item["tipo"] == "corpus" else "web"
        roteamento_ok = (rota == rota_esperada)

        resultados.append({
            "id": item["id"],
            "conjunto": item["conjunto"],
            "tipo_esperado": item["tipo"],
            "pergunta": item["pergunta"],
            "esperado": item["esperado"],
            "rota": rota,
            "roteamento_ok": roteamento_ok,
            "fonte": fonte_recuperada(estado),
            "distancia_min": round(estado.get("distancia_min", 0), 2),
            "resposta": estado.get("resposta"),
            "correcao": None,  # preenchido MANUALMENTE depois (True/False)
        })

        marca = "✓" if roteamento_ok else "✗"
        print(f"  [{marca}] {item['id']:>3} rota={rota:<3} (esperado {rota_esperada})  {item['pergunta'][:50]}")

    # --- Acurácia de roteamento (automática) ---
    def acuracia(subset):
        if not subset:
            return 0.0
        return sum(r["roteamento_ok"] for r in subset) / len(subset)

    teste = [r for r in resultados if r["conjunto"] == "teste"]
    validacao = [r for r in resultados if r["conjunto"] == "validacao"]

    print("\n=== Acurácia de roteamento ===")
    print(f"  Geral:     {acuracia(resultados):.0%} ({sum(r['roteamento_ok'] for r in resultados)}/{len(resultados)})")
    print(f"  Validação: {acuracia(validacao):.0%} ({sum(r['roteamento_ok'] for r in validacao)}/{len(validacao)})")
    print(f"  Teste:     {acuracia(teste):.0%} ({sum(r['roteamento_ok'] for r in teste)}/{len(teste)})")

    # --- Salva os resultados completos (para a correção manual) ---
    (AVALIACAO_DIR / "resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n✓ Resultados salvos em {AVALIACAO_DIR / 'resultados.json'}")


if __name__ == "__main__":
    main()
