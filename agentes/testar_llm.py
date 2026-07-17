"""
"Olá mundo" do LLM — testa se a chave da OpenAI está funcionando.

Manda uma frase para o gpt-4o-mini e imprime a resposta.
Se voltar texto, a chave + o crédito estão OK e podemos construir os agentes.

Rodar:  ./.venv/bin/python agentes/testar_llm.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Lê o arquivo .env e joga as variáveis (ex: OPENAI_API_KEY) pro ambiente.
# A ChatOpenAI, mais abaixo, procura a OPENAI_API_KEY automaticamente aqui.
load_dotenv()

# Confere se a chave chegou, antes de gastar uma chamada à toa.
if not os.getenv("OPENAI_API_KEY"):
    print("❌ OPENAI_API_KEY não encontrada. Confira o arquivo .env.")
    raise SystemExit(1)


def main():
    # Cria o "modelo": nosso gpt-4o-mini.
    #   temperature=0 → respostas mais objetivas e previsíveis (bom pra RAG).
    modelo = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    pergunta = "Em uma frase, o que é o teste Timed Up and Go (TUG)?"
    print(f"❓ {pergunta}\n")

    # .invoke() manda a pergunta e espera a resposta do modelo.
    resposta = modelo.invoke(pergunta)

    # A resposta vem num objeto; o texto fica no atributo .content.
    print(f"🤖 {resposta.content}")


if __name__ == "__main__":
    main()
