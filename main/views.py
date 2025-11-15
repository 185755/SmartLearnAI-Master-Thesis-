from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import Material
from .models import Flashcard
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from .file_reader import extract_text_from_file
from .ai_flashcard_generator import generate_flashcards_from_text
from django.shortcuts import render, redirect

@login_required
def manage_flashcards(request):
    if request.method == "POST":
        flashcard_id = request.POST.get("delete_id")
        Flashcard.objects.filter(id=flashcard_id, owner=request.user).delete()
        return redirect("manage_flashcards")

    flashcards = Flashcard.objects.filter(owner=request.user).order_by("-next_review")
    return render(request, "manage_flashcards.html", {"flashcards": flashcards})


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

        return redirect('dashboard')  # odświeżenie widoku po dodaniu

    materials = Material.objects.filter(uploaded_by=request.user)
    return render(request, 'dashboard.html', {'materials': materials})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Nieprawidłowe dane logowania'})
    return render(request, 'login.html')
@login_required
@login_required
def generate_flashcards(request):
    if request.method == "POST":
        materials = Material.objects.filter(uploaded_by=request.user)

        generated_count = 0
        max_flashcards = 20  # 🔒 limit fiszek

        for material in materials:
            if generated_count >= max_flashcards:
                break  # przerwij, jeśli osiągnięto limit

            file_path = material.file.path
            text = extract_text_from_file(file_path)
            raw_output = generate_flashcards_from_text(text)

            for block in raw_output.split('\n\n'):
                if generated_count >= max_flashcards:
                    break  # przerwij również wewnętrzną pętlę

                if 'Pytanie:' in block and 'Odpowiedź:' in block:
                    question = block.split('Pytanie:')[1].split('Odpowiedź:')[0].strip()
                    answer = block.split('Odpowiedź:')[1].strip()

                    Flashcard.objects.create(
                        question=question,
                        answer=answer,
                        owner=request.user,
                        level=1,
                        next_review=timezone.now()
                    )
                    generated_count += 1

        messages.success(request, f"Wygenerowano {generated_count} fiszek 🎉 (limit: {max_flashcards})")
    return redirect('dashboard')


@login_required
def learn_flashcard(request):
    now = timezone.now()
    flashcard = Flashcard.objects.filter(owner=request.user, next_review__lte=now).order_by('level').first()

    if not flashcard:
        return render(request, 'no_flashcards.html')

    if request.method == 'POST':
        user_answer = request.POST.get('user_answer', '').strip().lower()
        correct_answer = flashcard.answer.strip().lower()
        correct = user_answer == correct_answer

        # aktualizacja Leitnera
        flashcard.level = min(flashcard.level + 1, 5) if correct else 1
        flashcard.last_reviewed = now
        flashcard.next_review = now + timedelta(days=flashcard.level)
        flashcard.save()

        return render(request, 'learn_flashcard.html', {
            'flashcard': flashcard,
            'answered': True,
            'correct': correct,
            'user_answer': request.POST.get('user_answer'),
        })

    return render(request, 'learn_flashcard.html', {'flashcard': flashcard})


@login_required
def upload_material(request):
    if request.method == 'POST' and request.FILES.get('material'):
        file = request.FILES['material']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        return render(request, 'upload.html', {'filename': filename})
    return render(request, 'upload.html')

@login_required
def create_flashcard(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')
        Flashcard.objects.create(
            question=question,
            answer=answer,
            owner=request.user,
            level=1,
            next_review=timezone.now()
        )
        return redirect('dashboard')
    return render(request, 'create_flashcard.html')

@login_required
def review_flashcard(request, flashcard_id):
    flashcard = Flashcard.objects.get(id=flashcard_id, owner=request.user)

    if request.method == 'POST':
        user_answer = request.POST.get('user_answer')
        correct = user_answer.strip().lower() == flashcard.answer.strip().lower()

        if correct:
            flashcard.level = min(flashcard.level + 1, 5)
        else:
            flashcard.level = 1

        flashcard.last_reviewed = timezone.now()
        flashcard.next_review = timezone.now() + timedelta(days=flashcard.level)
        flashcard.save()

        return render(request, 'review_result.html', {
            'correct': correct,
            'flashcard': flashcard
        })

    return render(request, 'review_flashcard.html', {'flashcard': flashcard})

@login_required
def flashcard_queue(request):
    now = timezone.now()
    flashcards = Flashcard.objects.filter(owner=request.user, next_review__lte=now).order_by('level')
    return render(request, 'flashcard_queue.html', {'flashcards': flashcards})
