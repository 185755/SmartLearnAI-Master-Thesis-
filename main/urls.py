#TO JEST PLIK URL W MAIN
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('upload/', views.upload_material, name='upload_material'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('flashcards/create/', views.create_flashcard, name='create_flashcard'),
    path('flashcards/review/<int:flashcard_id>/', views.review_flashcard, name='review_flashcard'),
    path('flashcards/queue/', views.flashcard_queue, name='flashcard_queue'),
    path('learn/', views.learn_flashcard, name='learn_flashcard'),

]

