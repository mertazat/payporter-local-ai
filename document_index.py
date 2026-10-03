import json
from pathlib import Path

from document_chunker import chunk_pdf
from rag_service import create_embedding


DOCUMENTS_DIR = Path("documents")
OUTPUT_FILE = "document_index.json"


def build_document_index():
    index = []

    pdf_files = list(DOCUMENTS_DIR.glob("*.pdf"))

    print(f"Bulunan PDF sayısı: {len(pdf_files)}")

    for pdf_path in pdf_files:
        print(f"\nPDF işleniyor: {pdf_path.name}")

        chunks = chunk_pdf(pdf_path)

        for i, chunk in enumerate(chunks, start=1):
            print(
                f"Embedding: {pdf_path.name} "
                f"sayfa {chunk['page']} "
                f"chunk {i}/{len(chunks)}"
            )

            embedding = create_embedding(chunk["text"])

            index.append({
                "source_type": "pdf",
                "source": chunk["source"],
                "page": chunk["page"],
                "text": chunk["text"],
                "embedding": embedding
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)

    print("\nDocument index oluşturuldu.")
    print(f"PDF sayısı: {len(pdf_files)}")
    print(f"Toplam chunk: {len(index)}")
    print(f"Kaydedilen dosya: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_document_index()
