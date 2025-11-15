from django.contrib import admin
from .models import Flashcard

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'owner', 'level', 'next_review')
    search_fields = ('question', 'answer')
    list_filter = ('level', 'next_review')

# Register your models here.
