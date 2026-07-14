"""
Pipeline de ingestão do ElderSync — ETAPA 1: ler os documentos do corpus.

Por enquanto este script apenas LÊ cada documento e imprime um resumo
(nome, tipo, nº de caracteres e um trecho). Nas próximas etapas ele vai
picar em chunks, gerar embeddings e salvar no índice FAISS.
"""

from pathlib import Path
from pypdf import PdfReader

# Pasta onde estão os documentos. Path(__file__) é o caminho deste arquivo;
# .parent sobe uma pasta (de /ingestao para a raiz do projeto); depois entramos em /corpus.
CORPUS_DIR = Path(__file__).parent.parent / "corpus"


def ler_pdf(caminho: Path) -> str:
    """Abre um PDF e devolve todo o texto dele como uma única string."""
    leitor = PdfReader(caminho)
    paginas = [pagina.extract_text() or "" for pagina in leitor.pages]
    return "\n".join(paginas)


def ler_markdown(caminho: Path) -> str:
    """Abre um arquivo de texto (.md) e devolve o conteúdo como string."""
    return caminho.read_text(encoding="utf-8")


def ler_documento(caminho: Path) -> str:
    """Escolhe o leitor certo conforme a extensão do arquivo."""
    if caminho.suffix.lower() == ".pdf":
        return ler_pdf(caminho)
    elif caminho.suffix.lower() in (".md", ".txt"):
        return ler_markdown(caminho)
    else:
        raise ValueError(f"Formato não suportado: {caminho.name}")


def main():
    # Procura todos os arquivos dentro de corpus/ e subpastas (rglob = busca recursiva),
    # ignorando os .gitkeep. Ordenamos para a saída sair sempre na mesma ordem.
    arquivos = sorted(
        caminho
        for caminho in CORPUS_DIR.rglob("*")
        if caminho.is_file() and caminho.name != ".gitkeep"
    )

    print(f"Encontrados {len(arquivos)} documentos em {CORPUS_DIR}\n")

    for caminho in arquivos:
        texto = ler_documento(caminho)
        tipo = caminho.parent.name  # 'artigos' ou 'eldersync' (nome da subpasta)
        trecho = texto[:120].replace("\n", " ").strip()

        print(f"📄 {caminho.name}")
        print(f"   tipo: {tipo} | caracteres: {len(texto):,}")
        print(f"   início: {trecho}...\n")


if __name__ == "__main__":
    main()
