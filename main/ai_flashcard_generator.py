from openai import OpenAI

# inicjalizacja klienta
client = OpenAI(api_key="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")  # albo os.getenv("OPENAI_API_KEY")

def generate_flashcards_from_text(text):
    prompt = f"""
Na podstawie poniższego materiału stwórz fiszki edukacyjne w formacie:
Pytanie: ...
Odpowiedź: ...

Treść:
{text}
"""

    # 👇 Debug: pokaż prompt w konsoli
    print("=== PROMPT DO OPENAI ===")
    print(prompt)
    print("========================")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # tani i szybki model
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od tworzenia fiszek edukacyjnych."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500  # ✅ poprawny parametr
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # obsługa błędów (np. quota, rate limit)
        return f"⚠️ Błąd podczas generowania fiszek: {e}"

