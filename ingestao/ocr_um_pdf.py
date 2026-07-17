"""
Ferramenta pontual: extrai texto de um PDF baseado em imagem (scan) via OCR.

Uso: renderiza cada página como imagem, passa pelo motor de OCR (rapidocr)
e salva o texto reconhecido num arquivo .txt ao lado do PDF.

Rodar:  ./.venv/bin/python ingestao/ocr_um_pdf.py
"""

from pathlib import Path
import fitz  # PyMuPDF — abre o PDF e renderiza páginas como imagem
import numpy as np
from rapidocr_onnxruntime import RapidOCR

# PDF-imagem que queremos "ler" e onde salvar o texto reconhecido
PDF_ALVO = Path("corpus/artigos/A_short_physical_performance_battery_ass.pdf")
SAIDA_TXT = PDF_ALVO.with_name("A_short_physical_performance_battery_ass_OCR.txt")


def main():
    motor = RapidOCR()          # carrega o motor de OCR (modelos já embutidos)
    documento = fitz.open(PDF_ALVO)
    partes = []

    for numero, pagina in enumerate(documento, start=1):
        # Renderiza a página como imagem a 250 DPI (boa nitidez para OCR), sem canal alfa.
        pix = pagina.get_pixmap(dpi=250, alpha=False)
        # Converte os pixels da imagem para o formato (altura, largura, 3 cores) que o OCR entende.
        imagem = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

        resultado, _ = motor(imagem)  # roda o OCR na imagem da página
        # resultado é uma lista de [caixa, texto, confiança]; pegamos só os textos.
        linhas = [linha[1] for linha in resultado] if resultado else []
        partes.append("\n".join(linhas))
        print(f"  página {numero}/{len(documento)} — {len(linhas)} linhas reconhecidas")

    texto_final = "\n\n".join(partes)
    SAIDA_TXT.write_text(texto_final, encoding="utf-8")
    print(f"\n✓ Salvo em {SAIDA_TXT} ({len(texto_final):,} caracteres)")


if __name__ == "__main__":
    main()
