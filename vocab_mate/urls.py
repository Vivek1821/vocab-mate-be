from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('profile/', views.user_profile, name='profile'),
    path('stats/', views.user_stats, name='stats'),
    
    # Words
    path('words/', views.WordListCreateView.as_view(), name='word-list'),
    path('words/<int:pk>/', views.WordDetailView.as_view(), name='word-detail'),
    
    # User Progress
    path('progress/', views.UserProgressListCreateView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', views.UserProgressDetailView.as_view(), name='progress-detail'),

    # Daily Sentences
    path('daily-sentences/', views.GenerateDailySentencesView.as_view(), name='daily-sentences'),
]
