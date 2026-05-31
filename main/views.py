from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Material, Flashcard
from .file_reader import extract_text_from_file
import os
import re


# 🔥 Funkcja pomocnicza – tworzy klienta OpenAI tylko wtedy, gdy jest potrzebny
def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key="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")


# 🔥 Ocena odpowiedzi użytkownika
def evaluate_answer(question, correct_answer, user_answer):
    import numpy as np
    client = get_openai_client()

    emb_correct = client.embeddings.create(
        model="text-embedding-3-small",
        input=correct_answer
    ).data[0].embedding

    emb_user = client.embeddings.create(
        model="text-embedding-3-small",
        input=user_answer
    ).data[0].embedding

    similarity = np.dot(emb_correct, emb_user) / (
        np.linalg.norm(emb_correct) * np.linalg.norm(emb_user)
    )

    if similarity > 0.85:
        return "poprawna"
    elif similarity > 0.65:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Oceń odpowiedź użytkownika względem poprawnej odpowiedzi. Zwróć tylko 'poprawna', 'częściowo poprawna' lub 'błędna'."},
                {"role": "user", "content": f"Pytanie: {question}\nPoprawna odpowiedź: {correct_answer}\nOdpowiedź użytkownika: {user_answer}"}
            ]
        )
        return response.choices[0].message.content.strip()
    else:
        return "błędna"


# 🔥 Reset fiszek
@login_required
def reset_flashcards(request):
    if request.method == "POST":
        Flashcard.objects.filter(owner=request.user).update(remaining_reviews=4)
        messages.success(request, "Wszystkie fiszki zostały zresetowane do 4 powtórek 🎉")
        return redirect('dashboard')


# 🔥 Zarządzanie fiszkami
@login_required
def manage_flashcards(request):
    if request.method == "POST":
        flashcard_id = request.POST.get("delete_id")
        Flashcard.objects.filter(id=flashcard_id, owner=request.user).delete()
        return redirect("manage_flashcards")

    flashcards = Flashcard.objects.filter(owner=request.user).order_by("-remaining_reviews")
    return render(request, "manage_flashcards.html", {"flashcards": flashcards})


# 🔥 Dashboard użytkownika
@login_required
def user_dashboard(request):
    if request.method == 'POST' and request.FILES.get('material'):
        file = request.FILES['material']
        title = request.POST.get('title', file.name)
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)

        Material.objects.create(
            title=title,
            file=filename,
            uploaded_by=request.user
        )

        return redirect('dashboard')

    materials = Material.objects.filter(uploaded_by=request.user)
    return render(request, 'dashboard.html', {'materials': materials})


# 🔥 Usuwanie materiału
@login_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id, uploaded_by=request.user)
    material.file.delete(save=False)
    material.delete()
    return redirect('dashboard')


# 🔥 Logowanie
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'error': 'Nieprawidłowe dane logowania'})
    return render(request, 'login.html')


# 🔥 Generowanie fiszek z materiałów
def generate_flashcards_from_materials(materials, extra_instruction=""):
    from openai import OpenAI
    client = get_openai_client()

    combined_texts = ""

    for material in materials:
        file_path = material.file.path
        text = extract_text_from_file(file_path)

        if text.strip():
            combined_texts += f"\n=== Materiał: {material.title} ===\n{text}\n"
        else:
            combined_texts += f"\n=== Materiał: {material.title} ===\n[Brak tekstu w pliku]\n"

    prompt = f"""
Na podstawie poniższego materiału stwórz dokładnie 10 fiszek edukacyjnych.
Każda fiszka musi być w formacie:

Pytanie: ...
Odpowiedź: ...

Nie używaj żadnych dodatkowych komentarzy ani opisów.
{extra_instruction}

Materiały:
{combined_texts}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Jesteś ekspertem od tworzenia fiszek edukacyjnych."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=6000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Błąd podczas generowania fiszek: {e}"


# 🔥 Endpoint generowania fiszek
@login_required
def generate_flashcards(request):
    if request.method == "POST":
        materials = Material.objects.filter(uploaded_by=request.user)

        if not materials.exists():
            messages.error(request, "Brak materiałów w bazie danych.")
            return redirect('dashboard')

        raw_output = generate_flashcards_from_materials(materials)

        generated_count = 0
        max_flashcards = 120

        blocks = re.findall(r"Pytanie:(.*?)Odpowiedź:(.*?)(?=Pytanie:|$)", raw_output, re.S)

        for q, a in blocks:
            if generated_count >= max_flashcards:
                break

            Flashcard.objects.create(
                question=q.strip(),
                answer=a.strip(),
                owner=request.user,
                remaining_reviews=4,
                last_reviewed=timezone.now()
            )
            generated_count += 1

        messages.success(request, f"Wygenerowano {generated_count} fiszek 🎉 (limit: {max_flashcards})")

    return redirect('dashboard')


# 🔥 Nauka fiszek
@login_required
def learn_flashcard(request):
    if request.method == 'POST':
        flashcard_id = request.POST.get('flashcard_id')
        flashcard = get_object_or_404(Flashcard, id=flashcard_id, owner=request.user)

        user_answer = request.POST.get('user_answer', '').strip()
        verdict = evaluate_answer(flashcard.question, flashcard.answer, user_answer)

        if verdict == "poprawna":
            flashcard.remaining_reviews = max(0, flashcard.remaining_reviews - 1)
        elif verdict == "błędna":
            flashcard.remaining_reviews += 1

        flashcard.last_reviewed = timezone.now()
        flashcard.save()

        return render(request, 'learn_flashcard.html', {
            'flashcard': flashcard,
            'answered': True,
            'verdict': verdict,
            'user_answer': user_answer,
        })

    flashcard = Flashcard.objects.filter(
        owner=request.user,
        remaining_reviews__gt=0
    ).order_by('?').first()

    if not flashcard:
        return render(request, 'no_flashcards.html')

    return render(request, 'learn_flashcard.html', {'flashcard': flashcard})


# 🔥 Upload materiału
@login_required
def upload_material(request):
    if request.method == 'POST' and request.FILES.get('material'):
        file = request.FILES['material']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        return render(request, 'upload.html', {'filename': filename})
    return render(request, 'upload.html')


# 🔥 Ręczne tworzenie fiszki
@login_required
def create_flashcard(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        Flashcard.objects.create(
            question=question,
            answer=answer,
            owner=request.user,
            remaining_reviews=4,
            last_reviewed=timezone.now()
        )
        return redirect('dashboard')
    return render(request, 'create_flashcard.html')


# 🔥 Recenzja fiszki
@login_required
def review_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id, owner=request.user)

    if request.method == 'POST':
        user_answer = request.POST.get('user_answer', '').strip()
        verdict = evaluate_answer(flashcard.question, flashcard.answer, user_answer)

        if verdict == "poprawna":
            flashcard.remaining_reviews = max(0, flashcard.remaining_reviews - 1)
        elif verdict == "błędna":
            flashcard.remaining_reviews += 1

        flashcard.last_reviewed = timezone.now()
        flashcard.save()

        return render(request, 'review_result.html', {
            'correct': verdict == "poprawna",
            'flashcard': flashcard
        })

    return render(request, 'review_flashcard.html', {'flashcard': flashcard})


# 🔥 Kolejka fiszek
@login_required
def flashcard_queue(request):
    flashcards = Flashcard.objects.filter(
        owner=request.user,
        remaining_reviews__gt=0
    ).order_by('id')
    return render(request, 'flashcard_queue.html', {'flashcards': flashcards})
