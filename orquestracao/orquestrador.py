"""
Orquestrador — amarra os 4 agentes num fluxo único com LangGraph.

Fluxo:
  [reformular] → [recuperar] → decide pela distância:
                                 rota "rag" → [responder_rag]  (corpus)
                                 rota "web" → [responder_web]  (fallback)
              → salva o TRACE (ficha completa) em traces/<timestamp>.json

Rodar:
  ./.venv/bin/python orquestracao/orquestrador.py "qual a pontuação máxima da SPPB?"
  ./.venv/bin/python orquestracao/orquestrador.py            (modo interativo)
"""

import sys
import json
import operator
import warnings
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Annotated

warnings.filterwarnings("ignore")

# Os agentes ficam na pasta agentes/ — colocamos ela no caminho de import.
sys.path.insert(0, str(Path(__file__).parent.parent / "agentes"))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# Reaproveita as peças (agentes) que já construímos e testamos:
from reformulador import reformular
from recuperador import carregar_indice, recuperar_multi, LIMIAR
from respondedor import montar_contexto, REGRAS as REGRAS_RAG
from busca_web import responder_web

load_dotenv()

TRACES_DIR = Path(__file__).parent.parent / "traces"

# Recursos carregados UMA vez (índice e modelo são caros de criar).
print("Carregando índice e modelo...")
INDICE = carregar_indice()
MODELO = ChatOpenAI(model="gpt-4o-mini", temperature=0)
print(f"Pronto — {INDICE.index.ntotal} vetores. Limiar = {LIMIAR}\n")


# ---------------------------------------------------------------------------
# 1) O ESTADO: a "ficha" que passa de agente em agente.
#    Cada campo é preenchido por um dos nós ao longo do caminho.
# ---------------------------------------------------------------------------
class Estado(TypedDict):
    pergunta: str              # a pergunta original do usuário
    pergunta_reformulada: str  # preenchida pelo nó reformular
    distancia_min: float       # preenchida pelo nó recuperar
    rota: str                  # "rag" ou "web" — preenchida pelo nó recuperar
    trechos: list              # os trechos do corpus (quando rota="rag")
    origem: str                # "corpus" ou "web" — de onde veio a resposta
    resposta: str              # a resposta final
    fallback_acionado: bool    # o fallback web foi usado?
    motivo_fallback: str       # por quê (comparação distância x limiar)
    # etapas: registro de cada agente que rodou. O Annotated[..., operator.add]
    # faz o LangGraph SOMAR as listas (cada nó acrescenta a sua etapa, sem apagar).
    etapas: Annotated[list, operator.add]


# ---------------------------------------------------------------------------
# 2) OS NÓS: cada agente é uma função que recebe a ficha e devolve o que mudou.
# ---------------------------------------------------------------------------
def no_reformular(estado: Estado) -> dict:
    reformulada = reformular(MODELO, estado["pergunta"])
    return {
        "pergunta_reformulada": reformulada,
        "etapas": [{
            "agente": "reformulador",
            "acao": "reescreveu a pergunta em termos clínicos",
            "saida": reformulada,
        }],
    }


def no_recuperar(estado: Estado) -> dict:
    # Busca com as DUAS versões (original + reformulada) e une os resultados.
    # k=8 dá um recall melhor que 4, sem inflar o contexto com ruído.
    info = recuperar_multi(INDICE, [estado["pergunta"], estado["pergunta_reformulada"]], k=8)
    # Guardamos os trechos de forma "limpa" (fonte + distância + texto) pro trace.
    trechos = [
        {"fonte": doc.metadata["fonte"], "distancia": float(dist), "texto": doc.page_content}
        for doc, dist in info["resultados"]
    ]

    dist = float(info["distancia_min"])
    fallback = info["rota"] == "web"
    # O "porquê" da decisão, em texto legível para o avaliador.
    sinal = ">" if fallback else "<="
    destino = "corpus não responde → fallback web" if fallback else "corpus responde → RAG"
    motivo = f"melhor distância {dist:.2f} {sinal} limiar {LIMIAR} ({destino})"

    return {
        "distancia_min": dist,
        "rota": info["rota"],
        "trechos": trechos,
        "fallback_acionado": fallback,
        "motivo_fallback": motivo,
        "etapas": [{
            "agente": "recuperador",
            "acao": "buscou no índice (pergunta original + reformulada, união) e decidiu a rota",
            "distancia_min": round(dist, 2),
            "limiar": LIMIAR,
            "decisao": info["rota"],
            "motivo": motivo,
            "fontes_recuperadas": sorted({t["fonte"] for t in trechos}),
        }],
    }


def no_responder_rag(estado: Estado) -> dict:
    # Reconstrói o contexto a partir dos trechos já recuperados (não busca de novo).
    contexto = "\n\n".join(
        f"[Trecho {i} — fonte: {t['fonte']}]\n{t['texto']}"
        for i, t in enumerate(estado["trechos"], 1)
    )
    mensagens = [
        SystemMessage(content=REGRAS_RAG),
        HumanMessage(content=f"TRECHOS:\n{contexto}\n\nPERGUNTA: {estado['pergunta']}"),
    ]
    resposta = MODELO.invoke(mensagens).content
    return {
        "resposta": resposta,
        "origem": "corpus",
        "etapas": [{
            "agente": "respondedor",
            "acao": "gerou a resposta a partir dos trechos do corpus, citando a fonte",
        }],
    }


def no_responder_web(estado: Estado) -> dict:
    resposta = responder_web(MODELO, estado["pergunta"])
    return {
        "resposta": resposta,
        "origem": "web",
        "etapas": [{
            "agente": "busca_web",
            "acao": "fallback: buscou na web (Tavily) e gerou a resposta citando os links",
        }],
    }


# ---------------------------------------------------------------------------
# 3) A ARESTA CONDICIONAL: olha a ficha e diz por qual nó seguir.
# ---------------------------------------------------------------------------
def decidir_rota(estado: Estado) -> str:
    return estado["rota"]  # "rag" ou "web" (preenchido pelo nó recuperar)


# ---------------------------------------------------------------------------
# 4) MONTAGEM DO GRAFO: registra os nós e liga as setas.
# ---------------------------------------------------------------------------
def construir_grafo():
    grafo = StateGraph(Estado)

    grafo.add_node("reformular", no_reformular)
    grafo.add_node("recuperar", no_recuperar)
    grafo.add_node("responder_rag", no_responder_rag)
    grafo.add_node("responder_web", no_responder_web)

    grafo.add_edge(START, "reformular")       # início → reformular
    grafo.add_edge("reformular", "recuperar")  # reformular → recuperar

    # Aresta condicional: depois de recuperar, decidir_rota escolhe o próximo nó.
    grafo.add_conditional_edges(
        "recuperar",
        decidir_rota,
        {"rag": "responder_rag", "web": "responder_web"},
    )

    grafo.add_edge("responder_rag", END)  # os dois caminhos terminam no FIM
    grafo.add_edge("responder_web", END)

    return grafo.compile()


def salvar_trace(estado_final: dict) -> Path:
    """Salva a ficha completa como um JSON (a auditoria exigida pelo desafio)."""
    TRACES_DIR.mkdir(exist_ok=True)
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = TRACES_DIR / f"{carimbo}.json"

    registro = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "pergunta": estado_final["pergunta"],
        "pergunta_reformulada": estado_final.get("pergunta_reformulada"),
        # etapas: quem processou cada passo (exigência do desafio, item 2 do trace).
        "etapas": estado_final.get("etapas", []),
        "limiar": LIMIAR,
        "distancia_min": estado_final.get("distancia_min"),
        "rota": estado_final.get("rota"),
        "origem": estado_final.get("origem"),
        "fallback_acionado": estado_final.get("fallback_acionado"),
        "motivo_fallback": estado_final.get("motivo_fallback"),
        # No trace, guardamos só um resumo de cada trecho (fonte + distância + prévia).
        "trechos": [
            {"fonte": t["fonte"], "distancia": round(t["distancia"], 2),
             "previa": t["texto"][:200]}
            for t in estado_final.get("trechos", [])
        ],
        "resposta": estado_final.get("resposta"),
    }
    caminho.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    return caminho


def perguntar(app, pergunta: str):
    # O .invoke roda o grafo inteiro, começando com a ficha só com a pergunta.
    estado_final = app.invoke({"pergunta": pergunta})

    origem = "📚 corpus" if estado_final["origem"] == "corpus" else "🌐 web"
    print(f"🔄 reformulada: {estado_final['pergunta_reformulada']}")
    print(f"📏 distância: {estado_final['distancia_min']:.2f}  →  rota: {estado_final['rota']} ({origem})\n")
    print(f"🤖 {estado_final['resposta']}")

    caminho = salvar_trace(estado_final)
    print(f"\n📝 trace salvo em: {caminho}")


def main():
    app = construir_grafo()

    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])
        print(f"❓ {pergunta}\n")
        perguntar(app, pergunta)
    else:
        print('Digite uma pergunta e Enter. (Enter vazio para sair)')
        while True:
            pergunta = input("\n❓ Pergunta: ").strip()
            if not pergunta:
                print("Até mais! 👋")
                break
            print()
            perguntar(app, pergunta)


if __name__ == "__main__":
    main()
