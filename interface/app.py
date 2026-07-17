"""
Interface web (Streamlit) do assistente ElderSync.

Um chat simples: o usuário faz uma pergunta, o orquestrador decide entre
responder pelo corpus (RAG) ou buscar na web (fallback), e a interface mostra
a resposta junto com os detalhes da execução (rota, distância, fontes).

Rodar:  ./.venv/bin/streamlit run interface/app.py
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import streamlit as st

# O orquestrador está na pasta orquestracao/ — colocamos ela no caminho de import.
sys.path.insert(0, str(Path(__file__).parent.parent / "orquestracao"))
from orquestrador import construir_grafo, salvar_trace, LIMIAR  # noqa: E402

st.set_page_config(page_title="ElderSync — Assistente RAG", layout="centered")


# O grafo (com índice e modelo) é caro de montar: carregamos UMA vez e reusamos.
@st.cache_resource
def carregar_app():
    return construir_grafo()


def mostrar_detalhes(estado: dict):
    """Renderiza um painel recolhível com a auditoria da execução."""
    origem = "Corpus (RAG)" if estado.get("origem") == "corpus" else "Web (fallback)"
    with st.expander("Detalhes da execução"):
        st.markdown(f"**Fonte da resposta:** {origem}")
        st.markdown(f"**Pergunta reformulada:** {estado.get('pergunta_reformulada')}")
        st.markdown(
            f"**Decisão de rota:** distância mínima "
            f"{estado.get('distancia_min'):.2f} (limiar {LIMIAR}) — "
            f"{estado.get('motivo_fallback')}"
        )
        if estado.get("origem") == "corpus":
            st.markdown("**Trechos recuperados:**")
            for i, t in enumerate(estado.get("trechos", [])[:4], 1):
                previa = " ".join(t["texto"].split())[:200]
                st.markdown(f"{i}. `{t['fonte']}` (distância {t['distancia']:.2f}) — {previa}…")


st.title("ElderSync — Assistente de Mobilidade e Quedas")
st.caption(
    "Pergunte sobre SPPB, TUG, risco de quedas e mobilidade em idosos. "
    "Quando a pergunta sai do domínio do corpus, o sistema busca na web."
)

app = carregar_app()

# Histórico da conversa (sobrevive às re-execuções do script).
if "historico" not in st.session_state:
    st.session_state.historico = []

# Redesenha o histórico a cada re-execução.
for msg in st.session_state.historico:
    with st.chat_message(msg["papel"]):
        st.markdown(msg["texto"])
        if msg.get("estado"):
            mostrar_detalhes(msg["estado"])

# Caixa de entrada da pergunta (fica fixa no rodapé).
pergunta = st.chat_input("Digite sua pergunta")
if pergunta:
    # 1) Mostra e guarda a pergunta do usuário.
    st.session_state.historico.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # 2) Roda o orquestrador e mostra a resposta.
    with st.chat_message("assistant"):
        with st.spinner("Consultando..."):
            estado = app.invoke({"pergunta": pergunta})
            salvar_trace(estado)  # cada execução gera seu trace JSON
        st.markdown(estado["resposta"])
        mostrar_detalhes(estado)

    # 3) Guarda a resposta (com o estado) no histórico.
    st.session_state.historico.append({
        "papel": "assistant",
        "texto": estado["resposta"],
        "estado": estado,
    })
