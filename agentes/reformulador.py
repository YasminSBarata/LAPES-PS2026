"""
Agente Reformulador — reescreve a pergunta do usuário em termos clínicos.

Roda ANTES da busca. Objetivo: aproximar a linguagem da pergunta da linguagem
do corpus (termos como TUG, SPPB, velocidade de marcha), o que reduz a distância
na busca e melhora os trechos recuperados.

Rodar (mostra pergunta original vs reformulada e a distância de cada uma):
  ./.venv/bin/python agentes/reformulador.py "o idoso tá caindo muito, e aí?"
"""

import sys
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

INDICE_DIR = Path(__file__).parent.parent / "indice"
MODELO_EMBED = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Regras: reescrever mantendo a intenção, em vocabulário clínico, SEM responder.
REGRAS = """Sua tarefa é reescrever a pergunta do usuário de forma clara e específica.
Quando a pergunta for sobre mobilidade ou risco de quedas em idosos, use o vocabulário
clínico da área (ex.: TUG, SPPB, velocidade de marcha, equilíbrio, força de membros inferiores).
Se a pergunta fugir desse tema, apenas reescreva-a de forma clara, SEM recusar.
Mantenha sempre a intenção original. NUNCA responda à pergunta e NUNCA se recuse a reescrever.
Devolva APENAS a pergunta reescrita, em uma linha, em português."""


def reformular(modelo, pergunta: str) -> str:
    """Pede ao LLM a versão clínica da pergunta e devolve só o texto reescrito."""
    mensagens = [
        SystemMessage(content=REGRAS),
        HumanMessage(content=pergunta),
    ]
    return modelo.invoke(mensagens).content.strip()


def main():
    if len(sys.argv) < 2:
        print('Uso: python agentes/reformulador.py "sua pergunta"')
        raise SystemExit(1)

    pergunta = " ".join(sys.argv[1:])
    modelo = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Reformula.
    reformulada = reformular(modelo, pergunta)

    # Demonstração: mede a distância do melhor trecho ANTES e DEPOIS de reformular.
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBED)
    indice = FAISS.load_local(str(INDICE_DIR), embeddings, allow_dangerous_deserialization=True)

    dist_antes = indice.similarity_search_with_score(pergunta, k=1)[0][1]
    dist_depois = indice.similarity_search_with_score(reformulada, k=1)[0][1]

    print(f"\n📝 Original:     {pergunta}")
    print(f"   melhor distância: {dist_antes:.2f}")
    print(f"\n🔄 Reformulada:  {reformulada}")
    print(f"   melhor distância: {dist_depois:.2f}")

    melhora = dist_antes - dist_depois
    sinal = "menor (melhorou 👍)" if melhora > 0 else "maior (piorou)"
    print(f"\n→ variação: {melhora:+.2f} — distância ficou {sinal}")


if __name__ == "__main__":
    main()
