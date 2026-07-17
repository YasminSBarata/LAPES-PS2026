"""
Gera o relatório final do benchmark em Markdown (avaliacao/resultados.md).

Junta:
  - resultados.json      (dados automáticos: rota, roteamento_ok, resposta, fonte)
  - correcao_manual.py   (as notas humanas de correção)

E produz a tabela no formato pedido pelo desafio (pergunta, fonte, RAG/fallback,
resposta, pontuação) + a metodologia e o resumo das métricas.

Rodar:  ./.venv/bin/python avaliacao/gerar_relatorio.py
"""

import json
from pathlib import Path
from correcao_manual import CORRECAO

AVALIACAO_DIR = Path(__file__).parent


def resumir(texto: str, limite: int = 160) -> str:
    """Encurta a resposta e tira quebras de linha, pra caber numa célula da tabela."""
    t = " ".join((texto or "").split())
    return t if len(t) <= limite else t[:limite] + "…"


def linha_tabela(r: dict) -> str:
    correcao = CORRECAO.get(r["id"], {"correto": None})
    rota_txt = "RAG" if r["rota"] == "rag" else "fallback"
    rot_ok = "✅" if r["roteamento_ok"] else "❌"
    corr_ok = "✅" if correcao["correto"] else "❌"
    return (
        f"| {r['id']} | {r['pergunta']} | {r['fonte']} | {rota_txt} | "
        f"{rot_ok} | {corr_ok} | {resumir(r['resposta'])} |"
    )


def bloco_metricas(nome: str, subset: list) -> str:
    n = len(subset)
    rot = sum(x["roteamento_ok"] for x in subset)
    corr = sum(CORRECAO.get(x["id"], {}).get("correto") is True for x in subset)
    return (f"| {nome} | {rot}/{n} ({rot/n:.0%}) | {corr}/{n} ({corr/n:.0%}) |")


def main():
    resultados = json.loads((AVALIACAO_DIR / "resultados.json").read_text(encoding="utf-8"))

    teste = [r for r in resultados if r["conjunto"] == "teste"]
    validacao = [r for r in resultados if r["conjunto"] == "validacao"]

    cabecalho = "| ID | Pergunta | Fonte recuperada | Rota | Roteamento | Correção | Resposta (resumo) |"
    separador = "|----|----------|------------------|------|:----------:|:--------:|-------------------|"

    partes = []
    partes.append("# Benchmark de avaliação — Sistema Agêntico RAG (ElderSync)\n")

    partes.append("## Metodologia\n")
    partes.append(
        "Foram avaliadas **20 perguntas**, divididas em **validação** (10, usadas no "
        "desenvolvimento) e **teste** (10, reservadas para o resultado oficial). "
        "Metade de cada conjunto é respondível pelo corpus e metade é de **fallback** "
        "(fora do domínio, deve ir para a web) — 10 perguntas de fallback no total.\n"
    )
    partes.append("Duas métricas complementares:\n")
    partes.append(
        "1. **Acurácia de roteamento** (automática): a pergunta foi para a fonte certa "
        "(corpus→RAG, fallback→web)? *Escolhida porque, num assistente clínico, o erro "
        "mais grave é buscar no lugar errado — responder de memória quando deveria buscar, "
        "ou dizer \"não sei\" quando a resposta estava no corpus.*\n"
        "2. **Correção da resposta** (manual): a resposta final está factualmente correta, "
        "responde à pergunta e não inventa? *Avaliada por leitura humana de cada resposta — "
        "transparente e sem depender de outro modelo como juiz.*\n"
    )

    partes.append("## Resultados — conjunto de TESTE (oficial)\n")
    partes.append(cabecalho)
    partes.append(separador)
    partes.extend(linha_tabela(r) for r in teste)

    partes.append("\n## Resultados — conjunto de VALIDAÇÃO\n")
    partes.append(cabecalho)
    partes.append(separador)
    partes.extend(linha_tabela(r) for r in validacao)

    partes.append("\n## Resumo das métricas\n")
    partes.append("| Conjunto | Acurácia de roteamento | Correção da resposta |")
    partes.append("|----------|:----------------------:|:--------------------:|")
    partes.append(bloco_metricas("Teste (oficial)", teste))
    partes.append(bloco_metricas("Validação", validacao))
    partes.append(bloco_metricas("Geral", resultados))

    partes.append("\n## Observações sobre as falhas de correção\n")
    for r in resultados:
        nota = CORRECAO.get(r["id"], {}).get("nota")
        if CORRECAO.get(r["id"], {}).get("correto") is False and nota:
            partes.append(f"- **{r['id']}** ({r['pergunta']}): {nota}")

    partes.append(
        "\n> As falhas de correção não são alucinações: em todos os casos o sistema "
        "**admitiu não ter encontrado** em vez de inventar. As causas são qualidade de "
        "recuperação (modelo de embedding pequeno) e resultados de busca web pobres — "
        "melhorias futuras: reranker, modelo de embedding maior, mais resultados no Tavily.\n"
    )

    saida = AVALIACAO_DIR / "resultados.md"
    saida.write_text("\n".join(partes), encoding="utf-8")
    print(f"✓ Relatório gerado em {saida}")


if __name__ == "__main__":
    main()
