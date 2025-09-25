from django.contrib import admin
from .models import User, Material, Flashcard, Quiz, StudyHistory

admin.site.register(User)
admin.site.register(Material)
admin.site.register(Flashcard)
admin.site.register(Quiz)
admin.site.register(StudyHistory)

