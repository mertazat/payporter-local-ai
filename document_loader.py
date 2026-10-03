from pathlib import Path
from pypdf import PdfReader


DOCUMENTS_DIR = Path("documents")


def load_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "file": str(pdf_path),
                "page": page_number,
                "text": text.strip()
            })

    return pages


def load_documents():
    documents = []

    for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):
        print(f"PDF okunuyor: {pdf_path}")

        pages = load_pdf(pdf_path)
        documents.extend(pages)

    return documents


if __name__ == "__main__":
    documents = load_documents()

    print(f"\nToplam okunan sayfa: {len(documents)}")

    for document in documents[:3]:
        print("\n------------------------")
        print("Dosya:", document["file"])
        print("Sayfa:", document["page"])
        print(document["text"][:500])

