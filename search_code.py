from pathlib import Path
import math
import ollama

CODE_FOLDER = Path("company_code")

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".cs", ".java", ".sql", ".html", ".css"
}


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(y * y for y in b))

    return dot_product / (magnitude_a * magnitude_b)


chunks = []

for file_path in CODE_FOLDER.rglob("*"):

    if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:

        content = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        if not content.strip():
            continue

        lines = content.splitlines()

        for i in range(0, len(lines), 10):

            chunk_text = "\n".join(lines[i:i + 10])

            if chunk_text.strip():

                chunks.append({
                    "file": str(file_path),
                    "start_line": i + 1,
                    "text": chunk_text
                })


print("Toplam chunk:", len(chunks))
print("Embeddingler oluşturuluyor...")


for chunk in chunks:

    response = ollama.embed(
        model="nomic-embed-text",
        input=chunk["text"]
    )

    chunk["embedding"] = response["embeddings"][0]


question = input("\nSorunuzu yazın: ")


question_response = ollama.embed(
    model="nomic-embed-text",
    input=question
)

question_embedding = question_response["embeddings"][0]


for chunk in chunks:

    chunk["score"] = cosine_similarity(
        question_embedding,
        chunk["embedding"]
    )


chunks.sort(
    key=lambda x: x["score"],
    reverse=True
)


print("\nEn alakalı kod parçaları:\n")


for chunk in chunks[:3]:

    print("=" * 60)

    print("Dosya:", chunk["file"])
    print("Satır:", chunk["start_line"])
    print("Benzerlik:", round(chunk["score"], 4))

    print("-" * 60)

    print(chunk["text"])

    print()
