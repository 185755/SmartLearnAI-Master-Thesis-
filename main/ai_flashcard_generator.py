import openai

openai.api_key = "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"

def generate_flashcards_from_text(text):
    prompt = f"""
Na podstawie poniższego materiału stwórz fiszki edukacyjne w formacie:
Pytanie: ...
Odpowiedź: ...

Treść:
{text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jesteś ekspertem od tworzenia fiszek edukacyjnych."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']
