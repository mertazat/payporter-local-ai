import json
from pathlib import Path

import numpy as np
import ollama


INDEX_FILE = "code_index.json"
MODEL_NAME = "qwen3:4b"
EMBEDDING_MODEL = "nomic-embed-text"


def load_index():
    index_path = Path(INDEX_FILE)

    if not index_path.exists():
        raise FileNotFoundError(
            "code_index.json bulunamadı. Önce kod indeksini oluşturun."
        )

    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_embedding(text):
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=text
    )

    return response["embedding"]


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def search_code(question, top_k=5):
    chunks = load_index()

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

        results.append((score, chunk))

    results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return results[:top_k]


def ask_codebase(question):
    top_results = search_code(question)

    if not top_results:
        return {
            "answer": "No relevant source code was found.",
            "sources": []
        }

    context_parts = []

    for score, chunk in top_results:

        context_parts.append(
            f"""
File: {chunk['file']}
Lines: {chunk['start_line']}-{chunk['end_line']}

{chunk['content']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a private software assistant that analyzes internal source code.

Answer the user's question using only the provided source code context.

If multiple files are related, analyze them together.
Do not invent code that is not present in the context.
Mention relevant files when useful.

SOURCE CODE:

{context}

USER QUESTION:

{question}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    sources = []

    for score, chunk in top_results:
        sources.append({
            "file": chunk["file"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "score": score
        })

    return {
        "answer": answer,
        "sources": sources
    }


def check_llm():
    try:
        ollama.list()
        return True
    except Exception:
        return False
