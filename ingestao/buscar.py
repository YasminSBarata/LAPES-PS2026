"""
Ferramenta de teste de busca no índice FAISS.

Dois jeitos de usar:
  1) Interativo — você digita perguntas em loop:
       ./.venv/bin/python ingestao/buscar.py
  2) Pergunta direto no comando:
       ./.venv/bin/python ingestao/buscar.py "qual a pontuação máxima da SPPB?"
"""

import sys
import warnings
warnings.filterwarnings("ignore")  # esconde avisos que não são erros

from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INDICE_DIR = Path(__file__).parent.parent / "indice"
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def carregar_indice():
    """Carrega o modelo de embedding e o índice FAISS salvo em disco."""
    embeddings = HuggingFaceEmbeddings(model_name=MODELO)
    return FAISS.load_local(
        str(INDICE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def buscar(indice, pergunta: str, k: int = 3):
    """Busca os k chunks mais próximos da pergunta e imprime cada um."""
    print(f"\n❓ {pergunta}")
    # similarity_search_with_score devolve (chunk, distância). Distância MENOR = mais parecido.
    resultados = indice.similarity_search_with_score(pergunta, k=k)
    for i, (doc, distancia) in enumerate(resultados, 1):
        trecho = doc.page_content[:200].replace("\n", " ").strip()
        print(f"  {i}. [{doc.metadata['fonte']}]  (distância: {distancia:.2f})")
        print(f"     {trecho}...")


def main():
    print("Carregando o índice...")
    indice = carregar_indice()
    print(f"Pronto — {indice.index.ntotal} vetores no índice.")

    if len(sys.argv) > 1:
        # Modo 1: a pergunta veio junto no comando (tudo depois do nome do arquivo).
        buscar(indice, " ".join(sys.argv[1:]))
    else:
        # Modo 2: interativo — fica pedindo perguntas até você apertar Enter vazio.
        print('Digite uma pergunta e Enter. (Enter vazio para sair)')
        while True:
            pergunta = input("\n❓ Pergunta: ").strip()
            if not pergunta:
                print("Até mais! 👋")
                break
            buscar(indice, pergunta)


if __name__ == "__main__":
    main()
