"""
Agente Respondedor — o "RAG básico".

Fluxo:
  pergunta → busca os trechos mais relevantes no índice FAISS
          → monta um prompt com [regras + trechos + pergunta]
          → o gpt-4o-mini escreve a resposta usando SÓ esses trechos, citando a fonte.

Rodar:
  ./.venv/bin/python agentes/respondedor.py "qual a pontuação máxima da SPPB?"
  ./.venv/bin/python agentes/respondedor.py            (modo interativo)
"""

import sys
import warnings
warnings.filterwarnings("ignore")  # esconde avisos que não são erros

from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()  # carrega a OPENAI_API_KEY do .env

INDICE_DIR = Path(__file__).parent.parent / "indice"
MODELO_EMBED = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# --- As REGRAS do agente (o "system prompt"): o que ele pode e não pode fazer. ---
# A regra de ouro é a última: se a resposta não está nos trechos, ADMITIR que não sabe.
# É isso que impede o modelo de "inventar" (alucinar).
REGRAS = """Você é um assistente clínico especializado em mobilidade e risco de quedas em idosos.
Responda à pergunta do usuário com base nos trechos fornecidos.
As informações relevantes podem estar ESPALHADAS em vários trechos — reúna-as e sintetize uma resposta completa.
Baseie-se SOMENTE no conteúdo dos trechos: não use conhecimento externo nem invente dados.
Cite a(s) fonte(s) usada(s) (o nome do arquivo aparece em cada trecho).
Só diga que não encontrou a informação se os trechos realmente NÃO tratarem do assunto perguntado.
Responda em português, de forma objetiva."""


def carregar_indice():
    """Carrega o modelo de embedding e o índice FAISS salvo em disco."""
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBED)
    return FAISS.load_local(
        str(INDICE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def montar_contexto(resultados) -> str:
    """Transforma a lista de trechos achados num texto único, numerado e com a fonte.

    É esse texto que vai dentro do prompt, no lugar de "TRECHOS".
    """
    partes = []
    for i, (doc, distancia) in enumerate(resultados, 1):
        fonte = doc.metadata["fonte"]
        partes.append(f"[Trecho {i} — fonte: {fonte}]\n{doc.page_content}")
    return "\n\n".join(partes)


def responder(indice, modelo, pergunta: str, k: int = 4) -> str:
    """Executa o RAG: busca os k trechos, monta o prompt e pede a resposta ao LLM."""
    # 1) Busca semântica no índice (mesmo passo do buscar.py).
    resultados = indice.similarity_search_with_score(pergunta, k=k)

    # 2) Monta o "contexto" (os trechos formatados) que o LLM vai ler.
    contexto = montar_contexto(resultados)

    # 3) Monta as duas mensagens do prompt:
    #    - SystemMessage: as regras (quem ele é, o que pode/não pode).
    #    - HumanMessage: os trechos + a pergunta de verdade.
    mensagens = [
        SystemMessage(content=REGRAS),
        HumanMessage(content=f"TRECHOS:\n{contexto}\n\nPERGUNTA: {pergunta}"),
    ]

    # 4) Manda pro modelo e devolve só o texto da resposta.
    resposta = modelo.invoke(mensagens)
    return resposta.content


def main():
    print("Carregando índice e modelo...")
    indice = carregar_indice()
    modelo = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    print(f"Pronto — {indice.index.ntotal} vetores no índice.\n")

    if len(sys.argv) > 1:
        pergunta = " ".join(sys.argv[1:])
        print(f"❓ {pergunta}\n")
        print(f"🤖 {responder(indice, modelo, pergunta)}")
    else:
        print('Digite uma pergunta e Enter. (Enter vazio para sair)')
        while True:
            pergunta = input("\n❓ Pergunta: ").strip()
            if not pergunta:
                print("Até mais! 👋")
                break
            print(f"\n🤖 {responder(indice, modelo, pergunta)}")


if __name__ == "__main__":
    main()
