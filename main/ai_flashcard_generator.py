from openai import OpenAI

# inicjalizacja klienta
client = OpenAI(api_key="KLUCZ")  # albo os.getenv("OPENAI_API_KEY")

def generate_flashcards_from_text(text):
    prompt = f"""
Na podstawie poniższego materiału stwórz fiszki edukacyjne w formacie:
Pytanie: ...
Odpowiedź: ...

Treść:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # tani i szybki model
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od tworzenia fiszek edukacyjnych."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000  # 🔒 limit odpowiedzi, żeby nie wygenerował za dużo
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # obsługa błędów (np. quota, rate limit)
        return f"⚠️ Błąd podczas generowania fiszek: {e}"
