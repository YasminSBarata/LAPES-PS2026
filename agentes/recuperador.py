"""
Agente Recuperador — busca no índice e DECIDE se o corpus responde ou não.

Régua da decisão: a distância do melhor trecho encontrado.
  - menor distância <= LIMIAR  → o corpus tem material  → rota "rag"
  - menor distância  > LIMIAR  → o corpus não tem       → rota "web" (fallback)

O LIMIAR (12.5) foi escolhido empiricamente: as perguntas de dentro do corpus
deram distância <= 11.46 e as de fora >= 13.75 (ver agentes/calibrar_limiar.py).
12.5 fica no meio desse vão, com margem dos dois lados.

Rodar:
  ./.venv/bin/python agentes/recuperador.py "qual a pontuação máxima da SPPB?"
  ./.venv/bin/python agentes/recuperador.py            (modo interativo)
"""

import sys
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INDICE_DIR = Path(__file__).parent.parent / "indice"
MODELO_EMBED = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Limiar de corte (distância). <= vai pro RAG; > vai pro fallback web.
LIMIAR = 12.5


def carregar_indice():
    """Carrega o modelo de embedding e o índice FAISS salvo em disco."""
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBED)
    return FAISS.load_local(
        str(INDICE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def _decidir(resultados: list) -> dict:
    """Recebe uma lista [(doc, distancia), ...] já ordenada e monta a decisão."""
    distancia_min = resultados[0][1]  # o primeiro é o mais próximo
    rota = "rag" if distancia_min <= LIMIAR else "web"
    return {"rota": rota, "distancia_min": distancia_min, "resultados": resultados}


def recuperar(indice, pergunta: str, k: int = 4) -> dict:
    """Busca os k trechos de UMA pergunta e decide a rota pela menor distância."""
    resultados = indice.similarity_search_with_score(pergunta, k=k)
    return _decidir(resultados)


def recuperar_multi(indice, perguntas: list, k: int = 4) -> dict:
    """Busca com VÁRIAS versões da pergunta (ex.: original + reformulada) e une.

    Motivo: a reformulação nem sempre ajuda — às vezes a original acha o trecho
    que a reformulada perde. Buscando com as duas e ficando com a MENOR distância
    de cada trecho, aproveitamos o melhor das duas.
    """
    melhor_por_trecho = {}  # chave: (fonte, texto) → (doc, menor_distancia)
    for pergunta in perguntas:
        for doc, dist in indice.similarity_search_with_score(pergunta, k=k):
            chave = (doc.metadata["fonte"], doc.page_content)
            # Guarda este trecho só se ainda não vimos ou se agora veio mais perto.
            if chave not in melhor_por_trecho or dist < melhor_por_trecho[chave][1]:
                melhor_por_trecho[chave] = (doc, dist)

    # Ordena todos os trechos únicos pela distância (menor primeiro) e pega os k melhores.
    resultados = sorted(melhor_por_trecho.values(), key=lambda par: par[1])[:k]
    return _decidir(resultados)


def main():
    print("Carregando índice...")
    indice = carregar_indice()
    print(f"Pronto — {indice.index.ntotal} vetores. Limiar = {LIMIAR}\n")

    def mostrar(pergunta):
        info = recuperar(indice, pergunta)
        emoji = "📚" if info["rota"] == "rag" else "🌐"
        rota_txt = "RAG (corpus)" if info["rota"] == "rag" else "FALLBACK (web)"
        print(f"❓ {pergunta}")
        print(f"   distância do melhor trecho: {info['distancia_min']:.2f}")
        print(f"   {emoji} decisão: {rota_txt}\n")

    if len(sys.argv) > 1:
        mostrar(" ".join(sys.argv[1:]))
    else:
        print('Digite uma pergunta e Enter. (Enter vazio para sair)')
        while True:
            pergunta = input("❓ Pergunta: ").strip()
            if not pergunta:
                print("Até mais! 👋")
                break
            print()
            mostrar(pergunta)


if __name__ == "__main__":
    main()
