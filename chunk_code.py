from pathlib import Path

CODE_FOLDER = Path("company_code")

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".cs", ".java", ".sql", ".html", ".css"
}

CHUNK_SIZE = 10

chunks = []

for file_path in CODE_FOLDER.rglob("*"):

    if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:

        content = file_path.read_text(encoding="utf-8")

        if not content.strip():
            continue

        lines = content.splitlines()

        for start in range(0, len(lines), CHUNK_SIZE):

            end = start + CHUNK_SIZE
            chunk_lines = lines[start:end]

            chunk = {
                "file": str(file_path),
                "start_line": start + 1,
                "end_line": min(end, len(lines)),
                "content": "\n".join(chunk_lines)
            }

            chunks.append(chunk)


for i, chunk in enumerate(chunks, start=1):

    print("\n" + "=" * 60)
    print(f"CHUNK {i}")
    print(f"Dosya: {chunk['file']}")
    print(
        f"Satırlar: {chunk['start_line']} - "
        f"{chunk['end_line']}"
    )
    print("=" * 60)

    print(chunk["content"])


print(f"\nToplam chunk sayısı: {len(chunks)}")
