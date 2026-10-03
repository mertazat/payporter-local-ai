import requests

from search_documents import search_documents

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"

def ask_document(question):
    # PDF içinden en alakalı parçaları getir
    results = search_documents(question, top_k=3)

    if not results:
        return "Dokümanlarda bu soruyla ilgili bilgi bulunamadı.", []

    # Bulunan parçaları LLM context'i haline getir
    context_parts = []

    for result in results:
        context_parts.append(
            f"""
Kaynak: {result.get('file')}
Sayfa: {result.get('page')}

{result.get('text')}
"""
        )

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
Sen PayPorter şirket içi doküman asistanısın.

Aşağıdaki KAYNAK bölümü şirket dokümanlarından alınmıştır.

Kurallar:
- Soruyu yalnızca verilen KAYNAK bilgilerine göre cevapla.
- Kaynakta olmayan bilgileri uydurma.
- Genel bilgini kullanarak eksik kısımları tamamlama.
- Soruyla doğrudan ilgili olmayan kaynak parçalarını kullanma.
- Birden fazla kaynak varsa soruyla en alakalı olan bilgiyi kullan.
- Soruda istenmeyen ek bilgi verme.
- Cevabı kısa, açık ve Türkçe ver.
- Bilgi kaynakta yoksa:
  "Bu bilgi dokümanlarda bulunamadı." de.

KAYNAK:

{context}

SORU:
{question}

CEVAP:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False,
    "options": {
        "temperature": 0.1,
        "num_predict": 300
    }
},
timeout=300



    )

    response.raise_for_status()

    answer = response.json()["message"]["content"]

    return answer, results


if __name__ == "__main__":
    question = input("PDF hakkında soru: ")

    answer, sources = ask_document(question)

    print("\nCEVAP:\n")
    print(answer)

    print("\nKAYNAKLAR:\n")

    for source in sources:
        print(
            f"- {source.get('file')} "
            f"(Sayfa {source.get('page')}, "
            f"Benzerlik {source.get('score', 0):.4f})"
        )
