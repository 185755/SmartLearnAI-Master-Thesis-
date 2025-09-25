from django.db import models
from django.contrib.auth.models import User

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
    level = models.IntegerField(default=1)  # Leitner level: 1–5
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Fiszka: {self.question[:30]}..."