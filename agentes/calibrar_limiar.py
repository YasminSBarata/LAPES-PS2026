"""
Calibração do limiar do fallback.

Ideia: para decidir "o corpus tem a resposta?" a gente olha a distância do
MELHOR trecho (o mais próximo) que a busca encontrou.
  - Pergunta DENTRO do corpus  → melhor distância BAIXA.
  - Pergunta FORA do corpus     → melhor distância ALTA.

Este script roda perguntas dos dois grupos e imprime a menor distância de cada,
pra a gente enxergar onde fica a "fronteira" e escolher o número de corte.

Rodar:  ./.venv/bin/python agentes/calibrar_limiar.py
"""

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INDICE_DIR = Path(__file__).parent.parent / "indice"
MODELO_EMBED = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Perguntas que a gente SABE que estão cobertas pelo corpus.
DENTRO = [
    "qual a pontuação máxima da SPPB?",
    "quanto tempo manter o equilíbrio em cada posição no teste?",
    "o que é o teste Timed Up and Go?",
    "como o ElderSync integra os sensores IoT?",
    "quais fatores aumentam o risco de quedas em idosos?",
]

# Perguntas claramente FORA do assunto do corpus.
FORA = [
    "qual o preço do iPhone lançado em 2025?",
    "quem ganhou a Copa do Mundo de 2022?",
    "me dê uma receita de bolo de cenoura",
    "qual a capital da Austrália?",
    "como configurar um servidor nginx?",
]


def menor_distancia(indice, pergunta: str) -> float:
    """Devolve a distância do trecho MAIS próximo da pergunta (o melhor hit)."""
    resultados = indice.similarity_search_with_score(pergunta, k=1)
    return resultados[0][1]  # (doc, distancia) → pega a distancia


def main():
    print("Carregando índice...")
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBED)
    indice = FAISS.load_local(str(INDICE_DIR), embeddings, allow_dangerous_deserialization=True)
    print(f"Pronto — {indice.index.ntotal} vetores.\n")

    print("=== DENTRO do corpus (esperado: distância BAIXA) ===")
    dentro_dists = []
    for p in DENTRO:
        d = menor_distancia(indice, p)
        dentro_dists.append(d)
        print(f"  {d:5.2f}  {p}")

    print("\n=== FORA do corpus (esperado: distância ALTA) ===")
    fora_dists = []
    for p in FORA:
        d = menor_distancia(indice, p)
        fora_dists.append(d)
        print(f"  {d:5.2f}  {p}")

    # Resumo: o "teto" do grupo de dentro e o "piso" do grupo de fora.
    # Um bom limiar fica ENTRE esses dois valores.
    print("\n--- Resumo ---")
    print(f"  Maior distância DENTRO: {max(dentro_dists):.2f}")
    print(f"  Menor distância FORA:   {min(fora_dists):.2f}")
    print(f"  → um limiar entre esses dois valores separa os grupos.")


if __name__ == "__main__":
    main()
