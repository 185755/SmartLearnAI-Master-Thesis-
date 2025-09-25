from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

class Material(models.Model):
    MATERIAL_TYPES = (
        ('pdf', 'PDF'),
        ('audio', 'Audio'),
        ('text', 'Text'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=MATERIAL_TYPES)
    source_file = models.FileField(upload_to='materials/')
    processed_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Flashcard(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    leitner_level = models.IntegerField(default=1)
    last_reviewed = models.DateTimeField(blank=True, null=True)

class Quiz(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField()
    correct_option = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

class StudyHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    reviewed_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
