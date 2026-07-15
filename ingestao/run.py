"""
Pipeline de ingestão do ElderSync — ETAPAS 1, 2 e 3.

  Etapa 1: LER os documentos do corpus (PDF e Markdown/texto).
  Etapa 2: PICAR cada documento em chunks (medidos em TOKENS), com metadados.
  Etapa 3: gerar EMBEDDINGS e salvar o índice FAISS em disco.

Rodar:  ./.venv/bin/python ingestao/run.py
"""

from pathlib import Path
from pypdf import PdfReader
from transformers import AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- Configurações fixas do pipeline ---
CORPUS_DIR = Path(__file__).parent.parent / "corpus"
INDICE_DIR = Path(__file__).parent.parent / "indice"
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Tamanho do chunk agora em TOKENS (não caracteres). 120 deixa folga sob a
# janela de 128 tokens do modelo, garantindo que nenhum chunk seja cortado.
TAMANHO_CHUNK = 120
OVERLAP = 24


def ler_pdf(caminho: Path) -> str:
    """Abre um PDF e devolve todo o texto dele como uma única string."""
    leitor = PdfReader(caminho)
    paginas = [pagina.extract_text() or "" for pagina in leitor.pages]
    return "\n".join(paginas)


def ler_markdown(caminho: Path) -> str:
    """Abre um arquivo de texto (.md/.txt) e devolve o conteúdo como string."""
    return caminho.read_text(encoding="utf-8")


def ler_documento(caminho: Path) -> str:
    """Escolhe o leitor certo conforme a extensão do arquivo."""
    if caminho.suffix.lower() == ".pdf":
        return ler_pdf(caminho)
    elif caminho.suffix.lower() in (".md", ".txt"):
        return ler_markdown(caminho)
    else:
        raise ValueError(f"Formato não suportado: {caminho.name}")


# Picador que MEDE em tokens: usamos o tokenizador do próprio modelo como régua.
# Assim o chunk_size=120 significa "120 tokens", e não "120 caracteres".
tokenizador = AutoTokenizer.from_pretrained(MODELO)
splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    tokenizador,
    chunk_size=TAMANHO_CHUNK,
    chunk_overlap=OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def criar_chunks(texto: str, fonte: str, tipo: str) -> list:
    """Pica um texto em chunks, colando os metadados (fonte + tipo) em cada um."""
    return splitter.create_documents(
        texts=[texto],
        metadatas=[{"fonte": fonte, "tipo": tipo}],
    )


def main():
    # --- Etapas 1 e 2: ler e picar todos os documentos ---
    arquivos = sorted(
        caminho
        for caminho in CORPUS_DIR.rglob("*")
        if caminho.is_file() and caminho.name != ".gitkeep"
    )
    print(f"Encontrados {len(arquivos)} documentos em {CORPUS_DIR}\n")

    todos_os_chunks = []
    for caminho in arquivos:
        texto = ler_documento(caminho)
        chunks = criar_chunks(texto, fonte=caminho.name, tipo=caminho.parent.name)
        todos_os_chunks.extend(chunks)
        print(f"📄 {caminho.name}  →  {len(chunks)} chunks")

    print(f"\nTotal: {len(todos_os_chunks)} chunks.")

    # --- Etapa 3: embeddings + índice FAISS ---
    print(f"\nCarregando o modelo de embedding ({MODELO})...")
    embeddings = HuggingFaceEmbeddings(model_name=MODELO)

    print("Gerando embeddings e construindo o índice FAISS (pode levar ~1 min)...")
    indice = FAISS.from_documents(todos_os_chunks, embeddings)

    INDICE_DIR.mkdir(exist_ok=True)
    indice.save_local(str(INDICE_DIR))
    print(f"\n✓ Índice salvo em {INDICE_DIR}")


if __name__ == "__main__":
    main()
