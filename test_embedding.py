import ollama

text = """
def transfer_money(self, sender_id, receiver_id, amount):
    if amount <= 0:
        raise ValueError("Transfer amount must be greater than zero")
"""

response = ollama.embed(
    model="nomic-embed-text",
    input=text
)

vector = response["embeddings"][0]

print("Embedding oluşturuldu.")
print("Vektör uzunluğu:", len(vector))
print("İlk 10 sayı:")
print(vector[:10])
