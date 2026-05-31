import os
from PyPDF2 import PdfReader

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = ""
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        raise ValueError("Obsługiwane są tylko pliki PDF w tym teście.")

def generate_prompt(text):
    prompt = f"""
Na podstawie poniższego materiału stwórz fiszki edukacyjne w formacie:
Pytanie: ...
Odpowiedź: ...

Treść:
{text}
"""
    return prompt

if __name__ == "__main__":
    # 👉 Podaj ścieżkę do swojego PDF
    file_path = r"C:\Users\PC\Downloads\Testy.pdf"

    text = extract_text_from_file(file_path)
    prompt = generate_prompt(text)

    print("=== PROMPT DO OPENAI ===")
    print(prompt[:2000])  # pokaż pierwsze 2000 znaków, żeby nie zalać konsoli
    print("========================")
