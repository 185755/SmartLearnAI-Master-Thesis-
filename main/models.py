from django.db import models
from django.contrib.auth.models import User


class Material(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.uploaded_by.username})"

class Material(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='materials/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Flashcard(models.Model):
    question = models.TextField()
    answer = models.TextField()

    # stare pola (możesz je później usunąć)
    level = models.IntegerField(default=1)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # NOWE POLE – wymagane przez nowy algorytm
    remaining_reviews = models.IntegerField(default=4)

    def __str__(self):
        return f"Fiszka: {self.question[:30]}..."
