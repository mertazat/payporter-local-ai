import json
import math
import ollama

INDEX_FILE = "document_index.json"
EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )
    return response["embedding"]


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


def search_documents(question, top_k=3):

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    question_embedding = create_embedding(question)

    results = []

    for chunk in chunks:

        embedding = chunk.get("embedding")

        if not embedding:
            continue

        
        score = cosine_similarity(
            question_embedding,
            embedding
        )
        # Kelime eslesmesine gore kucuk bonus
        question_words = set(question.lower().split())
        chunk_text = (chunk.get("text") or "").lower()

        matching_words = sum(
            1 for word in question_words
            if len(word) > 3 and word in chunk_text
        )

        score += matching_words * 0.01
        results.append({
            "score": score,
            "file": chunk.get("source"),
            "page": chunk.get("page"),
            "text": chunk.get("text")
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    min_score = 0.60
    filtered_results = [
        result for result in results
        if result["score"] >= min_score
    ]

    return filtered_results[:top_k]

if __name__ == "__main__":

    question = input("PDF hakkında soru: ")

    results = search_documents(question)

    print("\nEn alakalı PDF parçaları:\n")

    for i, result in enumerate(results, 1):

        print("=" * 70)
        print(f"SONUÇ {i}")
        print(f"Benzerlik: {result['score']:.4f}")
        print(f"Dosya: {result['file']}")
        print(f"Sayfa: {result['page']}")
        print("-" * 70)
        print(result["text"])
        print()
