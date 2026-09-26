from pathlib import Path
import math
import json
import ollama

CODE_FOLDER = Path("company_code")

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".cs", ".java", ".sql", ".html", ".css"
}

CHUNK_SIZE = 10
TOP_K = 5
SIMILARITY_THRESHOLD = 0.30

def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)


def create_embedding(text):
    response = ollama.embed(
        model="nomic-embed-text",
        input=text
    )

    return response["embeddings"][0]


def create_chunks():
    chunks = []

    for file_path in CODE_FOLDER.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.splitlines()

        for start in range(0, len(lines), CHUNK_SIZE):

            chunk_lines = lines[start:start + CHUNK_SIZE]

            if not any(line.strip() for line in chunk_lines):
                continue

            chunks.append({
                "file": str(file_path),
                "start_line": start + 1,
                "end_line": start + len(chunk_lines),
                "content": "\n".join(chunk_lines)
            })

    return chunks


print("Hazır index yükleniyor...")

with open("code_index.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"{len(chunks)} kod parçası index'ten yüklendi.")

while True:

    question = input("\nSorunuzu yazın (çıkmak için 'çık'): ")

    if question.lower() == "çık":
        print("Program kapatıldı.")
        break

    question_embedding = create_embedding(question)

    results = []


    for chunk in chunks:

        score = cosine_similarity(
            question_embedding,
            chunk["embedding"]
        )
        file_name = Path(chunk["file"]).name.lower()
      
        keyword_map = {
            "kimlik doğrulama": "auth",
            "giriş": "auth",
            "token": "auth",
            "ödeme": "payment",
            "transfer": "payment",
            "transaction": "transaction",
            "işlem": "transaction",
            "profil": "user_profile", 
        }

        file_keyword = file_name.replace("_service.py", "")

        if file_keyword in question.lower():
            score += 0.30

        for turkish_word, target_file in keyword_map.items():
            if turkish_word in question.lower() and target_file in file_name:
                score += 0.60


        results.append((score, chunk))
       
       

    results.sort(key=lambda x: x[0], reverse=True)

    top_results = [
        (score, chunk)
        for score, chunk in results
        if score >= SIMILARITY_THRESHOLD
    ][:TOP_K]

    if not top_results:
        print("\nBu soruyla ilgili yeterli kaynak kod bulunamadı.")
        print("Kaynak bulunamadığı için LLM cevabı oluşturulmadı.")
        continue

    context_parts = []
   
    for score, chunk in top_results:

            context_parts.append(
            f"""
    Dosya: {chunk['file']}
    Satırlar: {chunk['start_line']}-{chunk['end_line']}

    {chunk['content']}
     """
        )

    context = "\n".join(context_parts)

    prompt = f"""
    Sen şirketin kaynak kodlarını analiz eden yerel bir yazılım asistanısın.

    Aşağıdaki kaynak kod parçalarını kullanarak kullanıcının sorusunu cevapla.
    Birden fazla dosya arasında ilişki varsa bunları birlikte analiz et.
    Sadece verilen kaynak kodlara dayan, tahmin yapma.
    İlgili dosya adlarını ve mümkünse satır aralıklarını belirt.

    KAYNAK KODLAR:

    {context}

    KULLANICI SORUSU:

    {question}
    """

    print("\nLocal LLM cevap oluşturuyor...\n")

    response = ollama.chat(
            model="qwen3:4b",
            messages=[
                {
                "role": "user",
                    "content": prompt
                }
        ]
    )

    print(response["message"]["content"])

    print("\n--- Kullanılan kaynaklar ---")

    for score, chunk in top_results:
        print(
           f"{chunk['file']} "
            f"(satır {chunk['start_line']}-{chunk['end_line']}) "
            f"benzerlik={score:.4f}"
        
)
