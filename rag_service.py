import json
from pathlib import Path

import numpy as np
import ollama


INDEX_FILE = "code_index.json"
MODEL_NAME = "deepseek-r1:7b"
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


    unique_results = []
    seen_files = set()

    for score, chunk in results:
        file_name = chunk.get("file")

        if file_name not in seen_files:
            seen_files.add(file_name)
            unique_results.append((score, chunk))

        if len(unique_results) >= top_k:
            break

    return unique_results

def ask_codebase(question, chat_history=None, model_name=None):
    chat_history = chat_history or []

    recent_history = chat_history[-6:]

    history_text = "\n".join(
        f'{message["role"]}: {message["content"]}'
        for message in recent_history
    )

    search_query = f"""
Previous conversation:
{history_text}

Current question:
{question}
"""

    top_results = search_code(search_query)

    if not top_results:
        return {
            "answer": "İlgili kaynak kod bulunamadı.",
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

LANGUAGE RULES:
- Detect the language of the user's question automatically.
- Always answer in the same language as the user's question.
- If the user asks in Turkish, answer completely in Turkish.
- Keep technical terms, function names, class names and file names unchanged.
- Understand Turkish even when Turkish characters are omitted.
- Tolerate common spelling mistakes and informal Turkish.

CONVERSATION RULES:
- Use the previous conversation to understand follow-up questions.
- Resolve references such as "bu", "bunu", "o", "hangi dosyada", "nerede" from previous messages when possible.

STRICT GROUNDING RULES:
- Treat the provided SOURCE CODE as the only source of truth.
- Never invent or assume functions, variables, classes, files, return values, tokens, sessions, database operations, security behavior, or implementation details.
- Every technical claim must be directly supported by the provided SOURCE CODE.
- If something is not explicitly present in the SOURCE CODE, say clearly that it is not shown in the available source code.
- Never infer behavior merely because it would normally exist in a real application.
- Never add explanations based on general programming knowledge unless the user explicitly asks for general information.
- If the retrieved context is insufficient, say that the available source code is insufficient to answer confidently.
- Previous conversation may clarify the user's question, but it must never be treated as evidence about the source code.
- When the answer refers to a specific implementation detail, mention the relevant file and line or line range when available.
- Distinguish clearly between what the code DOES and what the code DOES NOT show.
- Do not contradict explicit source code. If the source contains a statement such as token = secrets.token_hex(16), report exactly that behavior.

CODE RULES:
- If multiple files are related, analyze them together.
- Do not invent code that is not present in the context.
- Mention relevant files when useful.

Previous conversation:
{history_text}

SOURCE CODE:
{context}

USER QUESTION:
{question}
"""

    response = ollama.chat(
        model=model_name or MODEL_NAME,
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
