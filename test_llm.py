import ollama

response = ollama.chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": "Merhaba, tek cümleyle kendini tanıt."
        }
    ]
)

print(response["message"]["content"])
