from pathlib import Path
import json
import sys
import ollama

CODE_FOLDER = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("company_code")
INDEX_FILE = Path("code_index.json")

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".cs", ".java", ".sql", ".html", ".css"
}

CHUNK_SIZE = 30
CHUNK_OVERLAP = 5

IGNORED_FOLDERS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build"
}

def create_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]


chunks = []
processed_files = 0

print("Kod dosyalari taraniyor...")

for file_path in CODE_FOLDER.rglob("*"):

    if not file_path.is_file():
        continue

    if file_path.suffix not in SUPPORTED_EXTENSIONS:
        continue
    if any(folder in file_path.parts for folder in IGNORED_FOLDERS):
        continue
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Okunamadi: {file_path} -> {e}")
        continue

    processed_files += 1
    lines = content.splitlines()

    for start in range(0, len(lines), CHUNK_SIZE - CHUNK_OVERLAP):

        chunk_lines = lines[start:start + CHUNK_SIZE]

        if not any(line.strip() for line in chunk_lines):
            continue

        chunk_text = "\n".join(chunk_lines)

        print(
            f"Embedding: {file_path} "
            f"satir {start + 1}-{start + len(chunk_lines)}"
        )

        chunks.append({
            "file": str(file_path),
            "start_line": start + 1,
            "end_line": start + len(chunk_lines),
            "content": chunk_text,
            "embedding": create_embedding(chunk_text)
        })


with INDEX_FILE.open("w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False)


print("\nIndex olusturuldu.")
print(f"Taranan dosya sayisi: {processed_files}")
print(f"Toplam chunk: {len(chunks)}")
print(f"Kaydedilen dosya: {INDEX_FILE}")
