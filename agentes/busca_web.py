"""
Agente Busca Web (fallback) — usado quando o corpus NÃO tem a resposta.

Fluxo (espelha o Respondedor, mas a fonte é a internet):
  pergunta → busca no Tavily → monta um prompt com [regras + resultados web + pergunta]
          → o gpt-4o-mini escreve a resposta usando esses resultados, citando os LINKS.

Rodar:
  ./.venv/bin/python agentes/busca_web.py "diretrizes recentes de prevenção de quedas em idosos"
  ./.venv/bin/python agentes/busca_web.py            (modo interativo)
"""

import sys
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()  # carrega TAVILY_API_KEY e OPENAI_API_KEY do .env

# Regras do agente: responder pela WEB, mas com as mesmas travas anti-invenção.
REGRAS = """Você é um assistente clínico especializado em mobilidade e risco de quedas em idosos.
A resposta NÃO estava no material interno, então você recebeu resultados de uma busca na web.
Responda à pergunta usando APENAS as informações desses resultados.
Cite as fontes pelos links (URLs) de onde tirou a informação.
Se os resultados não responderem à pergunta, diga isso claramente. Não invente.
Responda em português, de forma objetiva."""


def buscar_web(pergunta: str, max_results: int = 4) -> list:
    """Faz a busca no Tavily e devolve a lista de resultados (título, url, conteúdo)."""
    ferramenta = TavilySearch(max_results=max_results)
    resposta = ferramenta.invoke({"query": pergunta})
    # O Tavily devolve um dicionário; os itens ficam na chave "results".
    return resposta["results"]


def montar_contexto(resultados: list) -> str:
    """Formata os resultados da web num texto único, com título, link e conteúdo."""
    partes = []
    for i, r in enumerate(resultados, 1):
        partes.append(
            f"[Resultado {i}]\n"
            f"Título: {r.get('title', '')}\n"
            f"Link: {r.get('url', '')}\n"
            f"Conteúdo: {r.get('content', '')}"
        )
    return "\n\n".join(partes)


def responder_web(modelo, pergunta: str) -> str:
    """Fallback completo: busca na web e pede ao LLM para redigir a resposta."""
    resultados = buscar_web(pergunta)
    contexto = montar_contexto(resultados)

    mensagens = [
        SystemMessage(content=REGRAS),
        HumanMessage(content=f"RESULTADOS DA WEB:\n{contexto}\n\nPERGUNTA: {pergunta}"),
    ]
    return modelo.invoke(mensagens).content


def main():
    modelo = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])
        print(f"❓ {pergunta}\n")
        print(f"🌐 {responder_web(modelo, pergunta)}")
    else:
        print('Digite uma pergunta e Enter. (Enter vazio para sair)')
        while True:
            pergunta = input("\n❓ Pergunta: ").strip()
            if not pergunta:
                print("Até mais! 👋")
                break
            print(f"\n🌐 {responder_web(modelo, pergunta)}")


if __name__ == "__main__":
    main()
