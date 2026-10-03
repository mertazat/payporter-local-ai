from pathlib import Path
from pypdf import PdfReader


def chunk_pdf(pdf_path, chunk_size=1000, overlap=150):
    pdf_path = Path(pdf_path)
    reader = PdfReader(str(pdf_path))

    chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            continue

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "source": pdf_path.name,
                    "page": page_number,
                    "text": chunk_text
                })

            if end >= len(text):
                break

            start = end - overlap

    return chunks


if __name__ == "__main__":
    pdf_path = "documents/payporter_llm_pdf_test_coding_guidelines (1).pdf"

    chunks = chunk_pdf(pdf_path)

    print(f"Toplam chunk: {len(chunks)}")

    for i, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 60)
        print(f"Chunk: {i}")
        print(f"Dosya: {chunk['source']}")
        print(f"Sayfa: {chunk['page']}")
        print("-" * 60)
        print(chunk["text"][:300])
